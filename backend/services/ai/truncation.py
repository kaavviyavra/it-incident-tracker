import json

MAX_ITEMS_PER_SECTION = 20
MAX_TRENDS = 50
MAX_PROBLEM_CANDIDATES = 10


def truncate_insights(insights: dict) -> dict:
    """
    Reduces payload size before sending to LLM.
    Prevents token explosion on very large datasets.
    """

    if not insights:
        return {}

    truncated = dict(insights)

    # Limit trends
    if "trends" in truncated:
        truncated["trends"] = truncated["trends"][:MAX_TRENDS]

    # Limit spikes
    if "spikes" in truncated:
        truncated["spikes"] = truncated["spikes"][:MAX_ITEMS_PER_SECTION]

    # Limit problem candidates
    if "problem_candidates" in truncated:
        truncated["problem_candidates"] = truncated["problem_candidates"][:MAX_PROBLEM_CANDIDATES]

    # Limit distributions
    for key in [
        "categories",
        "subcategories",
        "assignment_groups",
        "priority_distribution",
        "status_distribution"
    ]:
        if key in truncated and isinstance(truncated[key], dict):
            items = list(truncated[key].items())[:MAX_ITEMS_PER_SECTION]
            truncated[key] = dict(items)

    return truncated