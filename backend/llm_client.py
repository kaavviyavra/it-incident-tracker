import os
import json
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# Create Gemini client using API key
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def classify_with_gemini(description: str) -> dict:
    """
    Uses Gemini LLM to classify an incident and assign a support group.
    Returns structured JSON.
    """

    prompt = f"""
You are an ITSM incident classification assistant.

Classify the incident into one category:
- Network
- Application
- Infrastructure

Assign support groups:
- Network → Network Team
- Application → App Support Team
- Infrastructure → Infra Team

Return ONLY valid JSON in this format:
{{
  "category": "Application",
  "assignment_group": "App Support Team"
}}

Incident description:
\"\"\"{description}\"\"\"
"""

    # Try multiple models based on region/key availability
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
            break # Success!
        except Exception as e:
            last_error = e
            continue
            
    if not response:
        raise ValueError(f"All Gemini models failed. Last error: {str(last_error)}")


    import re
    text = response.text.strip()
    
    # Strip markdown block formatting if Gemini wraps the JSON response
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON")