import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHART_DIR = os.path.join(os.path.dirname(__file__), "static", "charts")
os.makedirs(CHART_DIR, exist_ok=True)

# Educational flags only. These are illustrative rules, not clinical thresholds.
ILLUSTRATIVE_RULES = {
    "heart_rate": {"low": 50, "high": 120, "description": "Heart-rate value outside the project's illustrative 50–120 bpm band"},
    "temperature": {"low": 35.0, "high": 38.0, "description": "Temperature value outside the project's illustrative 35–38 C band"},
    "systolic_bp": {"low": 90, "high": 180, "description": "Systolic blood pressure outside the project's illustrative 90–180 mmHg band"},
    "oxygen_saturation": {"low": 90, "high": 100, "description": "Oxygen saturation below the project's illustrative 90% threshold"},
}

def build_report(connection_factory):
    conn = connection_factory()
    try:
        patients = pd.read_sql("SELECT patient_id, age_band FROM patients", conn)
        visits = pd.read_sql("""SELECT v.visit_id, v.patient_id, v.visit_date,
                               d.department_name FROM visits v
                               JOIN departments d ON d.department_id=v.department_id""", conn)
        measurements = pd.read_sql("""SELECT measurement_id, patient_id, measurement_date,
                                     measure_type, value, unit FROM measurements""", conn)
    finally:
        conn.close()

    if not visits.empty:
        visits["visit_date"] = pd.to_datetime(visits["visit_date"], errors="coerce")
    if not measurements.empty:
        measurements["measurement_date"] = pd.to_datetime(measurements["measurement_date"], errors="coerce")
    indicator_rows = []
    for row in measurements.to_dict("records"):
        rule = ILLUSTRATIVE_RULES.get(row["measure_type"])
        if not rule:
            continue
        value = float(row["value"])
        flagged = (value < rule["low"] or value > rule["high"]) if row["measure_type"] != "oxygen_saturation" else value < rule["low"]
        if flagged:
            indicator_rows.append({
                "patient_id": int(row["patient_id"]),
                "measurement_id": int(row["measurement_id"]),
                "measure_type": row["measure_type"],
                "value": value,
                "unit": row["unit"],
                "rule_description": rule["description"],
                "indicator": "Review flag (educational)"
            })

    dept_counts = visits.groupby("department_name").size().sort_values(ascending=False) if not visits.empty else pd.Series(dtype=int)
    monthly = visits.dropna(subset=["visit_date"]).assign(month=lambda x: x["visit_date"].dt.to_period("M").astype(str)).groupby("month").size() if not visits.empty else pd.Series(dtype=int)
    indicator_counts = pd.Series([x["measure_type"] for x in indicator_rows]).value_counts()

    def save_bar(series, filename, title, xlabel, ylabel):
        plt.figure(figsize=(8, 4.5))
        if series.empty:
            plt.text(0.5, 0.5, "No data available", ha="center", va="center")
            plt.xticks([])
            plt.yticks([])
        else:
            series.plot(kind="bar")
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, filename), dpi=140)
        plt.close()

    save_bar(dept_counts, "visits_by_department.png", "Visits by Department", "Department", "Number of visits")
    save_bar(monthly, "monthly_visits.png", "Monthly Visit Trend", "Month", "Number of visits")
    save_bar(indicator_counts, "indicator_distribution.png", "Educational Indicator Flags by Measurement Type", "Measurement type", "Number of flags")

    age_counts = patients["age_band"].value_counts().sort_index() if not patients.empty else pd.Series(dtype=int)
    values = measurements["value"].astype(float) if not measurements.empty else pd.Series(dtype=float)
    return {
        "notice": "Educational operational analytics only. Flags are illustrative, not diagnoses or treatment advice. Do not use for real patient-care decisions.",
        "kpis": {
            "synthetic_patient_count": int(len(patients)),
            "visit_count": int(len(visits)),
            "measurement_count": int(len(measurements)),
            "educational_flag_count": int(len(indicator_rows)),
            "measurement_mean": round(float(np.mean(values)), 2) if len(values) else None,
            "measurement_median": round(float(np.median(values)), 2) if len(values) else None
        },
        "visits_by_department": [{"department": str(k), "visits": int(v)} for k, v in dept_counts.items()],
        "monthly_visits": [{"month": str(k), "visits": int(v)} for k, v in monthly.items()],
        "age_band_counts": [{"age_band": str(k), "patients": int(v)} for k, v in age_counts.items()],
        "educational_indicators": indicator_rows
    }
