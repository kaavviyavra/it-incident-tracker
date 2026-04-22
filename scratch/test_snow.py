import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

def test_snow():
    url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    user = os.getenv("SNOW_USERNAME")
    pwd = os.getenv("SNOW_PASSWORD")
    
    print(f"Testing connection to {url} with user {user}")
    
    auth = HTTPBasicAuth(user, pwd)
    api_url = f"{url}/api/now/table/incident?sysparm_limit=1"
    
    try:
        # Try with verify=False first to see if it's an SSL issue
        print("Attempting with verify=False...")
        response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=False)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success with verify=False!")
        else:
            print(f"Failed with verify=False: {response.text}")
            
        # Try with the certificate
        cert_path = 'backend/certs/netskope_root.pem'
        if os.path.exists(cert_path):
            print(f"Attempting with cert: {cert_path}...")
            try:
                response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify=cert_path)
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    print("Success with cert!")
                else:
                    print(f"Failed with cert: {response.text}")
            except Exception as e:
                print(f"Error with cert: {e}")
        else:
            print(f"Cert file not found: {cert_path}")
            
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    test_snow()
