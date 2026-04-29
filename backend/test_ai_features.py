import sys
import os

# Ensure the backend directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_engine import run_llm_with_prompt_cache, parse_toon

def test_prompt_caching():
    print("\n" + "="*30)
    print("TESTING PROMPT CACHING")
    print("="*30)
    
    test_prompt = "TASK: TEST_CACHE\nDOMAIN: UI\nDESC: Testing the in-memory prompt cache mechanism."
    
    print("\n[Step 1] First execution (Expect Cache MISS):")
    # This will trigger the actual LLM call
    run_llm_with_prompt_cache(test_prompt, response_format="toon")
    
    print("\n[Step 2] Second execution with identical prompt (Expect Cache HIT):")
    # This should return immediately from the local _PROMPT_CACHE
    run_llm_with_prompt_cache(test_prompt, response_format="toon")

def test_toon_parsing():
    print("\n" + "="*30)
    print("TESTING TOON PARSING")
    print("="*30)
    
    # Simulating a raw string in TOON format as returned by the LLM
    raw_toon_data = """
CATEGORY Network
SUBCATEGORY connectivity
IMPACT 1:Enterprise
URGENCY 2:High
"""
    
    print(f"\nRaw LLM Output (TOON):\n{raw_toon_data.strip()}")
    
    parsed_result = parse_toon(raw_toon_data)
    
    print("\nParsed Result (Python Dictionary):")
    import json
    print(json.dumps(parsed_result, indent=4))
    
    # Verification logic
    expected_keys = ["category", "subcategory", "impact", "urgency"]
    if all(k in parsed_result for k in expected_keys):
        print("\n[SUCCESS] All keys correctly extracted from TOON format.")
    else:
        print("\n[FAILURE] Missing keys in parsed dictionary.")

if __name__ == "__main__":
    print("Starting AI Feature Validation...")
    try:
        test_prompt_caching()
        test_toon_parsing()
        print("\n" + "="*30)
        print("ALL TESTS COMPLETED")
        print("="*30)
    except Exception as e:
        print(f"\n[!] Test Execution Error: {e}")
