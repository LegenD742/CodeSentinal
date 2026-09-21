from app.agents.base_agent import BaseAgent
from app.agents.prompts.quality_agent_prompt import QUALITY_AGENT_SYSTEM_PROMPT
from app.core.constants import Category


class QualityAgent(BaseAgent):
    name = "quality"
    category = Category.QUALITY
    system_prompt = QUALITY_AGENT_SYSTEM_PROMPT

    def build_user_prompt(self, context: dict) -> str:
        return f"""File: {context['file_path']}

Enclosing function/class context:
```
{context.get('enclosing_context', 'N/A')}
```

Diff hunk:
```diff
{context['diff_hunk']}
```

Related repository context (use this to judge consistency with existing conventions):
{context.get('repo_context', 'None retrieved.')}

Analyze only the changed lines above for maintainability/quality issues."""
