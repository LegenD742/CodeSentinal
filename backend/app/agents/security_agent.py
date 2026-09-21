import json

from app.agents.base_agent import BaseAgent
from app.agents.prompts.security_agent_prompt import SECURITY_AGENT_SYSTEM_PROMPT
from app.core.config import get_settings
from app.core.constants import Category

settings = get_settings()


class SecurityAgent(BaseAgent):
    name = "security"
    category = Category.SECURITY
    system_prompt = SECURITY_AGENT_SYSTEM_PROMPT
    # Security findings benefit most from a bigger local model if you have one
    # pulled (e.g. `ollama pull qwen2.5-coder:7b`) — falls back to llm_model if unset.
    model_override = settings.llm_model_heavy or None

    def build_user_prompt(self, context: dict) -> str:
        static_findings = context.get("static_findings", [])
        static_block = json.dumps(static_findings, indent=2) if static_findings else "None."

        return f"""File: {context['file_path']}

Enclosing function/class context:
```
{context.get('enclosing_context', 'N/A')}
```

Diff hunk:
```diff
{context['diff_hunk']}
```

Static analyzer findings for this file (Semgrep/Bandit/ESLint) — cross-reference these:
{static_block}

Related repository context:
{context.get('repo_context', 'None retrieved.')}

Analyze only the changed lines above for security vulnerabilities."""
