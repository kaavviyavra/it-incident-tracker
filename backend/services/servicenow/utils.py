def calculate_priority(impact, urgency):
    """
    Deterministically calculates priority based on Impact and Urgency.
    Default to '3 - Moderate' if inputs are missing or invalid.
    """
    # Mapping based on user requirement
    matrix = {
        ("1 - High", "1 - High"): "1 - Critical",
        ("1 - High", "2 - Medium"): "2 - High",
        ("1 - High", "3 - Low"): "3 - Moderate",
        ("2 - Medium", "1 - High"): "2 - High",
        ("2 - Medium", "2 - Medium"): "3 - Moderate",
        ("2 - Medium", "3 - Low"): "4 - Low",
        ("3 - Low", "1 - High"): "3 - Moderate",
        ("3 - Low", "2 - Medium"): "4 - Low",
        ("3 - Low", "3 - Low"): "5 - Planning",
    }
    return matrix.get((impact, urgency), "3 - Moderate")

def map_snow_to_standard(val):
    """Maps SNOW numeric values to the standard 'N - Label' format."""
    mapping = {
        "1": "1 - High",
        "2": "2 - Medium",
        "3": "3 - Low"
    }
    return mapping.get(str(val), "3 - Low")
