# CareSync Pro
 
## Project Overview
 
CareSync Pro is a hospital management system built to track patients,
doctors, appointments, billing, prescriptions, reports, and
notifications in one place. It gives hospital staff a live dashboard
showing patient records, billing status, and doctor workload, backed
by a MySQL database and a FastAPI backend.

## Technology Stack
 
- Python — backend language
- FastAPI — REST API framework
- MySQL — database (8 tables: doctor, patient, appointment,
  billing, prescription, notification, report, activity_log)
- Vue.js — frontend dashboard framework
- Chart.js — charts on the dashboard

## API Endpoints
 
| Method | URL | Description |

GET :- `/summary`  Overall counts: patients, doctors, appointments, bills, prescriptions, notifications, reports, revenue, rejection rate.
GET :- `/patients` 50 most recently registered active patients.
GET :- `/patients/{patient_id}`  One patient’s details by ID,  or 404 if not found.
GET :- `/patients/{patient_id}/appointments` |All appointments for a specific patient (empty list if none).
GET :- `/billing`  50 most recent bills with patient name and status.
GET :- `/doctors`  All active doctors with completed appointment count.
GET :- `/analytics/doctors` Doctor name + total appointment count, from the vw_doctor_appointment_summary view.
GET :- `/prescriptions`  50 most recent active prescriptions with patient and doctor names.
GET :- `/notifications`  50 most recent notifications, unread first.
GET :- `/reports`  50 most recent active reports with patient name
  and report type.
GET :- `/activity-log` | Last 100 audit trail entries.

## How to Run
 
### 1. Set up the database
 
1. Open MySQL Workbench and run `schema.sql` to create the `caresync_pro` database and all 8 tables.
2. Run `queries.sql` to create the SQL views used by the dashboard.
3. Run `generate_data1.py` once to fill the database with sample data: python generate_data1.py
   
 ### 2. Start the backend
 
1. Open a terminal in the project folder.
2. Install the required packages if you haven’t already: pip install fastapi uvicorn mysql-connector-python
3. Start the API server: uvicorn main:app --reload
4. Confirm it’s running by opening http://127.0.0.1:8000/docs  you should see the Swagger documentation page.
 
### 3. Open the dashboard
 
1. Make sure the backend from Step 2 is still running.
2. Open `dashboard.html` in your browser (double-click it, or use the Live Server extension in VS Code).
3. The dashboard loads live data across the summary cards, the patient lookup box, and the tabs (Patients, Billing, Doctors,Prescriptions, Notifications, Reports, Activity Log, Doctor Summary).

 
