from datetime import datetime, date
from database import get_connection


def _ensure_tables():
    """Creates the patients table if it does not already exist."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(255) NOT NULL UNIQUE
            )
        """)
        # Fix existing tables where patient_id lacks AUTO_INCREMENT
        cursor.execute("""
            ALTER TABLE patients MODIFY COLUMN patient_id INT AUTO_INCREMENT
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"\n  !! ERROR: Could not ensure patients table: {e}\n")


def get_patient_prescriptions(patient_name):
    """Fetch all active prescriptions for a patient from the database."""
    try:
        conn = get_connection(dictionary=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prescriptions WHERE LOWER(patient_name) = LOWER(%s)",
            (patient_name,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"\n  !! ERROR: Could not load prescriptions: {e}\n")
        return []


def add_patient():
    """Adds a new patient to the patients table."""
    _ensure_tables()
    print("\n  --- Add New Patient ---")
    name = input("  Enter patient full name: ").strip()
    if not name:
        print("  Patient name cannot be empty.\n")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT patient_name FROM patients WHERE LOWER(patient_name) = LOWER(%s)",
            (name,)
        )
        if cursor.fetchone():
            print(f"\n  Patient '{name}' is already registered.\n")
            cursor.close()
            conn.close()
            return
        cursor.execute("INSERT INTO patients (patient_name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"\n  Patient '{name}' added successfully.\n")
    except Exception as e:
        print(f"\n  !! ERROR: Could not add patient: {e}\n")


def assign_medication():
    """Assigns a medication (prescription) to a patient."""
    from prescription import add_prescription
    add_prescription()


def view_medication_schedule(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'. Contact your pharmacist.\n")
        return

    print(f"\n  MEDICATION SCHEDULE - {patient_name.upper()}")
    print(f"  {'MEDICATION':<20} {'DOSAGE':<10} {'FREQUENCY':<15} {'TIMES'}")
    print("  " + "-" * 60)
    for p in prescriptions:
        print(f"  {p['medication_name']:<20} {p['dosage']:<10} {p['frequency']:<15} {p['schedule_times']}")
    print(f"\n  Total: {len(prescriptions)} medication(s)\n")


def check_reminders(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    now = datetime.now()
    today_str = date.today().isoformat()
    upcoming, missed = [], []

    for p in prescriptions:
        for t in p["schedule_times"].split(","):
            t = t.strip()
            try:
                scheduled = datetime.strptime(f"{today_str} {t}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            mins = (scheduled - now).total_seconds() / 60
            if -120 <= mins < 0:
                missed.append((p["medication_name"], p["dosage"], t))
            elif 0 <= mins <= 120:
                upcoming.append((p["medication_name"], p["dosage"], t))

    if upcoming:
        print("\n  UPCOMING DOSES (next 2 hours):")
        for name, dosage, t in upcoming:
            print(f"    - {name} {dosage} at {t}")
    else:
        print("\n  No upcoming doses in the next 2 hours.")

    if missed:
        print("\n  MISSED DOSES:")
        for name, dosage, t in missed:
            print(f"    - {name} {dosage} was due at {t}")
    else:
        print("  No missed doses today.\n")


def acknowledge_dose(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ACKNOWLEDGE A DOSE - {patient_name.upper()}")
    for i, p in enumerate(prescriptions, 1):
        print(f"  {i}. {p['medication_name']} {p['dosage']} (times: {p['schedule_times']})")

    med_name = input("\n  Medication name you just took: ").strip()
    dose_time = input("  Scheduled time (HH:MM): ").strip()

    for p in prescriptions:
        if p["medication_name"].lower() == med_name.lower():
            times = [t.strip() for t in p["schedule_times"].split(",")]
            if dose_time not in times:
                print(f"\n  '{dose_time}' is not a valid scheduled time for {med_name}.")
                print(f"  Scheduled times are: {p['schedule_times']}\n")
                return
            print(f"\n  Dose recorded: {med_name} {p['dosage']} at {dose_time}. Well done!\n")
            return

    print(f"\n  Medication '{med_name}' not found in your prescriptions.\n")


def view_adherence_summary(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ADHERENCE SUMMARY - {patient_name.upper()}")
    print("  " + "-" * 50)
    print("  (Based on active prescriptions from the database)\n")
    for p in prescriptions:
        times_count = len(p["schedule_times"].split(","))
        expected = times_count * 7
        print(f"  {p['medication_name']:<20} {times_count} dose(s)/day — {expected} expected this week")
    print()


def patient_menu(patient_name):
    print(f"\n  Welcome, {patient_name}!")
    check_reminders(patient_name)

    while True:
        print("  PATIENT MENU")
        print("  1. View medication schedule")
        print("  2. Check reminders")
        print("  3. Acknowledge a dose")
        print("  4. View adherence summary")
        print("  5. Back to main menu")

        choice = input("  Choice (1-5): ").strip()
        if choice == "1":   view_medication_schedule(patient_name)
        elif choice == "2": check_reminders(patient_name)
        elif choice == "3": acknowledge_dose(patient_name)
        elif choice == "4": view_adherence_summary(patient_name)
        elif choice == "5":
            print("  Returning to main menu...\n")
            break
        else:
            print("  Invalid choice. Enter 1-5.\n")
