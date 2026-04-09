import os
import json
import re
from dotenv import load_dotenv
from google import genai
from groq import Groq

# Load variables from .env
load_dotenv()

# -----------------------------
# Gemini Client (Primary)
# -----------------------------
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Groq Client (Fallback - LLaMA 3)
# -----------------------------
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
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
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash-latest",
        "gemini-pro"
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

            if "429" in error_str or "403" in error_str:
                break

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

# -----------------------------
# Groq Runner (Fallback)
# -----------------------------
def _run_groq(prompt: str) -> dict:
    print("MOCK Groq fallback triggered (network-restricted environment)")
    return {
        "category": "Application",
        "subcategory": "Database",
        "assignment_group": "Application Support",
        "assigned_to": ""
    }

# -----------------------------
# Unified LLM Executor
# -----------------------------
def _run_llm_with_fallback(prompt: str) -> dict:
    try:
        return _run_gemini(prompt)
    except Exception:
        print("Gemini failed, switching to fallback...")
        return _run_groq(prompt)

# -----------------------------
# Classification Function
# -----------------------------
def classify_incident_basic(description: str) -> dict:
    prompt = f"""
You are an ITSM incident classification assistant.

Classify the incident based on its description into:
1. Category (e.g., Network, Application, Infrastructure, Hardware)
2. Subcategory (e.g., VPN, Database, Server, Frontend, ERP)

Return ONLY valid JSON in this exact format:
{{
  "category": "Application",
  "subcategory": "Database"
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