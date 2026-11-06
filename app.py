import os
from datetime import date
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from analytics import build_report

load_dotenv()
app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "healthcare_analytics"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

def query_db(sql, params=(), fetch=True):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else None
        if not fetch:
            conn.commit()
            result = {"inserted_id": cur.lastrowid}
        cur.close()
        return result
    finally:
        conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    try:
        query_db("SELECT 1 AS ok")
        return jsonify({"status": "ok", "database": "connected"})
    except Error as exc:
        return jsonify({"status": "error", "message": "Database connection failed", "detail": str(exc)}), 503

@app.get("/api/patients")
def list_patients():
    rows = query_db("""SELECT patient_id, patient_code, age_band, optional_demographic
                       FROM patients ORDER BY patient_id""")
    return jsonify(rows)

@app.post("/api/patients")
def add_patient():
    data = request.get_json(silent=True) or {}
    code = str(data.get("patient_code", "")).strip()
    age_band = str(data.get("age_band", "")).strip()
    demo = data.get("optional_demographic")
    if not code or len(code) > 30:
        return jsonify({"error": "patient_code is required (max 30 characters)"}), 400
    if age_band not in {"0-17", "18-29", "30-44", "45-59", "60+"}:
        return jsonify({"error": "age_band must be one of 0-17, 18-29, 30-44, 45-59, 60+"}), 400
    try:
        result = query_db(
            "INSERT INTO patients (patient_code, age_band, optional_demographic) VALUES (%s,%s,%s)",
            (code, age_band, demo), fetch=False)
        return jsonify({"message": "Synthetic patient added", **result}), 201
    except Error as exc:
        return jsonify({"error": "Could not add patient", "detail": str(exc)}), 400

@app.get("/api/departments")
def departments():
    return jsonify(query_db("SELECT department_id, department_name FROM departments ORDER BY department_name"))

@app.post("/api/visits")
def add_visit():
    data = request.get_json(silent=True) or {}
    try:
        patient_id = int(data["patient_id"])
        department_id = int(data["department_id"])
        visit_date = date.fromisoformat(str(data["visit_date"]))
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "patient_id, department_id and visit_date (YYYY-MM-DD) are required"}), 400
    try:
        result = query_db(
            "INSERT INTO visits (patient_id, department_id, visit_date) VALUES (%s,%s,%s)",
            (patient_id, department_id, visit_date), fetch=False)
        return jsonify({"message": "Visit added", **result}), 201
    except Error as exc:
        return jsonify({"error": "Could not add visit; check patient and department IDs", "detail": str(exc)}), 400

@app.post("/api/measurements")
def add_measurement():
    data = request.get_json(silent=True) or {}
    allowed = {
        "heart_rate": ("bpm", 30, 220),
        "temperature": ("C", 25, 45),
        "systolic_bp": ("mmHg", 50, 260),
        "oxygen_saturation": ("%", 50, 100),
    }
    kind = str(data.get("measure_type", "")).strip()
    if kind not in allowed:
        return jsonify({"error": "measure_type must be heart_rate, temperature, systolic_bp or oxygen_saturation"}), 400
    try:
        patient_id = int(data["patient_id"])
        measured_on = date.fromisoformat(str(data["measurement_date"]))
        value = float(data["value"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "patient_id, measurement_date (YYYY-MM-DD), and numeric value are required"}), 400
    unit, low, high = allowed[kind]
    if not low <= value <= high:
        return jsonify({"error": f"{kind} must be within the project's illustrative validation range {low}-{high} {unit}"}), 400
    try:
        result = query_db(
            "INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit) VALUES (%s,%s,%s,%s,%s)",
            (patient_id, measured_on, kind, value, unit), fetch=False)
        return jsonify({"message": "Measurement added", **result, "unit": unit}), 201
    except Error as exc:
        return jsonify({"error": "Could not add measurement; check patient ID", "detail": str(exc)}), 400

@app.get("/api/analytics")
def analytics():
    try:
        report = build_report(get_connection)
        return jsonify(report)
    except Exception as exc:
        app.logger.exception("Analytics failed")
        return jsonify({"error": "Analytics could not be generated", "detail": str(exc)}), 500

@app.get("/api/charts/<path:filename>")
def chart(filename):
    from flask import send_from_directory, abort
    safe_files = {"visits_by_department.png", "monthly_visits.png", "indicator_distribution.png"}
    if filename not in safe_files:
        abort(404)
    chart_dir = os.path.join(app.root_path, "static", "charts")
    if not os.path.exists(os.path.join(chart_dir, filename)):
        try:
            build_report(get_connection)
        except Exception:
            abort(503)
    return send_from_directory(chart_dir, filename)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
