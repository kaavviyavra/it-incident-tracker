PROMPT_VERSION = "v2.4"

BASE_TOON_HEADER = "STRICT true"
CLASSIFY_BASE_HEADER = """
TASK CLASSIFY_INCIDENT
DOMAIN SERVICENOW
"""

def build_classifier_static_prompt():
    return f"""{BASE_TOON_HEADER}
{CLASSIFY_BASE_HEADER}
OUTPUT category subcategory impact urgency
FORMAT TOON
"""

def build_classification_prompt(description, categories, rules):
    static_prompt = build_classifier_static_prompt()
    return f"""{static_prompt}
CATEGORIES {'|'.join(categories)}
SUBCATEGORY_RULES {';'.join(rules)}

IMPACT_RULES 1:Enterprise/Multiple_Depts | 2:Single_Dept/Group | 3:Single_User
URGENCY_RULES 1:Critical_Stopped | 2:Degraded_Response_Today | 3:Low_Impact_Workaround

REQUIRE category subcategory impact urgency
DESC {description}
"""
