import requests
import os
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

def test_connection():
    snow_url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    
    auth = HTTPBasicAuth(snow_user, snow_pwd)
    api_url = f"{snow_url}/api/now/table/incident?sysparm_limit=1"
    
    print(f"Testing connection to {api_url} with Netskope SSL verification...")
    try:
        response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify="netskope_root.pem")
        print(f"Success! Status code: {response.status_code}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
