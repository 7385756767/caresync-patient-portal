from main import get_db

db = get_db()
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS prescription (
    prescription_id INT NOT NULL AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration_days INT,
    instructions TEXT,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prescription_id),
    CONSTRAINT fk_prescription_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (appointment_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prescription_patient
        FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prescription_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctor (doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_prescription_patient (patient_id),
    INDEX idx_prescription_appointment (appointment_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notification (
    notification_id INT NOT NULL AUTO_INCREMENT,
    user_type ENUM('Doctor','Patient','Billing') NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    INDEX idx_notification_user (user_type, user_id),
    INDEX idx_notification_read (is_read)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS report (
    report_id INT NOT NULL AUTO_INCREMENT,
    patient_id INT NOT NULL,
    appointment_id INT,
    report_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(255),
    generated_by INT,
    is_deleted TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (report_id),
    CONSTRAINT fk_report_patient
        FOREIGN KEY (patient_id) REFERENCES patient (patient_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_report_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (appointment_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_report_doctor
        FOREIGN KEY (generated_by) REFERENCES doctor (doctor_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_report_patient (patient_id)
)
""")

db.commit()

print("3 missing tables created successfully")

cursor.close()
db.close()