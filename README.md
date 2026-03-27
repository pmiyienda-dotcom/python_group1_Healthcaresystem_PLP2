# Healthcare Medication Management System

A command-line Python application for managing pharmacy inventory, patient prescriptions, medication schedules, and dose reminders. Built for pharmacists and patients.

---

## What It Does

### For Pharmacists (password-protected)
- **Inventory Management** — view all medications, add new ones, update stock quantities, remove discontinued drugs, check low-stock warnings, and check expiration dates
- **Prescriptions** — add new prescriptions for patients (with automatic stock deduction), view any patient's full prescription history
- **Patient Management** — register new patients into the system
- **Assign Medication** — assign a prescription/medication directly to a patient
- **Reminders** — check medication reminders for a specific patient, or send reminders to all patients whose dose time is right now

### For Patients (name login)
- **Medication Schedule** — view all active medications with dosage, frequency, and times
- **Reminders** — see upcoming doses (next 2 hours) and any missed doses from the past 2 hours
- **Acknowledge a Dose** — confirm that a dose was taken
- **Adherence Summary** — see how many doses per day are expected for each medication

---

## Project Structure

```
├── main.py           # Entry point — login screen and main menu routing
├── patient.py        # Patient login, patient menu, dose tracking functions
├── prescription.py   # Add/view prescriptions, reminder check (pharmacist view)
├── inventory.py      # In-memory drug inventory management
├── Reminders.py      # Sends reminders to all patients based on current time
├── database.py       # MySQL database connection (single get_connection() function)
├── patients.csv      # (reference data)
└── README.md
```

---

## Requirements

- Python 3.8+
- `mysql-connector-python` library

Install the dependency:

```bash
pip install mysql-connector-python
```

---

## Database Setup

The app connects to a MySQL database. The connection details are in `database.py`.

The following tables must exist in your database:

**`patients` table** (auto-created on first patient login or add):
```sql
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(255) NOT NULL UNIQUE
);
```

**`prescriptions` table** (must be created manually if not present):
```sql
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(255),
    medication_name VARCHAR(255),
    dosage VARCHAR(50),
    frequency VARCHAR(100),
    schedule_times VARCHAR(255),
    prescribed_by VARCHAR(255),
    prescribed_date DATE,
    end_date DATE
);
```

---

## How to Run

From the project directory, run:

```bash
python main.py
```

You will see the home screen:

```
=======================================================
   HEALTHCARE MEDICATION MANAGEMENT SYSTEM
=======================================================
   Who are you?

   1. Pharmacist  (password required)
   2. Patient     (name only)
   3. Exit
```

### Pharmacist Login
- Select `1`
- Enter the password (default: `123`)
- You have 3 attempts before being locked out

### Patient Login
- Select `2`
- Enter your full name exactly as registered by the pharmacist
- You must be registered first — ask the pharmacist to add you via **option 6** in the pharmacist menu

---

## Pharmacist Menu Options

| Option | Action |
|--------|--------|
| 1 | Inventory Management (view, add, update, remove, check stock/expiry) |
| 2 | Add a new prescription for a patient |
| 3 | View a patient's full prescription list |
| 4 | Check medication reminders for a patient |
| 5 | Send reminders to ALL patients due right now |
| 6 | Register a new patient |
| 7 | Assign medication to a patient |
| 8 | Log out |

---

## Patient Menu Options

| Option | Action |
|--------|--------|
| 1 | View medication schedule (all active prescriptions) |
| 2 | Check reminders (upcoming and missed doses) |
| 3 | Acknowledge a dose you just took |
| 4 | View adherence summary (expected doses per week) |
| 5 | Back to main menu |

---

## Notes

- The pharmacist password is set in `main.py` as `PHARMACIST_PASSWORD = "123"` — change it before deploying
- Inventory (`inventory.py`) is stored in memory — changes are lost when the program exits
- Prescription data and patient data are persisted in the MySQL database
- Schedule times must be in `HH:MM` format (e.g. `08:00,20:00`)
- Reminder checks match times within a 5-minute window (for the bulk send) or a 2-hour window (for the patient reminder view)
