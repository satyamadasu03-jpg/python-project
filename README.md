# CareLens — Healthcare Analytics & Patient Risk Indicator System

**Project number:** 23  
**Difficulty:** Advanced  
**Stack:** Python, Flask, MySQL, Pandas, NumPy, Matplotlib, HTML/CSS/JavaScript

## 1. Project overview
CareLens is an educational healthcare operations analytics project using synthetic patient, visit, and measurement records. It exposes REST APIs, validates input, summarizes department and monthly visits, plots three charts, and applies transparent illustrative rules to flag measurement records for further review.

> **Important limitation:** This is not a medical device. Rules and thresholds are invented for demonstration, are not clinically validated, and must not be used for diagnosis, treatment, triage, or real patient-care decisions. All seed data is fictional.

## 2. Features
- REST endpoints to list and add synthetic patients, visits, and measurements.
- MySQL relational database with primary keys and foreign keys.
- Input validation and parameterized SQL.
- Pandas data cleaning/grouping; NumPy descriptive statistics.
- Matplotlib charts: visits by department, monthly visit trend, educational indicator distribution.
- Dashboard with KPI cards, a review-flag table, and API links.
- A database health endpoint and JSON analytics endpoint.

## 3. Folder structure
```text
healthcare_analytics_patient_risk/
├── app.py
├── analytics.py
├── schema.sql
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── charts/                 # generated at runtime
```

## 4. Setup (Windows)
1. Install Python 3.10+ and MySQL Server. Start the MySQL service.
2. Extract this ZIP and open the project folder in VS Code or a terminal.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```
4. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
5. Import database and fictional seed data. In MySQL Workbench, open `schema.sql` and execute it. Or run:
   ```bash
   mysql -u root -p < schema.sql
   ```
6. Copy `.env.example` to `.env` and set your own MySQL username/password. Never share the `.env` file.
7. Start the application:
   ```bash
   python app.py
   ```
8. Open `http://127.0.0.1:5000` in your browser.

## 5. API guide
All request bodies are JSON. Use Postman, Thunder Client, or curl.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check API and database connection |
| GET | `/api/patients` | List synthetic patient records |
| POST | `/api/patients` | Add a synthetic patient |
| GET | `/api/departments` | List departments |
| POST | `/api/visits` | Add a visit |
| POST | `/api/measurements` | Add a measurement after illustrative range validation |
| GET | `/api/analytics` | Return KPIs, group summaries, and flags as JSON |
| GET | `/api/charts/visits_by_department.png` | Department chart |
| GET | `/api/charts/monthly_visits.png` | Monthly visits chart |
| GET | `/api/charts/indicator_distribution.png` | Flag distribution chart |

### Example requests

Add patient:
```json
{
  "patient_code": "SYN-2001",
  "age_band": "30-44",
  "optional_demographic": "Sample G"
}
```

Add visit:
```json
{
  "patient_id": 1,
  "department_id": 2,
  "visit_date": "2026-10-27"
}
```

Add measurement:
```json
{
  "patient_id": 1,
  "measurement_date": "2026-10-27",
  "measure_type": "heart_rate",
  "value": 80
}
```

## 6. Database design
- `patients`: fictional patient code and age band.
- `departments`: department lookup table.
- `visits`: each visit references one patient and one department.
- `measurements`: dated observations with type, value, and unit.
- `risk_indicators`: schema reserved for persisting rule evaluations; current analytics computes flags dynamically from measurements.

Relationships:
```text
patients 1 ─── * visits * ─── 1 departments
patients 1 ─── * measurements
patients 1 ─── * risk_indicators
measurements 1 ─── * risk_indicators
```

## 7. Analysis formulas and assumptions
- Visit count by department = number of visit records grouped by department.
- Monthly visit trend = number of visit records grouped by calendar month.
- Mean measurement value = arithmetic mean across stored measurement values. Since different measurement types have different units, this overall mean is only a software demonstration statistic and should not be interpreted clinically.
- Median measurement value = median across stored values; same unit-mixing limitation applies.
- Educational indicator = a measurement that falls outside the illustrative range documented in `analytics.py`. It is a review flag, not a diagnosis.
- Validation ranges in `app.py` only prevent obviously out-of-range demonstration values; they are not medical guidance.

## 8. Test checklist
1. Visit `/api/health` with MySQL running — expect status `ok`.
2. Visit `/api/patients` — expect fictional records from `schema.sql`.
3. POST a patient with a valid age band — expect HTTP 201.
4. POST a patient without `patient_code` — expect HTTP 400.
5. POST a measurement with unknown `measure_type` — expect HTTP 400.
6. POST a measurement with a value outside its documented demo validation range — expect HTTP 400.
7. Visit `/api/analytics` — expect KPIs, department/month summaries, and educational flags.
8. Open dashboard — expect KPI cards, three charts, and a flag table.
9. Stop MySQL and request `/api/health` — expect HTTP 503 and a meaningful connection error.
10. Try a visit with a nonexistent patient or department ID — expect HTTP 400.

## 9. Troubleshooting
- **Access denied:** update `.env` credentials and restart Flask.
- **Unknown database:** execute `schema.sql` in MySQL.
- **Module not found:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Charts not appearing:** load `/api/analytics` once; check write permission for `static/charts/`.
- **Port in use:** change the `app.run` port or stop the other process using port 5000.

## 10. Suggested demo flow (8–12 minutes)
1. Explain the operational analytics problem and the synthetic-data boundary.
2. Show the MySQL tables and foreign-key relationships.
3. Open `/api/health`, `/api/patients`, and `/api/analytics`.
4. Show the dashboard KPIs and three charts.
5. Demonstrate one valid API request and one invalid request.
6. Explain the illustrative rules and limitations.
7. Conclude with possible extensions: authentication/role restrictions, audit logs, CSV import, pagination, and automated tests.

## 11. Team contribution suggestion (5 members)
1. **Member 1 — Backend:** Flask app setup, routes, request validation.
2. **Member 2 — Database:** MySQL schema, relationships, seed data, SQL checks.
3. **Member 3 — Analytics:** Pandas/NumPy processing and rule explanation.
4. **Member 4 — Visuals/UI:** Matplotlib charts and dashboard styling.
5. **Member 5 — QA & documentation:** test cases, README, screenshots, presentation and demo coordination.

## 12. Project conclusion
CareLens demonstrates how a Flask API can connect to MySQL and turn synthetic records into transparent operational summaries and charts. It also demonstrates why health-related indicators need careful validation, clear limitations, and strict separation from clinical decision-making.
