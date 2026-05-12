import os
import requests
from requests.auth import HTTPBasicAuth
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

def get_snow_auth():
    snow_url = os.getenv("SNOW_INSTANCE_URL", "").rstrip("/")
    snow_user = os.getenv("SNOW_USERNAME")
    snow_pwd = os.getenv("SNOW_PASSWORD")
    if not all([snow_url, snow_user, snow_pwd]):
        raise ValueError("ServiceNow credentials are not configured in the .env file.")
    return snow_url, HTTPBasicAuth(snow_user, snow_pwd)

def fetch_incidents(limit=10):
    url, auth = get_snow_auth()
    # Simplified query to fetch active incidents opened by current user
    api_url = f"{url}/api/now/table/incident?sysparm_query=active=true^opened_by=javascript:gs.getUserID()^ORDERBYDESCsys_created_on"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify="certs/netskope_root.pem")
    response.raise_for_status()
    return response.json().get("result", [])

def fetch_groups(limit=15):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/sys_user_group?sysparm_query=active=true&sysparm_limit={limit}"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify="certs/netskope_root.pem")
    response.raise_for_status()
    return response.json().get("result", [])

def fetch_users(limit=50):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/sys_user?sysparm_query=active=true^emailISNOTEMPTY&sysparm_limit={limit}"
    response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify="certs/netskope_root.pem")
    response.raise_for_status()
    return response.json().get("result", [])

def get_user_vip(user_sys_id):
    """Checks if a specific user sys_id has the VIP flag set to true."""
    if not user_sys_id:
        return False
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/sys_user/{user_sys_id}?sysparm_fields=vip"
    try:
        response = requests.get(api_url, auth=auth, headers={"Accept": "application/json"}, verify="certs/netskope_root.pem")
        response.raise_for_status()
        result = response.json().get("result", {})
        if isinstance(result, dict):
            vip_val = result.get("vip", "false")
            return str(vip_val).lower() == "true"
        return False
    except Exception as e:
        logger.warning(f"Failed to fetch VIP status for user {user_sys_id}: {e}")
        return False


def update_incident(sys_id, update_data):
    url, auth = get_snow_auth()
    api_url = f"{url}/api/now/table/incident/{sys_id}?sysparm_input_display_value=true"
    try:
        logger.info(f"[SNOW Sync] Preparing PATCH incident {sys_id}")
        response = requests.patch(api_url, auth=auth, json=update_data, headers={"Accept": "application/json"}, verify="certs/netskope_root.pem")
        if response.status_code != 200:
             logger.warning(f"[SNOW Warning] PATCH status {response.status_code}: {response.text}")
        response.raise_for_status()
        logger.info(f"[SNOW Success] Updated Incident {sys_id} payload keys: {list(update_data.keys())}")
        return response.json().get("result")
    except Exception as e:
        status_code = getattr(response, "status_code", "N/A") if 'response' in locals() else "N/A"
        logger.error(f"[SNOW CRITICAL] Synchronize Failed for {sys_id} | HTTP Status: {status_code} | Error: {e}")
        raise e
