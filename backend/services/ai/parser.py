import json
import re

def _clean_and_parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

def parse_toon(text: str) -> dict:
    return {
        k.lower().strip().rstrip(':'): v.strip()
        for k, v in
        (line.strip().split(" ", 1) for line in text.splitlines() if " " in line.strip())
    }
