import app
import requests
import json

def test_push():
    # Grab first incident
    incidents = app.fetch_servicenow_incidents(limit=1)
    if not incidents:
        print("No incidents to test.")
        return
    
    sys_id = incidents[0]['sys_id']
    inc_num = incidents[0]['number']
    print(f"Testing on {inc_num} ({sys_id})")

    # Attempt a mock update using the EXACT structure we use in /classify
    update_data = {
        "work_notes": "Test work notes",
        "category": "Software",
        "subcategory": "Email",
        "impact": "2",
        "urgency": "2"
    }

    url, auth = app.get_snow_auth()
    api_url = f"{url}/api/now/table/incident/{sys_id}?sysparm_input_display_value=true"
    
    print(f"Sending payload: {json.dumps(update_data)}")
    
    response = requests.patch(api_url, auth=auth, json=update_data, headers={"Accept": "application/json"}, verify=False)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_push()
