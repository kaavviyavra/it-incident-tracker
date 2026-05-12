import json
from services.ai.truncation import truncate_insights

PROMPT_VERSION = "v1.3"

def build_ask_prompt(question, insights):
    safe_insights = truncate_insights(insights)
    return f"""
You are an AIOps assistant.

Answer the user's question using ITSM insights.

DATA:
{json.dumps(safe_insights, indent=2)}

QUESTION:
{question}

INSTRUCTIONS:
- Answer in simple English
- Be concise
- Base answer only on given data

OUTPUT FORMAT (STRICT JSON):
{{
  "answer": "..."
}}
"""
