PROMPT_VERSION = "v1.8"

BASE_TOON_HEADER = "STRICT true"
ASSIGN_BASE_HEADER = """
TASK ASSIGN_INCIDENT
DOMAIN ITSM
"""

def build_assignment_static_prompt():
    return f"""{BASE_TOON_HEADER}
{ASSIGN_BASE_HEADER}
OUTPUT assignment_group assigned_to
FORMAT TOON
"""

def build_assignment_prompt(description, category, groups, users):
    static_prompt = build_assignment_static_prompt()
    return f"""{static_prompt}
CATEGORY {category}
GROUPS {'|'.join(groups)}
USERS {'|'.join(users)}
DESC {description}
"""
