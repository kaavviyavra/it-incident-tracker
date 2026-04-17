import os
import json
import re
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# -----------------------------
# Gemini Client (Primary)
# -----------------------------
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Helper: Clean & Parse JSON
# -----------------------------
def _clean_and_parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

# -----------------------------
# TOON Utilities
# -----------------------------
def parse_toon(text: str) -> dict:
    return {
        k.lower(): v.strip()
        for k, v in
        (line.split(" ", 1) for line in text.splitlines() if " " in line)
    }

# -----------------------------
# Gemini Runner (Primary)
# -----------------------------
def _run_gemini(prompt: str, response_format: str = "json") -> dict:
    models_to_try = [
        "models/gemini-3.1-flash-lite-preview",
        "models/gemini-3-flash-preview",
        "models/gemini-2.5-flash-lite",
        "models/gemini-2.0-flash-lite",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash"
    ]

    last_error = None

    for model_name in models_to_try:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if hasattr(response, "usage_metadata") and response.usage_metadata:
                usage = response.usage_metadata
                print(
                    f"[Gemini Tokens] Model: {model_name} | "
                    f"Prompt tokens: {usage.prompt_token_count} | "
                    f"Response tokens: {usage.candidates_token_count} | "
                    f"Total tokens: {usage.total_token_count}"
                )
            else:
                print(f"[Gemini Tokens] Model: {model_name} | Usage metadata not available")

            print(f"Gemini success with model: {model_name}")

            if response_format == "toon":
                return parse_toon(response.text)
            else:
                return _clean_and_parse_json(response.text)

        except Exception as e:
            last_error = e
            error_str = str(e)
            print(f"Gemini model '{model_name}' failed: {error_str}")

            if "403" in error_str:
                break

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

# -----------------------------
# Unified LLM Executor
# -----------------------------
def _run_llm_with_fallback(prompt: str, response_format: str = "json") -> dict:
    """Runs the LLM. Fallback logic removed as Groq is no longer used."""
    return _run_gemini(prompt)

# -----------------------------
# -----------------------------
# Classification Function
# -----------------------------
def classify_incident_basic(description: str, categories: list,
                            subcategories_map: dict, category_map: dict) -> dict:
    # Build compact subcategory rules
    subcat_rules = []
    for cat_label in categories:
        cat_value = category_map.get(cat_label)
        subs = subcategories_map.get(cat_value, [])
        if subs:
            subcat_rules.append(f"{cat_label}:{'|'.join(subs)}")

    toon_prompt = f"""TASK CLASSIFY_INCIDENT
DOMAIN SERVICENOW

DESC {description}

CATEGORIES {'|'.join(categories)}
SUBCATEGORY_RULES {';'.join(subcat_rules)}

OUTPUT category subcategory
FORMAT JSON
STRICT true
"""

    return _run_llm_with_fallback(toon_prompt)

# -----------------------------
# Assignment Function
# -----------------------------
def assign_incident_with_context(description: str, category: str,
                                 groups: list, users: list) -> dict:
    toon_prompt = f"""TASK ASSIGN_INCIDENT
DOMAIN ITSM

CATEGORY {category}
DESC {description}

GROUPS {'|'.join(groups)}
USERS {'|'.join(users)}

REQUIRE assignment_group assigned_to
FORMAT JSON
STRICT true
"""

    return _run_llm_with_fallback(toon_prompt)