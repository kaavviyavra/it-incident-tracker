import os
import logging
from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)

try:
    gemini_client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )
    logger.info("Gemini Client successfully initialized.")
except Exception as e:
    logger.error(f"CRITICAL Failure initializing Gemini client: {e}")
    gemini_client = None
