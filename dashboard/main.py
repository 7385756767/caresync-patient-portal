# main.py
# CareSync Pro Dashboard Backend
#
# This file is a FastAPI application.
# It connects to the caresync_pro MySQL database and provides API endpoints
# covering all 8 tables: doctor, patient, appointment, billing, prescription,
# notification, report, and activity_log.
# The Vue.js frontend will call these endpoints to get data.
#
# To run this file:
#   uvicorn main:app --reload

from fastapi import FastAPI                        # the web framework
from fastapi.middleware.cors import CORSMiddleware # allows browser to call this API
import mysql.connector                             # connects to MySQL

# ── Create the FastAPI application ──────────────────────────────────────────
app = FastAPI(title='CareSync Pro Dashboard API')

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
        host='localhost',
        port=3306,
        user='root',
        database='caresync_pro'
    )

# ── ENDPOINT 1: Summary numbers ──────────────────────────────────────────────
# URL: http://127.0.0.1:8000/summary
# Returns: total counts across every table, for the dashboard's top cards
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

    # Count active prescriptions
    cursor.execute('SELECT COUNT(*) AS total FROM prescription WHERE is_deleted = 0')
    prescriptions = cursor.fetchone()['total']

    # Count unread notifications
    cursor.execute('SELECT COUNT(*) AS total FROM notification WHERE is_read = 0')
    unread_notifications = cursor.fetchone()['total']

    # Count active reports
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
@app.get('/billing')
def get_billing():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            b.bill_id,
            p.full_name                           AS patient_name,
            b.total_amount,
            b.amount_paid,
            b.status,
            DATE_FORMAT(b.bill_date, '%d %b %Y') AS bill_date
        FROM billing b
        JOIN patient p ON p.patient_id = b.patient_id
        ORDER BY b.created_at DESC
        LIMIT 50
        '''
    )
    bills = cursor.fetchall()

    # Convert Decimal types to float so JSON serialisation works correctly
    for bill in bills:
        bill['total_amount'] = float(bill['total_amount'])
        bill['amount_paid']  = float(bill['amount_paid'])

    cursor.close()
    db.close()

    return {'bills': bills}

# ── ENDPOINT 4: Doctor list ──────────────────────────────────────────────────
# URL: http://127.0.0.1:8000/doctors
# Returns: all active doctors with appointment count
@app.get('/doctors')
def get_doctors():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            d.doctor_id,
            d.full_name,
            d.specialisation,
            COUNT(a.appointment_id) AS total_appointments
        FROM doctor d
        LEFT JOIN appointment a ON a.doctor_id = d.doctor_id
            AND a.status = 'Completed'
        WHERE d.is_active = 1
        GROUP BY d.doctor_id, d.full_name, d.specialisation
        ORDER BY total_appointments DESC
        '''
    )
    doctors = cursor.fetchall()

    cursor.close()
    db.close()

    return {'doctors': doctors}

# ── ENDPOINT 5: Prescription list ────────────────────────────────────────────
# URL: http://127.0.0.1:8000/prescriptions
# Returns: 50 most recent active prescriptions with patient and doctor names
@app.get('/prescriptions')
def get_prescriptions():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            pr.prescription_id,
            p.full_name                          AS patient_name,
            d.full_name                          AS doctor_name,
            pr.medicine_name,
            pr.dosage,
            pr.frequency,
            pr.duration_days,
            DATE_FORMAT(pr.created_at, '%d %b %Y') AS prescribed_on
        FROM prescription pr
        JOIN patient p ON p.patient_id = pr.patient_id
        JOIN doctor  d ON d.doctor_id  = pr.doctor_id
        WHERE pr.is_deleted = 0
        ORDER BY pr.created_at DESC
        LIMIT 50
        '''
    )
    prescriptions = cursor.fetchall()

    cursor.close()
    db.close()

    return {'prescriptions': prescriptions}

# ── ENDPOINT 6: Notification list ────────────────────────────────────────────
# URL: http://127.0.0.1:8000/notifications
# Returns: 50 most recent notifications, unread first
@app.get('/notifications')
def get_notifications():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            notification_id,
            user_type,
            user_id,
            title,
            message,
            is_read,
            DATE_FORMAT(created_at, '%d %b %Y %H:%i') AS created_on
        FROM notification
        ORDER BY is_read ASC, created_at DESC
        LIMIT 50
        '''
    )
    notifications = cursor.fetchall()

    cursor.close()
    db.close()

    return {'notifications': notifications}

# ── ENDPOINT 7: Report list ──────────────────────────────────────────────────
# URL: http://127.0.0.1:8000/reports
# Returns: 50 most recent active reports with patient name and report type
@app.get('/reports')
def get_reports():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            r.report_id,
            p.full_name                          AS patient_name,
            r.report_type,
            r.file_path,
            d.full_name                          AS generated_by_doctor,
            DATE_FORMAT(r.created_at, '%d %b %Y') AS generated_on
        FROM report r
        JOIN patient p ON p.patient_id = r.patient_id
        LEFT JOIN doctor d ON d.doctor_id = r.generated_by
        WHERE r.is_deleted = 0
        ORDER BY r.created_at DESC
        LIMIT 50
        '''
    )
    reports = cursor.fetchall()

    cursor.close()
    db.close()

    return {'reports': reports}

# ── ENDPOINT 8: Activity log list ────────────────────────────────────────────
# URL: http://127.0.0.1:8000/activity-log
# Returns: 100 most recent audit trail entries, newest first
@app.get('/activity-log')
def get_activity_log():
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        '''
        SELECT
            log_id,
            user_type,
            user_id,
            action,
            target_table,
            target_id,
            ip_address,
            DATE_FORMAT(logged_at, '%d %b %Y %H:%i') AS logged_on
        FROM activity_log
        ORDER BY logged_at DESC
        LIMIT 100
        '''
    )
    logs = cursor.fetchall()

    cursor.close()
    db.close()

    return {'activity_log': logs}