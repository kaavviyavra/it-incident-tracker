import requests
import time

print("Fetching incidents...")
r = requests.get('http://127.0.0.1:5000/incidents')
incs = r.json()
print(f"Found {len(incs)} incidents")

if len(incs) > 0:
    inc_id = incs[0]['id']
    print(f"Classifying {inc_id}...")
    res = requests.post(f'http://127.0.0.1:5000/incidents/{inc_id}/classify')
    print(f"Status: {res.status_code}")
    print(res.text[:500])
