import os
import json
import re
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# Create Gemini client using API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def _run_gemini(prompt: str) -> dict:
    models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash-latest", "gemini-pro"]
    response = None
    last_error = None
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            print(f"SUCCESS: Connected using model '{model_name}'!")
            break
        except Exception as e:
            error_str = str(e)
            print(f"Model '{model_name}' failed: {error_str}")
            last_error = e
            # Stop trying if we hit a Rate Limit (429) or API Key invalid (403), 
            # since testing other models won't bypass a key-level block.
            if "429" in error_str or "403" in error_str:
                break
            continue
            
    if not response:
        raise ValueError(f"All Gemini models failed. Last error: {str(last_error)}")

    text = response.text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON")


def classify_incident_basic(description: str) -> dict:
    """Uses Gemini LLM to classify category and subcategory."""
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
    return _run_gemini(prompt)


def assign_incident_with_context(description: str, category: str, groups: list, users: list) -> dict:
    """Uses Gemini to assign the ticket to an actual SNOW user & group."""
    prompt = f"""
You are an ITSM incident routing assistant.

Given the Incident details, pick the MOST APPROPRIATE Assignment Group and Assigned To user from the provided lists ONLY. 
Do NOT make up names that are not in the lists. You don't have to assign a user if uncertain, but do assign a group.

Incident Category: {category}
Incident Description: {description}

Valid Assignment Groups to choose from:
{groups}

Valid Users to choose from (along with their ID/Roles):
{users}

Return ONLY valid JSON in this exact format:
{{
  "assignment_group": "[Chosen Group Name from the list]",
  "assigned_to": "[Chosen User Name from the list or empty string]"
}}
"""
    return _run_gemini(prompt)