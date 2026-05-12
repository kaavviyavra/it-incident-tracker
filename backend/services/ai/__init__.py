import logging
import re
from .llm_runners import run_llm_with_prompt_cache
from .parser import parse_toon
from .validators import validate_question

# Import Prompts & Versions
from .prompts.classification import build_classification_prompt, PROMPT_VERSION as CLASSIFY_VER
from .prompts.assignment import build_assignment_prompt, PROMPT_VERSION as ASSIGN_VER
from .prompts.summary import build_summary_prompt, PROMPT_VERSION as SUMMARY_VER
from .prompts.recommendations import build_recommendation_prompt, PROMPT_VERSION as RECS_VER
from .prompts.ask import build_ask_prompt, PROMPT_VERSION as ASK_VER

logger = logging.getLogger(__name__)

# =====================================================
# 1. Classification Layer
# =====================================================
def classify_incident_basic(description, categories, subcategories_map, category_map):
    rules = []
    for cat_label in categories:
        subs = subcategories_map.get(category_map.get(cat_label), [])
        if subs:
            rules.append(f"{cat_label}:{'|'.join(subs)}")

    final_prompt = build_classification_prompt(description, categories, rules)

    result = run_llm_with_prompt_cache(final_prompt, response_format="toon", version=CLASSIFY_VER)

    # Safety Checks
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


# =====================================================
# 2. Assignment Orchestration
# =====================================================
def resolve_assignment(llm_output, category, groups, users):
    assignment_group = llm_output.get("assignment_group")
    if assignment_group not in groups:
        assignment_group = groups[0] if groups else "Unknown"

    assigned_to = llm_output.get("assigned_to")
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

def assign_incident_with_context(description, category, groups, users):
    final_prompt = build_assignment_prompt(description, category, groups, users)
    llm_output = run_llm_with_prompt_cache(final_prompt, response_format="toon", version=ASSIGN_VER)
   
    resolved = resolve_assignment(
        llm_output=llm_output,
        category=category,
        groups=groups,
        users=users
    )
    logger.info(f"[Assignment] Orchestration finalized with prompts {ASSIGN_VER}")
    return resolved


# =====================================================
# 3. Analytics Summaries & Advice
# =====================================================
def generate_ai_summary(insights):
    final_prompt = build_summary_prompt(insights)
    return run_llm_with_prompt_cache(final_prompt, response_format="json", version=SUMMARY_VER)

def generate_recommendations(insights):
    final_prompt = build_recommendation_prompt(insights)
    return run_llm_with_prompt_cache(final_prompt, response_format="json", version=RECS_VER)


# =====================================================
# 4. Direct Dataset Q&A with INJECTION BLOCKER
# =====================================================
def ask_data(question, insights):
    # SECURITY GUARDRAIL
    safe_question = validate_question(question)
    
    final_prompt = build_ask_prompt(safe_question, insights)
    return run_llm_with_prompt_cache(final_prompt, response_format="json", version=ASK_VER)
