import logging
from .gemini_client import gemini_client
from .parser import _clean_and_parse_json, parse_toon
from .cache import get_cached_response, commit_cache
from services.config import ENABLE_LLM

logger = logging.getLogger(__name__)

def _run_llm(prompt: str, response_format="json") -> dict:
    models = [
        "models/gemini-3.1-flash-lite-preview",
        "models/gemini-3.1-pro",
        "models/gemini-3-flash-preview",
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash"
    ]

    last_error = None
    if not gemini_client:
         raise RuntimeError("Gemini client failed initialization. Check environment variables.")

    for model in models:
        try:
            response = gemini_client.models.generate_content(
                model=model,
                contents=prompt
            )

            usage = response.usage_metadata
            if usage:
                logger.info(
                    f"[Gemini Tokens] Model: {model} | "
                    f"Prompt: {usage.prompt_token_count} | "
                    f"Response: {usage.candidates_token_count} | "
                    f"Total: {usage.total_token_count}"
                )

            logger.info(f"Gemini model sequence success. Loaded: {model}")

            if response_format == "toon":
                return parse_toon(response.text)

            return _clean_and_parse_json(response.text)

        except Exception as e:
            last_error = e
            logger.error(f"Gemini fallback. '{model}' failed: {e}")

    raise RuntimeError(f"All configured Gemini models failed. Last error: {last_error}")

def run_llm_with_prompt_cache(
    prompt: str,
    response_format="json",
    version: str = "unknown"
) -> dict:
    """
    Centralized AI execution gateway.

    Handles:
    - cache lookup
    - LLM enable/disable
    - model execution
    - response persistence
    """

    # -----------------------------------
    # LLM Global Toggle
    # -----------------------------------
    if not ENABLE_LLM:

        logger.warning(
            "[AI DISABLED] ENABLE_LLM=false. "
            "Returning deterministic fallback response."
        )

        return {
            "disabled": True,
            "message": "LLM features disabled by configuration."
        }

    # -----------------------------------
    # Cache Layer
    # -----------------------------------
    cached_val, key = get_cached_response(
        prompt,
        version=version
    )

    if cached_val:
        return cached_val

    # -----------------------------------
    # Execute Model
    # -----------------------------------
    result = _run_llm(
        prompt,
        response_format
    )

    # -----------------------------------
    # Persist Cache
    # -----------------------------------
    commit_cache(key, result)

    return result
