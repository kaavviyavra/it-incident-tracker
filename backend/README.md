# Incident Automation Backend

This project provides a Flask-based API service that simulates ITSM incident lifecycle by fetching, classifying, assigning, and auto-remediating incidents. It integrates Google Gemini to analyze incident descriptions and automatically map them to appropriate assignments.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory and add your Google Gemini API key and ServiceNow credentials:
   ```env
   GEMINI_API_KEY=your_genai_api_key_here
   SNOW_INSTANCE_URL=https://devXXX.service-now.com
   SNOW_USERNAME=admin
   SNOW_PASSWORD=your_password
   ```

3. **Run the App:**
   ```bash
   python app.py
   ```

4. **Run the Test Suite:**
   ```bash
   pytest test_app.py -v
   ```

## Endpoints

### 1. `GET /incidents`
Returns a list of all incidents currently stored in memory.

### 2. `POST /incidents/sync`
Fetches active incidents from a LIVE ServiceNow instance via its Table API. It reads the description of each new incident, auto-categorizes them using Gemini (with a local fallback in case of rate limits), and saves them to the active in-memory store.

### 3. `POST /incidents/<incident_id>/classify`
Triggers Gemini to classify an individual incident (Network, Application, or Infrastructure) and assign it to a team based on its description.

### 4. `POST /incidents/<incident_id>/heal`
Simulates an auto-remediation task that sets the incident status to "Resolved". updates its state.

### 5. `GET /incidents/<incident_id>/history`
Tracks the lifecycle history and actions taken on a specific incident.
