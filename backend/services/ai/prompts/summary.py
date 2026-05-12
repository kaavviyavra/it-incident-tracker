import json
from services.ai.truncation import truncate_insights

PROMPT_VERSION = "v1.2"

def build_summary_prompt(insights):
    safe_insights = truncate_insights(insights)
    return f"""
You are an AIOps assistant.

Analyze ITSM incident data and provide a simple explanation.

DATA:
{json.dumps(safe_insights, indent=2)}

INSTRUCTIONS:
- Explain why incidents are happening
- Describe key trends
- Highlight risks
- Suggest actions

OUTPUT FORMAT (STRICT JSON):
{{
  "summary": "..."
}}
"""
