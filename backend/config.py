import os
from dotenv import load_dotenv

load_dotenv()

ENABLE_BATCH_LLM = os.getenv("ENABLE_BATCH_LLM", "true").lower() == "true"

SPIKE_WINDOW_DAYS = int(os.getenv("SPIKE_WINDOW_DAYS", "7"))

