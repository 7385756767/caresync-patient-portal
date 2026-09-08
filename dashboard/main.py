
# main.py
# CareSync Dashboard Backend
#
# This file is a FastAPI application.
# It connects to the MySQL database and provides two API endpoints.
# The Vue.js frontend will call these endpoints to get data.
#
# To run this file:
#   uvicorn main:app --reload

from fastapi import FastAPI                        # the web framework
from fastapi.middleware.cors import CORSMiddleware # allows browser to call this API
import mysql.connector                             # connects to MySQL

# ── Create the FastAPI application ──────────────────────────────────────────
app = FastAPI(title='CareSync Dashboard API')

# ── CORS Configuration ───────────────────────────────────────────────────────
# CORS stands for Cross-Origin Resource Sharing.
# Without this, the browser will block the Vue.js page from calling this API.
# allow_origins=['*'] means: accept requests from any browser tab.
# In a production system, you would list specific allowed addresses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['GET'],
    allow_headers=['*'],
)

# ── Database connection helper ───────────────────────────────────────────────
# This function creates a fresh connection to MySQL every time it is called.
# We do not reuse a single connection because MySQL closes idle connections.
def get_db():
    return mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='Admin',  # change this to your own MySQL password
        database='caresync',
        use_pure=True
    )
# ── ENDPOINT 1: Summary numbers ──────────────────────────────────────────────
# URL: http://127.0.0.1:8000/summary
# Returns: total counts for patients, doctors, appointments, and bills
@app.get('/summary')
def get_summary():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    # Count active patients only (soft delete filter)
    cursor.execute('SELECT COUNT(*) AS total FROM patient WHERE is_deleted = 0')
    patients = cursor.fetchone()['total']

    # Count active doctors only
    cursor.execute('SELECT COUNT(*) AS total FROM doctor WHERE is_active = 1')
    doctors = cursor.fetchone()['total']

    # Count all appointments
    cursor.execute('SELECT COUNT(*) AS total FROM appointment')
    appointments = cursor.fetchone()['total']

    # Count all bills
    cursor.execute('SELECT COUNT(*) AS total FROM billing')
    bills = cursor.fetchone()['total']

    # Count rejected bills
    cursor.execute("SELECT COUNT(*) AS total FROM billing WHERE status = 'Rejected'")
    rejected = cursor.fetchone()['total']

    # Calculate rejection percentage
    rejection_rate = round((rejected / bills * 100), 1) if bills > 0 else 0

    # Total revenue collected
    cursor.execute('SELECT ROUND(SUM(amount_paid), 2) AS total FROM billing')
    revenue = cursor.fetchone()['total'] or 0
    cursor.execute('SELECT COUNT(*) AS total FROM prescription WHERE is_deleted = 0')
    prescriptions = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM notification WHERE is_read = 0')
    unread_notifications = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) AS total FROM report WHERE is_deleted = 0')
    reports = cursor.fetchone()['total']

    cursor.close()
    db.close()

    # Return all values as a JSON object
    return {
    'total_patients':        patients,
    'total_doctors':         doctors,
    'total_appointments':    appointments,
    'total_bills':           bills,
    'rejection_rate':        rejection_rate,
    'total_revenue':         float(revenue),
    'total_prescriptions':   prescriptions,
    'unread_notifications':  unread_notifications,
    'total_reports':         reports,
}

# ── ENDPOINT 2: Patient list ─────────────────────────────────────────────────
# URL: http://127.0.0.1:8000/patients
# Returns: list of 50 most recent active patients
@app.get('/patients')
def get_patients():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            patient_id,
            full_name,
            gender,
            blood_group,
            DATE_FORMAT(date_of_birth, '%d %b %Y') AS date_of_birth,
            DATE_FORMAT(created_at,    '%d %b %Y') AS registered_on
        FROM patient
        WHERE is_deleted = 0
        ORDER BY created_at DESC
        LIMIT 50
        '''
    )
    patients = cursor.fetchall()

    cursor.close()
    db.close()

    return {'patients': patients}

# ── ENDPOINT 3: Billing summary ──────────────────────────────────────────────
# URL: http://127.0.0.1:8000/billing
# Returns: recent 50 bills with patient name and status
    return {'patients': patients}


@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            patient_id,
            full_name,
            gender,
            blood_group,
            email
        FROM patient
        WHERE patient_id = %s
          AND is_deleted = 0
        """,
        (patient_id,)
    )

    patient = cursor.fetchone()

    cursor.close()
    db.close()

    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@app.get('/billing')
def get_billing():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            b.bill_id,
            p.full_name AS patient_name,
            b.total_amount,
            b.amount_paid,
            b.status,
            DATE_FORMAT(b.bill_date, '%d %b %Y') AS bill_date
        FROM billing b
        JOIN patient p ON p.patient_id = b.patient_id
        ORDER BY b.created_at DESC
        LIMIT 50
        """
    )

    bills = cursor.fetchall()

    for bill in bills:
        if bill["total_amount"] is not None:
            bill["total_amount"] = float(bill["total_amount"])

        if bill["amount_paid"] is not None:
            bill["amount_paid"] = float(bill["amount_paid"])

    cursor.close()
    db.close()

    return {"bills": bills}

@app.get('/doctors')
def get_doctors():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            doctor_id,
            full_name,
            specialisation,
            phone,
            email,
            is_active
        FROM doctor
        ORDER BY full_name
    """)

    doctors = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'doctors': doctors
    }
@app.get('/prescriptions')
def get_prescriptions():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.prescription_id,
            p.appointment_id,
            p.patient_id,
            p.doctor_id,
            p.medicine_name,
            p.dosage,
            p.frequency,
            p.duration_days,
            p.instructions,
            p.created_at
        FROM prescription p
        WHERE p.is_deleted = 0
        ORDER BY p.created_at DESC
    """)

    prescriptions = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'prescriptions': prescriptions
    }

@app.get('/notifications')
def get_notifications():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            notification_id,
            user_type,
            user_id,
            title,
            message,
            is_read,
            created_at
        FROM notification
        ORDER BY created_at DESC
    """)

    notifications = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'notifications': notifications
    }

@app.get('/reports')
def get_reports():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            report_id,
            patient_id,
            appointment_id,
            report_type,
            file_path,
            generated_by,
            created_at
        FROM report
        WHERE is_deleted = 0
        ORDER BY created_at DESC
    """)

    reports = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'reports': reports
    }

@app.get('/activity-log')
def get_activity_log():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            log_id,
            user_type,
            user_id,
            action,
            target_table,
            target_id,
            old_value,
            new_value,
            ip_address,
            logged_at
        FROM activity_log
        ORDER BY logged_at DESC
        LIMIT 500
    """)

    logs = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'activity_log': logs
    }

@app.get('/doctor-summary')
def get_doctor_summary():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.doctor_id,
            d.full_name,
            d.specialisation,
            COUNT(a.appointment_id) AS total_appointments,
            SUM(CASE WHEN a.status = 'Completed' THEN 1 ELSE 0 END) AS completed_appointments,
            SUM(CASE WHEN a.status = 'Scheduled' THEN 1 ELSE 0 END) AS scheduled_appointments,
            SUM(CASE WHEN a.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_appointments
        FROM doctor d
        LEFT JOIN appointment a
            ON d.doctor_id = a.doctor_id
        WHERE d.is_active = 1
        GROUP BY d.doctor_id, d.full_name, d.specialisation
        ORDER BY total_appointments DESC
    """)

    doctors = cursor.fetchall()

    cursor.close()
    db.close()

    return {
        'doctor_summary': doctors
    }