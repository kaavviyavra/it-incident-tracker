import requests
from .client import get_snow_auth

# Global cache to avoid excessive API calls
CACHE = {
    "categories": None,
    "subcategories": None, # dict grouped by category value
    "category_map": None,
    "last_fetch": 0
}

def fetch_all_choices():
    """
    Fetches categories and subcategories from ServiceNow sys_choice table.
    Groups subcategories by their dependent_value (which is the category's value).
    """
    url, auth = get_snow_auth()
    
    # 1. Fetch Categories
    cat_query = "name=incident^element=category^inactive=false"
    cat_api = f"{url}/api/now/table/sys_choice?sysparm_query={cat_query}&sysparm_fields=label,value"
    
    # 2. Fetch Subcategories
    sub_query = "name=incident^element=subcategory^inactive=false"
    sub_api = f"{url}/api/now/table/sys_choice?sysparm_query={sub_query}&sysparm_fields=label,value,dependent_value"
    
    headers = {"Accept": "application/json"}
    
    try:
        cat_res = requests.get(cat_api, auth=auth, headers=headers, verify="netskope_root.pem")
        cat_res.raise_for_status()
        categories = cat_res.json().get("result", [])
        
        sub_res = requests.get(sub_api, auth=auth, headers=headers, verify="netskope_root.pem")
        sub_res.raise_for_status()
        subcategories_raw = sub_res.json().get("result", [])
        
        # Group subcategories by dependent_value
        sub_mapped = {}
        for sub in subcategories_raw:
            dep = sub.get("dependent_value", "generic")
            if not dep: dep = "generic"
            if dep not in sub_mapped:
                sub_mapped[dep] = []
            sub_mapped[dep].append(sub.get("label"))
            
        CACHE["categories"] = [c.get("label") for c in categories]
        # We also need to map labels to values for category so we can look up subcategories
        CACHE["category_map"] = {c.get("label"): c.get("value") for c in categories}
        CACHE["subcategories"] = sub_mapped
        
        return CACHE["categories"], CACHE["subcategories"], CACHE["category_map"]
        
    except Exception as e:
        print(f"Error fetching ServiceNow choices: {e}")
        return [], {}, {}

def get_choices_for_llm():
    """Returns cached choices or fetches them if missing."""
    if CACHE["categories"] is None:
        return fetch_all_choices()
    return CACHE["categories"], CACHE["subcategories"], CACHE["category_map"]
