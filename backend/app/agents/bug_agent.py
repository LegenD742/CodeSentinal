from app.agents.base_agent import BaseAgent
from app.agents.prompts.bug_agent_prompt import BUG_AGENT_SYSTEM_PROMPT
from app.core.constants import Category


class BugAgent(BaseAgent):
    name = "bug"
    category = Category.BUG
    system_prompt = BUG_AGENT_SYSTEM_PROMPT

    def build_user_prompt(self, context: dict) -> str:
        return f"""File: {context['file_path']}

Enclosing function/class context:
```
{context.get('enclosing_context', 'N/A')}
```

Diff hunk (only + and - lines are changes; context lines are unchanged):
```diff
{context['diff_hunk']}
```

Related repository context (for understanding intent, not for flagging issues in):
{context.get('repo_context', 'None retrieved.')}

Analyze only the changed lines above for logic/correctness bugs."""
