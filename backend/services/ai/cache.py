import hashlib
import time
import logging

logger = logging.getLogger(__name__)

CACHE_TTL = 86400
CACHE_MAX_SIZE = 5000
_PROMPT_CACHE = {}

def normalize_prompt(prompt: str) -> str:
    lines = [line.strip() for line in prompt.splitlines() if line.strip()]
    return "\n".join(lines)

def get_cached_response(prompt: str, version: str = "unknown"):
    normalized = normalize_prompt(prompt)
    key = hashlib.sha256(normalized.encode()).hexdigest()
    current_time = time.time()

    if key in _PROMPT_CACHE:
        entry = _PROMPT_CACHE[key]
        if current_time - entry["timestamp"] > CACHE_TTL:
            logger.warning(f"[LLM Cache EXPIRED] Hash: {key[:8]} | Version: {version}")
            del _PROMPT_CACHE[key]
        else:
            logger.info(f"[LLM Cache HIT] Hash: {key[:8]} | Version: {version}")
            return entry["response"], key

    logger.info(f"[LLM Cache MISS] Version: {version}. Submitting...")
    return None, key

def commit_cache(key, result):
    _PROMPT_CACHE[key] = {
        "response": result,
        "timestamp": time.time()
    }

    while len(_PROMPT_CACHE) > CACHE_MAX_SIZE:
        oldest_key = next(iter(_PROMPT_CACHE))
        del _PROMPT_CACHE[oldest_key]
        logger.warning("[LLM Cache EVICTED] FIFO constraints applied.")
