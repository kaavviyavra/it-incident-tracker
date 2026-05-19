<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# IT Incident Tracker & Analytics Engine

An intelligent, state-of-the-art incident management dashboard and analytics platform. This application integrates local AI classifications with real-time operational insights, allowing IT administrators and site reliability engineers to monitor incident trends, perform interactive Q&A analysis on ticket dumps, auto-generate standard operating procedures (SOPs), and export forecasting models.

---

## 🚀 Key Features

*   **Real-time Incident Monitoring & Actions:** Fetch, classify, assign, and resolve incidents with seamless visual badges and state transitions.
*   **AIOps Dataset Intelligence:**
    *   **Excel/CSV Batch Uploads:** Process massive dumps of IT tickets directly from your local filesystem.
    *   **Interactive Column Mapping:** Drag, drop, or select mappings from your sheet to align fields (Description, Category, Subcategory, Assignment Group, Priority, Status, and Resolution Notes) with our analytics engine.
    *   **Status vs Count Visualizations:** Beautiful, responsive horizontal bar charts representing incident statuses (New/Open, In-Progress/Assigned, Resolved/Closed, On-Hold/Pending) styled with tailored operational colors.
    *   **Hourly Resolution Analysis:** Breakdown resolution times relative to ticket priority tiers.
    *   **Daily Incident Surges & Trends:** Interactive sparklines identifying rolling 7-day and 30-day volume anomalies.
*   **Interactive AI Analyst:** Run interactive zero-shot LLM Q&A sessions on arbitrary ticket files to extract insights instantly (e.g., *“Which group handles the most critical incidents?”*).
*   **Documentation Automation:**
    *   **Export SOP Documents:** Auto-generate Standard Operating Procedures mapped to your category volumes.
    *   **Export KEDB Patterns:** Identify Known Error Database (KEDB) resolution signatures automatically.
    *   **Export Forecasting Reports:** Download strategic AI/AIOps predictions on recurring infrastructure threats.

---

## 📂 Project Architecture

```
it-incident-tracker/
├── backend/                  # Flask-based API Gateway
│   ├── main.py               # Application Entrypoint (port 5000)
│   ├── routes/               # Blueprint Controllers (incidents, batch, insights, ai, sop)
│   ├── services/             # Core Business Logic & Insights Engine
│   │   ├── insights_engine/  # Schema resolution, aggregations, trend analysis, anomaly detection
│   │   └── local_ai/         # Zero-shot classification engines
│   └── store/                # Volatile & persistent storage caches
└── frontend/                 # Vite + React Client Dashboard
    ├── src/                  # Components, Hooks, Data Assets & Types
    │   ├── App.tsx           # Main Dashboard Shell (port 3000)
    │   └── types.ts          # TypeScript type definitions
    ├── vite.config.ts        # Proxy redirection config mapping `/api/*` to `localhost:5000`
    └── package.json          # Dependency definition and build scripts
```

---

## 🛠️ Run Locally

### Prerequisites
*   [Node.js](https://nodejs.org/) (v18+)
*   [Python](https://www.python.org/) (v3.10+)

### 1. Backend Setup
1. Navigate to the `backend` directory.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file inside the `backend` folder and add:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   # Optional ServiceNow Credentials for Live Sync
   SNOW_INSTANCE_URL=https://devXXX.service-now.com
   SNOW_USERNAME=admin
   SNOW_PASSWORD=your_password
   ```
4. Run the Flask server:
   ```bash
   python main.py
   ```
   *The backend gateway runs on `http://127.0.0.1:5000`.*

### 2. Frontend Setup
1. Navigate to the `frontend` directory.
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend dashboard will be available at `http://localhost:3000`.*

---

## 🛡️ Recent System Enhancements

- **Flexible Status Column Mapping**: Users can now select and map their custom "Status" columns when uploading incident dumps, with intelligent auto-detection rules serving as a fallback.
- **Status vs Count Dashboard Graphs**: Interactive visual distributions display current status percentages styled in modern, dynamic color tokens.
- **Simplified Layout Controls**: Removed extraneous settings, search bars, notifications, and integration controls from the main header and sidebars to focus fully on incident management, batch intelligence, and document exporting.
- **Help Centre**: Integrated a Help Centre navigation panel for quickly viewing user manual documentation directly inside the dashboard.
