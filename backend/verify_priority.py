
def calculate_priority(impact, urgency):
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

test_cases = [
    ("1 - High", "1 - High", "1 - Critical"),
    ("1 - High", "2 - Medium", "2 - High"),
    ("1 - High", "3 - Low", "3 - Moderate"),
    ("2 - Medium", "1 - High", "2 - High"),
    ("2 - Medium", "2 - Medium", "3 - Moderate"),
    ("2 - Medium", "3 - Low", "4 - Low"),
    ("3 - Low", "1 - High", "3 - Moderate"),
    ("3 - Low", "2 - Medium", "4 - Low"),
    ("3 - Low", "3 - Low", "5 - Planning"),
    (None, "1 - High", "3 - Moderate"), # Default case
    ("Invalid", "Invalid", "3 - Moderate"), # Default case
]

for impact, urgency, expected in test_cases:
    result = calculate_priority(impact, urgency)
    print(f"Impact: {impact}, Urgency: {urgency} -> Priority: {result} (Expected: {expected})")
    assert result == expected

print("All tests passed!")
