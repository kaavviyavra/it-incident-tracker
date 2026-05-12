import os


ENABLE_LLM = (
    os.getenv("ENABLE_LLM", "true").lower() == "true"
)

ENABLE_LOCAL_MODEL = (
    os.getenv("ENABLE_LOCAL_MODEL", "true").lower() == "true"
)