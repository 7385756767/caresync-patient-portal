from main import get_db
import random

db = get_db()
cursor = db.cursor(dictionary=True)

# Get existing IDs
cursor.execute("SELECT appointment_id, patient_id, doctor_id FROM appointment WHERE status = 'Completed'")
appointments = cursor.fetchall()

cursor.execute("SELECT patient_id FROM patient WHERE is_deleted = 0")
patients = [row["patient_id"] for row in cursor.fetchall()]

cursor.execute("SELECT doctor_id FROM doctor WHERE is_active = 1")
doctors = [row["doctor_id"] for row in cursor.fetchall()]

# --------------------------------------------------
# 1. PRESCRIPTIONS
# --------------------------------------------------

medicines = [
    ("Paracetamol", "500 mg", "Twice daily"),
    ("Amoxicillin", "500 mg", "Three times daily"),
    ("Ibuprofen", "400 mg", "Twice daily"),
    ("Cetirizine", "10 mg", "Once daily"),
    ("Azithromycin", "500 mg", "Once daily"),
    ("Omeprazole", "20 mg", "Once daily"),
    ("Metformin", "500 mg", "Twice daily"),
    ("Amlodipine", "5 mg", "Once daily"),
]

prescription_count = 0

for appointment in appointments:
    if random.random() < 0.20:
        continue

    number_of_medicines = random.randint(1, 3)

    for medicine in random.sample(medicines, number_of_medicines):
        cursor.execute(
            """
            INSERT INTO prescription
            (appointment_id, patient_id, doctor_id, medicine_name,
             dosage, frequency, duration_days, instructions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                appointment["appointment_id"],
                appointment["patient_id"],
                appointment["doctor_id"],
                medicine[0],
                medicine[1],
                medicine[2],
                random.choice([3, 5, 7, 10, 14]),
                "Take as directed by the doctor"
            )
        )
        prescription_count += 1


# --------------------------------------------------
# 2. REPORTS
# --------------------------------------------------

report_types = [
    "Blood Test",
    "X-Ray",
    "MRI Scan",
    "CT Scan",
    "ECG",
    "Ultrasound",
    "Urine Test"
]

report_count = 0

for appointment in appointments:
    if random.random() < 0.40:
        report_type = random.choice(report_types)

        cursor.execute(
            """
            INSERT INTO report
            (patient_id, appointment_id, report_type, generated_by)
            VALUES (%s, %s, %s, %s)
            """,
            (
                appointment["patient_id"],
                appointment["appointment_id"],
                report_type,
                appointment["doctor_id"]
            )
        )
        report_count += 1


# --------------------------------------------------
# 3. NOTIFICATIONS
# --------------------------------------------------

notification_count = 1200

titles = [
    "Appointment Reminder",
    "New Report Available",
    "Prescription Updated",
    "Payment Reminder",
    "Appointment Completed",
    "Health Check Reminder"
]

messages = [
    "You have an upcoming appointment.",
    "A new medical report is available.",
    "Your prescription has been updated.",
    "Please check your pending payment.",
    "Your appointment has been completed.",
    "Please schedule your regular health check."
]

for i in range(notification_count):

    user_type = random.choice(["Doctor", "Patient", "Billing"])

    if user_type == "Patient":
        user_id = random.choice(patients)
    elif user_type == "Doctor":
        user_id = random.choice(doctors)
    else:
        user_id = random.randint(1, 10)

    is_read = 1 if random.random() < 0.65 else 0

    cursor.execute(
        """
        INSERT INTO notification
        (user_type, user_id, title, message, is_read)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user_type,
            user_id,
            random.choice(titles),
            random.choice(messages),
            is_read
        )
    )


db.commit()

print("Missing data populated successfully!")
print("Prescriptions:", prescription_count)
print("Reports:", report_count)
print("Notifications:", notification_count)

cursor.close()
db.close()