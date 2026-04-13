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
# Gemini Runner (Primary)
# -----------------------------
def _run_gemini(prompt: str) -> dict:
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
            print(f"Gemini success with model: {model_name}")
            return _clean_and_parse_json(response.text)

        except Exception as e:
            last_error = e
            error_str = str(e)
            print(f"Gemini model '{model_name}' failed: {error_str}")

            if "403" in error_str:
                break  # Break only on 403 (Invalid API Key)

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")



# -----------------------------
# Unified LLM Executor
# -----------------------------
def _run_llm_with_fallback(prompt: str) -> dict:
    """Runs the LLM. Fallback logic removed as Groq is no longer used."""
    return _run_gemini(prompt)


# -----------------------------
# -----------------------------
# Classification Function
# -----------------------------
def classify_incident_basic(description: str, categories: list, subcategories_map: dict, category_map: dict) -> dict:
    # Prepare the subcategory guidance string
    subcat_guidance = ""
    for cat_label in categories:
        cat_value = category_map.get(cat_label)
        subs = subcategories_map.get(cat_value, [])
        if subs:
            subcat_guidance += f"- If Category is {cat_label}: Pick from {subs}\n"

    prompt = f"""
You are a ServiceNow incident classification assistant.

Classify the incident based on its description. You MUST pick the Category strictly from this list:
{categories}

For the Subcategory, you MUST pick a value that is a standard "child" of the category in ServiceNow. 
Based on these categories, pick from the following choices only:
{subcat_guidance}

Choose the most appropriate one. If none match perfectly, choose the closest generic one from the lists above.

Return ONLY valid JSON in this exact format:
{{
  "category": "Chosen Category",
  "subcategory": "Chosen Subcategory"
}}

Incident description:
\"\"\"{description}\"\"\"
"""
    return _run_llm_with_fallback(prompt)

# -----------------------------
# Assignment Function
# -----------------------------
def assign_incident_with_context(description: str, category: str, groups: list, users: list) -> dict:
    prompt = f"""
You are an ITSM incident routing assistant.

Pick the MOST APPROPRIATE Assignment Group and Assigned To user ONLY from the provided lists. 
You MUST assign a user from the list. Pick the closest match. 
Do not leave assignment_group or assigned_to empty or unknown.

Incident Category: {category}
Incident Description: {description}

Valid Assignment Groups:
{groups}

Valid Users (with IDs/Roles):
{users}

Return ONLY valid JSON in this exact format:
{{
  "assignment_group": "Group Name",
  "assigned_to": "User Name"
}}
"""
    return _run_llm_with_fallback(prompt)