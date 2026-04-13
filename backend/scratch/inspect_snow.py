import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

def inspect_incident():
    snow_url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    
    auth = HTTPBasicAuth(snow_user, snow_pwd)
    
    # Fetch one incident without display values to see raw field names and values
    api_url = f"{snow_url}/api/now/table/incident?sysparm_limit=1"
    
    print(f"Fetching from: {api_url}")
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
    
    if response.status_code == 200:
        try:
            data = response.json()
        except Exception as e:
            print(f"Failed to parse JSON even though status was 200. Response text:\n{response.text[:500]}")
            return
        if data.get("result"):
            inc = data["result"][0]
            print("Incident Sample Data (Raw):")
            print(f"All keys: {sorted(inc.keys())}")
            for key in ["number", "category", "subcategory", "u_subcategory", "sub_category"]:
                if key in inc:
                    print(f"{key}: {inc[key]}")
                else:
                    print(f"{key}: [NOT FOUND]")
            
            # Also check with display values
            api_url_dv = f"{snow_url}/api/now/table/incident?sysparm_limit=1&sysparm_display_value=true"
            print(f"\nFetching from (display value): {api_url_dv}")
            response_dv = requests.get(api_url_dv, auth=auth, headers={"Accept": "application/json"}, verify=False)
            if response_dv.status_code == 200:
                inc_dv = response_dv.json()["result"][0]
                print("Incident Sample Data (Display Value):")
                for key in ["number", "category", "subcategory", "u_subcategory", "sub_category"]:
                    if key in inc_dv:
                        print(f"{key}: {inc_dv[key]}")
        else:
            print("No incidents found.")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    inspect_incident()
