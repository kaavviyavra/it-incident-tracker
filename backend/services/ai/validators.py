import logging

logger = logging.getLogger(__name__)

INJECTION_KEYWORDS = [
    "ignore previous",
    "ignore system instructions",
    "forget what I told you",
    "you are now",
    "system prompt bypass",
    "new persona",
    "disregard"
]

def validate_question(question: str) -> str:
    """
    Inspects incoming user questions for common prompt injection strings.
    Raises ValueError if dangerous keywords are identified.
    """
    if not question:
        return ""
        
    q_lower = str(question).lower()
    
    for trigger in INJECTION_KEYWORDS:
        if trigger in q_lower:
            logger.warning(f"BLOCKED Prompt Injection attempt detected: '{trigger}' found.")
            raise ValueError("Security validation failed: Input contains unauthorized command patterns.")
            
    return question
