"""
The Verification/Critic Agent. Unlike the specialist agents, it doesn't
produce new findings — it audits a batch of findings against the same
diff evidence they were generated from, and returns a verdict per
finding. This is the primary hallucination/false-positive guard.

Runs on a local model via Ollama (see app/core/llm_client.py). Because
this is the safety-net stage, model_override defaults to
LLM_MODEL_HEAVY if you've set one — a small 3B model is usable here but
a 7-8B local model will reject far fewer valid findings and catch more
hallucinations.
"""
from app.agents.prompts.critic_agent_prompt import CRITIC_AGENT_SYSTEM_PROMPT
from app.core.config import get_settings
from app.core.llm_client import chat_completion, safe_json_loads
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CriticAgent:
    name = "critic"
    model_override = settings.llm_model_heavy or None

    async def verify(self, findings: list[dict], diff_hunk: str) -> list[dict]:
        if not findings:
            return []

        findings_payload = [
            {
                "index": i,
                "title": f["title"],
                "severity": f["severity"],
                "confidence": f["confidence"],
                "explanation": f["explanation"],
                "evidence": f["evidence"],
                "category": f.get("category"),
            }
            for i, f in enumerate(findings)
        ]

        user_prompt = f"""Diff hunk these findings were generated from:
```diff
{diff_hunk}
```

Findings to verify (JSON):
{findings_payload}

Respond with ONLY a JSON object of this exact shape:
{{"verdicts": [{{"index": <int>, "verdict": "confirmed"|"downgraded"|"rejected", \
"revised_severity": <string or null>, "revised_confidence": <int>, "reasoning": <short string>}}]}}
One verdict object per finding above, same order."""

        try:
            raw_text = await chat_completion(
                system_prompt=CRITIC_AGENT_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                model=self.model_override,
            )
        except Exception:
            logger.exception("Critic agent call failed; treating all findings as unverified")
            return [
                {**f, "critic_verdict": "rejected", "critic_reasoning": "Critic agent unavailable"}
                for f in findings
            ]

        parsed = safe_json_loads(raw_text, fallback={"verdicts": []})
        verdicts = parsed.get("verdicts", []) if isinstance(parsed, dict) else []
        verdict_by_index = {v["index"]: v for v in verdicts if "index" in v}

        verified: list[dict] = []
        for i, f in enumerate(findings):
            v = verdict_by_index.get(i)
            if v is None:
                f["critic_verdict"] = "rejected"
                f["critic_reasoning"] = "No verdict returned by critic"
            else:
                f["critic_verdict"] = v.get("verdict", "rejected")
                f["critic_reasoning"] = v.get("reasoning", "")
                if v.get("revised_severity"):
                    f["severity"] = v["revised_severity"]
                if v.get("revised_confidence") is not None:
                    f["confidence"] = v["revised_confidence"]
            verified.append(f)
        return verified
