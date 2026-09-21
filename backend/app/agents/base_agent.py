"""
Shared scaffolding for every reasoning agent: calls the local LLM (via
Ollama, see app/core/llm_client.py) with a system prompt + structured
context, and parses the response into a list of Finding-shaped dicts.

NOTE on local small models (llama3.2:3b etc.): asking a 3B model for a
bare top-level JSON array is noticeably less reliable than asking it for
a JSON *object* with a named key, even with Ollama's format="json" mode
(which guarantees valid JSON syntax, not a specific shape). So unlike a
hosted-model version of this file, we ask for {"findings": [...]} and
unwrap it — this alone fixes most parse failures with small models.
"""
from abc import ABC, abstractmethod

from app.core.llm_client import chat_completion, safe_json_loads
from app.core.logging import get_logger

logger = get_logger(__name__)

RESPONSE_SCHEMA_INSTRUCTIONS = """
Respond with ONLY a JSON object of this exact shape, nothing else — no markdown fences, no prose:
{"findings": [ { ... }, { ... } ]}

Each object inside "findings" MUST have exactly these keys:
- "title": short string
- "severity": one of "critical" | "high" | "medium" | "low" | "info"
- "confidence": integer 0-100, your own confidence this is a real, actionable issue
- "start_line": integer, line number in the NEW file version
- "end_line": integer
- "explanation": 1-3 sentences explaining the issue and why it matters
- "evidence": the exact code/diff snippet that supports this finding
- "suggested_fix": short actionable suggestion (or null)

If you find nothing in this category, respond with {"findings": []}
Never invent line numbers that are not present in the provided diff.
"""


class BaseAgent(ABC):
    name: str
    category: str
    system_prompt: str
    # Override per-agent to route to a bigger local model (e.g. for security),
    # leave None to use the default LLM_MODEL from settings.
    model_override: str | None = None

    @abstractmethod
    def build_user_prompt(self, context: dict) -> str:
        raise NotImplementedError

    async def analyze(self, context: dict) -> list[dict]:
        user_prompt = self.build_user_prompt(context) + "\n\n" + RESPONSE_SCHEMA_INSTRUCTIONS
        try:
            raw_text = await chat_completion(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                model=self.model_override,
            )
        except Exception:
            logger.exception("%s agent call failed", self.name)
            return []

        parsed = safe_json_loads(raw_text, fallback={"findings": []})
        findings = parsed.get("findings", []) if isinstance(parsed, dict) else []

        for f in findings:
            f["source_agent"] = self.name
            f["category"] = self.category
            f["file_path"] = context.get("file_path", "")
            f["tool_origin"] = "llm"
        return findings
