import os
import json
import re
import hashlib
from dotenv import load_dotenv
from google import genai

_PROMPT_CACHE = {}

# Load variables from .env
load_dotenv()

# -----------------------------
# Gemini Client
# -----------------------------
gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Prompt Utilities
# -----------------------------
def normalize_prompt(prompt: str) -> str:
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    return "\n".join(lines)


def run_llm_with_prompt_cache(prompt: str, response_format="json") -> dict:
    normalized = normalize_prompt(prompt)
    key = hashlib.sha256(normalized.encode()).hexdigest()

    if key in _PROMPT_CACHE:
        print("[LLM Cache HIT]")
        return _PROMPT_CACHE[key]

    print("[LLM Cache MISS]")
    result = _run_llm(prompt, response_format)
    _PROMPT_CACHE[key] = result
    return result

# -----------------------------
# Parsing Helpers
# -----------------------------
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

# -----------------------------
# Gemini Runner
# -----------------------------
def _run_llm(prompt: str, response_format="json") -> dict:
    models = [
        "models/gemini-3.1-flash-lite-preview",
        "models/gemini-3.1-pro",
        "models/gemini-3-flash-preview",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash"
    ]

    last_error = None

    for model in models:
        try:
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )

            usage = response.usage_metadata
            if usage:
                print(
                    f"[Gemini Tokens] Model: {model} | "
                    f"Prompt: {usage.prompt_token_count} | "
                    f"Response: {usage.candidates_token_count} | "
                    f"Total: {usage.total_token_count}"
                )

            print(f"Gemini success with model: {model}")

            if response_format == "toon":
                return parse_toon(response.text)

            return _clean_and_parse_json(response.text)

        except Exception as e:
            last_error = e
            print(f"Gemini model '{model}' failed: {e}")

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

# -----------------------------
# TOON Prompt Blocks
# -----------------------------
BASE_TOON_HEADER = "STRICT true"

CLASSIFY_BASE_HEADER = """
TASK CLASSIFY_INCIDENT
DOMAIN SERVICENOW
"""

ASSIGN_BASE_HEADER = """
TASK ASSIGN_INCIDENT
DOMAIN ITSM
"""

# -----------------------------
# Classification (LLM = Intent)
# -----------------------------
def build_classifier_static_prompt():
    return f"""{BASE_TOON_HEADER}
{CLASSIFY_BASE_HEADER}
OUTPUT category subcategory impact urgency
FORMAT TOON
"""


def classify_incident_basic(description, categories, subcategories_map, category_map):
    static_prompt = build_classifier_static_prompt()

    rules = []
    for cat_label in categories:
        subs = subcategories_map.get(category_map.get(cat_label), [])
        if subs:
            rules.append(f"{cat_label}:{'|'.join(subs)}")

    toon_prompt = f"""{static_prompt}
CATEGORIES {'|'.join(categories)}
SUBCATEGORY_RULES {';'.join(rules)}

IMPACT_RULES 1:Enterprise/Multiple_Depts | 2:Single_Dept/Group | 3:Single_User
URGENCY_RULES 1:Critical_Stopped | 2:Degraded_Response_Today | 3:Low_Impact_Workaround

REQUIRE category subcategory impact urgency
DESC {description}
"""

    result = run_llm_with_prompt_cache(toon_prompt, response_format="toon")

    #RESOLVER: classification safety
    if result.get("category") not in categories:
        result["category"] = categories[0]

    valid_subs = subcategories_map.get(
        category_map.get(result["category"]), []
    )
    if result.get("subcategory") not in valid_subs and valid_subs:
        result["subcategory"] = valid_subs[0]
        
    impact_str = str(result.get("impact", "3")).strip()
    result["impact"] = impact_str[0] if impact_str and impact_str[0] in ["1", "2", "3"] else "3"

    urgency_str = str(result.get("urgency", "3")).strip()
    result["urgency"] = urgency_str[0] if urgency_str and urgency_str[0] in ["1", "2", "3"] else "3"

    return result

# -----------------------------
# Assignment Prompt
# -----------------------------
def build_assignment_static_prompt():
    return f"""{BASE_TOON_HEADER}
{ASSIGN_BASE_HEADER}
OUTPUT assignment_group assigned_to
FORMAT TOON
"""


# -----------------------------
# Resolver Logic (Authoritative)
# -----------------------------
def resolve_assignment(llm_output, category, groups, users):
    """
    LLM provides weak signal.
    Resolver enforces ServiceNow-safe values from available sources.
    """
    assignment_group = llm_output.get("assignment_group")

    if assignment_group not in groups:
        assignment_group = groups[0] if groups else "Unknown"

    assigned_to = llm_output.get("assigned_to")
    
    # We attempt robust user matching since SNOW format might contain titles
    user_names = [u.split(' (')[0].strip() for u in users]
    
    is_valid_user = False
    if assigned_to:
        for valid_name in user_names:
            if valid_name.lower() in assigned_to.lower():
                assigned_to = valid_name
                is_valid_user = True
                break
                
    if not is_valid_user:
        assigned_to = user_names[0] if user_names else "Unknown"

    return {
        "assignment_group": assignment_group,
        "assigned_to": assigned_to
    }

# -----------------------------
# Assignment Entry Point
# -----------------------------
def assign_incident_with_context(description, category, groups, users):
    static_prompt = build_assignment_static_prompt()

    toon_prompt = f"""{static_prompt}
CATEGORY {category}
GROUPS {'|'.join(groups)}
USERS {'|'.join(users)}
DESC {description}
"""

    llm_output = run_llm_with_prompt_cache(toon_prompt, response_format="toon")
   
    resolved = resolve_assignment(
        llm_output=llm_output,
        category=category,
        groups=groups,
        users=users
    )

    print("DEBUG: Resolved Assignment →", resolved)

    return resolved
