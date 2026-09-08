from main import get_db
import random

db = get_db()
cursor = db.cursor()

cursor.execute("SELECT doctor_id FROM doctor")
doctors = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT patient_id FROM patient")
patients = [row[0] for row in cursor.fetchall()]

actions = [
    "Login",
    "Logout",
    "View Patient",
    "Create Appointment",
    "Update Appointment",
    "Complete Appointment",
    "Create Prescription",
    "View Report",
    "Create Bill",
    "Update Bill"
]

target_tables = [
    "patient",
    "appointment",
    "prescription",
    "report",
    "billing"
]

for i in range(5000):

    user_type = random.choice(["Doctor", "Patient", "Billing"])

    if user_type == "Doctor" and doctors:
        user_id = random.choice(doctors)
    elif user_type == "Patient" and patients:
        user_id = random.choice(patients)
    else:
        user_id = random.randint(1, 10)

    action = random.choice(actions)
    target_table = random.choice(target_tables)

    cursor.execute(
        """
        INSERT INTO activity_log
        (user_type, user_id, action, target_table, target_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user_type,
            user_id,
            action,
            target_table,
            random.randint(1, 500)
        )
    )

db.commit()

print("Activity logs created successfully: 5000")

cursor.close()
db.close()