-- Milestone 9: Doctor Appointment Summary Query

SELECT
    d.doctor_id,
    d.full_name AS doctor_name,
    COUNT(a.appointment_id) AS appointment_count
FROM doctor d
LEFT JOIN appointment a
    ON d.doctor_id = a.doctor_id
GROUP BY
    d.doctor_id,
    d.full_name;


-- Milestone 10: Doctor Appointment Summary View

CREATE OR REPLACE VIEW vw_doctor_appointment_summary AS
SELECT
    d.doctor_id,
    d.full_name AS doctor_name,
    COUNT(a.appointment_id) AS appointment_count
FROM doctor d
LEFT JOIN appointment a
    ON d.doctor_id = a.doctor_id
GROUP BY
    d.doctor_id,
    d.full_name;