import json
from services.ai.truncation import truncate_insights

PROMPT_VERSION = "v1.4"

def build_recommendation_prompt(insights):
    safe_insights = truncate_insights(insights)
    return f"""
You are an AIOps system.

Based on ITSM incident insights, generate actionable recommendations.

DATA:
{json.dumps(safe_insights, indent=2)}

INSTRUCTIONS:
- Identify major problems
- Suggest clear actions
- Keep it practical and short

OUTPUT FORMAT (STRICT JSON):
[
  {{
    "problem": "...",
    "recommendation": "..."
  }}
]
"""
