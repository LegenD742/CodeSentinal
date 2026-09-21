from app.agents.base_agent import BaseAgent
from app.agents.prompts.performance_agent_prompt import PERFORMANCE_AGENT_SYSTEM_PROMPT
from app.core.constants import Category


class PerformanceAgent(BaseAgent):
    name = "performance"
    category = Category.PERFORMANCE
    system_prompt = PERFORMANCE_AGENT_SYSTEM_PROMPT

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

Related repository context (use this to judge call frequency, e.g. is this in a hot loop or a \
one-time setup path):
{context.get('repo_context', 'None retrieved.')}

Analyze only the changed lines above for performance issues."""
