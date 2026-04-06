import pytest
from app import app
from store import incidents

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_store():
    # Clear and reset incidents store before each test
    incidents.clear()
    incidents["INC001"] = {
        "id": "INC001",
        "description": "Application is down for all users",
        "status": "New",
        "category": None,
        "assignment_group": None,
        "history": []
    }
    yield

def test_get_incidents(client):
    response = client.get("/incidents")
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["id"] == "INC001"

def test_classify_incident_success(client, mocker):
    mock_classify = mocker.patch('app.classify_with_gemini', return_value={
        "category": "Application",
        "assignment_group": "App Support Team"
    })
    
    response = client.post("/incidents/INC001/classify")
    assert response.status_code == 200
    assert response.json["category"] == "Application"
    assert response.json["assignment_group"] == "App Support Team"
    assert response.json["status"] == "Assigned"
    assert "Gemini classified as Application" in response.json["history"][0]

def test_classify_incident_not_found(client):
    response = client.post("/incidents/INVALID/classify")
    assert response.status_code == 404

def test_auto_heal(client):
    response = client.post("/incidents/INC001/heal")
    assert response.status_code == 200
    assert response.json["status"] == "Resolved"
    assert "Auto-healing simulated: Issue resolved" in response.json["history"][-1]

def test_incident_history(client):
    response = client.get("/incidents/INC001/history")
    assert response.status_code == 200
    assert "history" in response.json

def test_sync_incidents(client, mocker):
    # Mock the ServiceNow API request
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "result": [
            {"number": "INC999", "short_description": "Network test"}
        ]
    }
    mocker.patch("requests.get", return_value=mock_response)
    
    # Mock env vars so credential checks pass in tests
    mocker.patch("os.getenv", side_effect=lambda k: "mock_val" if k in ["SNOW_INSTANCE_URL", "SNOW_USERNAME", "SNOW_PASSWORD"] else None)

    # Mock time.sleep so our tests run instantly instead of waiting 2 seconds!
    mocker.patch("time.sleep", return_value=None)
    
    # Mock the LLM classification to avoid hitting real API
    mocker.patch('app.classify_with_gemini', return_value={
        "category": "Network",
        "assignment_group": "Network Team"
    })

    response = client.post("/incidents/sync")
    assert response.status_code == 200
    assert "INC999" in incidents
    assert incidents["INC999"]["category"] == "Network"
    assert incidents["INC999"]["assignment_group"] == "Network Team"
