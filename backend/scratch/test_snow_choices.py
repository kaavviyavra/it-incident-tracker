import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

def fetch_snow_choices(table_name, field_name):
    snow_url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    
    auth = HTTPBasicAuth(snow_user, snow_pwd)
    
    # Query sys_choice table
    # sysparm_query=name=<table_name>^element=<field_name>^inactive=false
    query = f"name={table_name}^element={field_name}^inactive=false"
    api_url = f"{snow_url}/api/now/table/sys_choice?sysparm_query={query}&sysparm_fields=label,value,dependent_value"
    
    print(f"Fetching choices from: {api_url}")
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    
    if response.status_code == 200:
        results = response.json().get("result", [])
        print(f"Found {len(results)} choices.")
        for choice in results[:10]:
            print(choice)
        return results
    else:
        print(f"Error {response.status_code}: {response.text}")
        return []

if __name__ == "__main__":
    print("--- Categories ---")
    fetch_snow_choices("incident", "category")
    print("\n--- Subcategories ---")
    fetch_snow_choices("incident", "subcategory")
