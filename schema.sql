CREATE DATABASE IF NOT EXISTS healthcare_analytics
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE healthcare_analytics;

CREATE TABLE IF NOT EXISTS patients (
  patient_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_code VARCHAR(30) NOT NULL UNIQUE,
  age_band VARCHAR(10) NOT NULL,
  optional_demographic VARCHAR(40) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT chk_age_band CHECK (age_band IN ('0-17','18-29','30-44','45-59','60+'))
);

CREATE TABLE IF NOT EXISTS departments (
  department_id INT AUTO_INCREMENT PRIMARY KEY,
  department_name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS visits (
  visit_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  department_id INT NOT NULL,
  visit_date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_visit_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  CONSTRAINT fk_visit_department FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS measurements (
  measurement_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  measurement_date DATE NOT NULL,
  measure_type VARCHAR(30) NOT NULL,
  value DECIMAL(8,2) NOT NULL,
  unit VARCHAR(12) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_measurement_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  CONSTRAINT chk_measure_type CHECK (measure_type IN ('heart_rate','temperature','systolic_bp','oxygen_saturation'))
);

CREATE TABLE IF NOT EXISTS risk_indicators (
  indicator_id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  measurement_id INT NOT NULL,
  rule_code VARCHAR(60) NOT NULL,
  indicator_value VARCHAR(30) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_indicator_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
  CONSTRAINT fk_indicator_measurement FOREIGN KEY (measurement_id) REFERENCES measurements(measurement_id) ON DELETE CASCADE
);

INSERT IGNORE INTO departments (department_name) VALUES
('Cardiology'), ('General Medicine'), ('Orthopedics'), ('Pediatrics'), ('Neurology');

-- All records below are fictional and created only for demonstration.
INSERT IGNORE INTO patients (patient_code, age_band, optional_demographic) VALUES
('SYN-1001','18-29','Sample A'), ('SYN-1002','30-44','Sample B'),
('SYN-1003','45-59','Sample C'), ('SYN-1004','60+','Sample D'),
('SYN-1005','0-17','Sample E'), ('SYN-1006','30-44','Sample F');

INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-01' FROM patients p JOIN departments d ON d.department_name='General Medicine' WHERE p.patient_code='SYN-1001'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-01');
INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-05' FROM patients p JOIN departments d ON d.department_name='Cardiology' WHERE p.patient_code='SYN-1002'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-05');
INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-08' FROM patients p JOIN departments d ON d.department_name='Orthopedics' WHERE p.patient_code='SYN-1003'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-08');
INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-12' FROM patients p JOIN departments d ON d.department_name='General Medicine' WHERE p.patient_code='SYN-1004'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-12');
INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-14' FROM patients p JOIN departments d ON d.department_name='Pediatrics' WHERE p.patient_code='SYN-1005'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-14');
INSERT INTO visits (patient_id, department_id, visit_date)
SELECT p.patient_id, d.department_id, '2026-10-20' FROM patients p JOIN departments d ON d.department_name='Cardiology' WHERE p.patient_code='SYN-1006'
AND NOT EXISTS (SELECT 1 FROM visits v WHERE v.patient_id=p.patient_id AND v.visit_date='2026-10-20');

INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-01', 'heart_rate', 78, 'bpm' FROM patients WHERE patient_code='SYN-1001'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='heart_rate' AND m.measurement_date='2026-10-01');
INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-05', 'temperature', 38.6, 'C' FROM patients WHERE patient_code='SYN-1002'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='temperature' AND m.measurement_date='2026-10-05');
INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-08', 'systolic_bp', 128, 'mmHg' FROM patients WHERE patient_code='SYN-1003'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='systolic_bp' AND m.measurement_date='2026-10-08');
INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-12', 'oxygen_saturation', 88, '%' FROM patients WHERE patient_code='SYN-1004'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='oxygen_saturation' AND m.measurement_date='2026-10-12');
INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-14', 'heart_rate', 132, 'bpm' FROM patients WHERE patient_code='SYN-1005'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='heart_rate' AND m.measurement_date='2026-10-14');
INSERT INTO measurements (patient_id, measurement_date, measure_type, value, unit)
SELECT patient_id, '2026-10-20', 'temperature', 36.8, 'C' FROM patients WHERE patient_code='SYN-1006'
AND NOT EXISTS (SELECT 1 FROM measurements m WHERE m.patient_id=patients.patient_id AND m.measure_type='temperature' AND m.measurement_date='2026-10-20');
