
# patient.py
# Handles patient management: adding patients, assigning medications,
# viewing schedules, reminders, and dose acknowledgment.

from datetime import datetime, date, timedelta
from database import get_connection

def _err(msg):
    """Prints a visible error message on the command line."""
    print()
    print("  !! ERROR: " + msg)
    print()


# ─────────────────────────────────────────────
#  ENSURE TABLES EXIST
# ─────────────────────────────────────────────

def _ensure_tables():
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(255) NOT NULL,
                medication_name VARCHAR(255) NOT NULL,
                dosage VARCHAR(100),
                frequency VARCHAR(100),
                schedule_times VARCHAR(255),
                prescribed_by VARCHAR(255),
                prescribed_date DATE,
                end_date DATE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acknowledged_doses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(255) NOT NULL,
                medication_name VARCHAR(255) NOT NULL,
                dose_key VARCHAR(20) NOT NULL,
                UNIQUE KEY unique_dose (patient_name, medication_name, dose_key)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        _err(f"Could not set up database tables: {e}")


# ─────────────────────────────────────────────
#  FEATURE 1: ADD NEW PATIENT
# ─────────────────────────────────────────────

def add_patient():
    _ensure_tables()
    print("\n  --- ADD NEW PATIENT ---")
    patient_id = input("  Patient ID        : ").strip()
    name       = input("  Patient full name : ").strip()
    age        = input("  Age               : ").strip()
    gender     = input("  Gender            : ").strip()
    phone      = input("  Phone number      : ").strip()

    if not patient_id or not name:
        _err("Patient ID and full name cannot be empty.")
        return

    if age and not age.isdigit():
        _err(f"Age must be a whole number. You entered: '{age}'")
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO patients (patient_id, patient_name, age, gender, phone) VALUES (%s, %s, %s, %s, %s)",
            (patient_id, name, int(age) if age else None, gender or None, phone or None)
        )
        conn.commit()
        cursor.close()
        print(f"\n  Patient '{name}' (ID: {patient_id}) added successfully!\n")
    except Exception as e:
        _err(f"Failed to add patient '{name}': {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  FEATURE 2: ASSIGN MEDICATION TO PATIENT
# ─────────────────────────────────────────────

def assign_medication():
    _ensure_tables()
    print("\n  --- ASSIGN MEDICATION TO PATIENT ---")
    patient_name    = input("  Patient name                        : ").strip()
    medication_name = input("  Medication name                     : ").strip()
    dosage          = input("  Dosage (e.g. 500mg)                 : ").strip()
    frequency       = input("  Frequency (e.g. Twice daily)        : ").strip()
    schedule_times  = input("  Schedule times (e.g. 08:00,20:00)   : ").strip()
    prescribed_by   = input("  Prescribed by                       : ").strip()
    end_date        = input("  End date (YYYY-MM-DD)               : ").strip()

    if not patient_name or not medication_name:
        _err("Patient name and medication name cannot be empty.")
        return

    validated_end_date = None
    if end_date:
        try:
            parsed = datetime.strptime(end_date, "%Y-%m-%d").date()
            if parsed.year < 1000 or parsed.year > 9999:
                _err(f"Invalid year in end date: {parsed.year}. Must be between 1000 and 9999.")
                return
            if parsed < date.today():
                _err(f"End date '{end_date}' is in the past. Please enter a future date.")
                return
            validated_end_date = end_date
        except ValueError:
            _err(f"Invalid date format '{end_date}'. Use YYYY-MM-DD (e.g. 2025-12-31).")
            return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prescriptions
                (patient_name, medication_name, dosage, frequency,
                 schedule_times, prescribed_by, prescribed_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_name, medication_name, dosage, frequency,
            schedule_times, prescribed_by, date.today().isoformat(), validated_end_date
        ))
        conn.commit()
        cursor.close()
        print(f"\n  Medication '{medication_name}' assigned to '{patient_name}' successfully!\n")
    except Exception as e:
        _err(f"Failed to assign medication '{medication_name}' to '{patient_name}': {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  HELPER: GET PRESCRIPTIONS FOR A PATIENT
# ─────────────────────────────────────────────

def get_patient_prescriptions(patient_name):
    _ensure_tables()
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM prescriptions WHERE LOWER(patient_name) = LOWER(%s)",
            (patient_name,)
        )
        rows = cursor.fetchall()
        cursor.execute(
            "SELECT medication_name, dose_key FROM acknowledged_doses WHERE LOWER(patient_name) = LOWER(%s)",
            (patient_name,)
        )
        ack_rows = cursor.fetchall()
        cursor.close()
    except Exception as e:
        _err(f"Could not load prescriptions for '{patient_name}': {e}")
        return []
    finally:
        conn.close()

    ack_map = {}
    for ack in ack_rows:
        ack_map.setdefault(ack["medication_name"].lower(), []).append(ack["dose_key"])

    result = []
    for row in rows:
        times_raw = row.get("schedule_times", "") or ""
        result.append({
            "patient_name"      : row["patient_name"],
            "medication_name"   : row["medication_name"],
            "dosage"            : row.get("dosage", ""),
            "frequency"         : row.get("frequency", ""),
            "schedule_times"    : [t.strip() for t in times_raw.split(",") if t.strip()],
            "acknowledged_dates": ack_map.get(row["medication_name"].lower(), []),
        })
    return result


# ─────────────────────────────────────────────
#  FEATURE 3: VIEW MEDICATION SCHEDULE
# ─────────────────────────────────────────────

def view_medication_schedule(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.")
        print("  Please contact your pharmacist.\n")
        return

    print(f"\n  MEDICATION SCHEDULE FOR: {patient_name.upper()}")
    print("  " + "-" * 65)
    print(f"  {'MEDICATION':<20} {'DOSAGE':<10} {'FREQUENCY':<18} {'TIMES'}")
    print("  " + "-" * 65)
    for p in prescriptions:
        times = ", ".join(p["schedule_times"])
        print(f"  {p['medication_name']:<20} {p['dosage']:<10} {p['frequency']:<18} {times}")
    print("  " + "-" * 65)
    print(f"  Total medications: {len(prescriptions)}\n")


# ─────────────────────────────────────────────
#  FEATURE 4: CHECK REMINDERS
# ─────────────────────────────────────────────

def check_reminders(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    now       = datetime.now()
    today_str = date.today().isoformat()
    upcoming  = []
    missed    = []

    for p in prescriptions:
        for time_str in p["schedule_times"]:
            try:
                scheduled_dt = datetime.strptime(f"{today_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                _err(f"Skipping invalid schedule time '{time_str}' for {p['medication_name']}.")
                continue

            dose_key = f"{today_str} {time_str}"
            if dose_key in p["acknowledged_dates"]:
                continue

            minutes_until = (scheduled_dt - now).total_seconds() / 60
            if -120 <= minutes_until < 0:
                missed.append((p["medication_name"], p["dosage"], time_str))
            elif 0 <= minutes_until <= 120:
                upcoming.append((p["medication_name"], p["dosage"], time_str))

    if upcoming:
        print(f"\n  UPCOMING DOSES (due within 2 hours):")
        print("  " + "-" * 45)
        for name, dosage, time_str in upcoming:
            print(f"  -> {name} {dosage}  at  {time_str}")
    else:
        print("\n  No upcoming doses in the next 2 hours.")

    if missed:
        print(f"\n  MISSED DOSES (not yet acknowledged):")
        print("  " + "-" * 45)
        for name, dosage, time_str in missed:
            print(f"  x  {name} {dosage}  -- was due at  {time_str}")
        print("\n  Please acknowledge missed doses or inform your pharmacist.\n")
    else:
        print("  No missed doses recorded for today.\n")


# ─────────────────────────────────────────────
#  FEATURE 5: ACKNOWLEDGE A DOSE
# ─────────────────────────────────────────────

def acknowledge_dose(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ACKNOWLEDGE A DOSE -- {patient_name.upper()}")
    print("  " + "-" * 45)
    print("  Your medications:")
    for i, p in enumerate(prescriptions, 1):
        times = ", ".join(p["schedule_times"])
        print(f"  {i}. {p['medication_name']} {p['dosage']}  (scheduled: {times})")

    print()
    med_name  = input("  Enter the medication name you just took: ").strip()
    dose_time = input("  Enter the scheduled time (HH:MM): ").strip()

    match = next((p for p in prescriptions if p["medication_name"].lower() == med_name.lower()), None)
    if not match:
        _err(f"Medication '{med_name}' not found in your prescriptions.")
        return

    if dose_time not in match["schedule_times"]:
        _err(f"'{dose_time}' is not a scheduled time for {med_name}. Scheduled times: {', '.join(match['schedule_times'])}")
        return

    today_str = date.today().isoformat()
    dose_key  = f"{today_str} {dose_time}"

    if dose_key in match["acknowledged_dates"]:
        _err(f"You already acknowledged {med_name} at {dose_time} today.")
        return

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT IGNORE INTO acknowledged_doses (patient_name, medication_name, dose_key) VALUES (%s, %s, %s)",
            (patient_name, match["medication_name"], dose_key)
        )
        conn.commit()
        cursor.close()
        print(f"\n  Dose acknowledged: {match['medication_name']} {match['dosage']} at {dose_time} -- {today_str}")
        print("  Well done for staying on track!\n")
    except Exception as e:
        _err(f"Could not save acknowledgment for '{med_name}': {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  FEATURE 6: ADHERENCE SUMMARY
# ─────────────────────────────────────────────

def view_adherence_summary(patient_name):
    prescriptions = get_patient_prescriptions(patient_name)
    if not prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ADHERENCE SUMMARY (Last 7 Days) -- {patient_name.upper()}")
    print("  " + "-" * 55)

    today      = date.today()
    week_dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    for p in prescriptions:
        total_expected = len(p["schedule_times"]) * 7
        total_taken    = sum(
            1 for ack in p["acknowledged_dates"]
            if any(ack.startswith(d) for d in week_dates)
        )
        adherence_pct = round((total_taken / total_expected) * 100) if total_expected else 0
        bar = "X" * (adherence_pct // 10) + "-" * (10 - adherence_pct // 10)
        print(f"  {p['medication_name']:<20} [{bar}] {adherence_pct}%  ({total_taken}/{total_expected} doses)")
    print()


# ─────────────────────────────────────────────
#  PATIENT MENU
# ─────────────────────────────────────────────

def patient_menu(patient_name):
    _ensure_tables()
    while True:
        print("\n" + "=" * 50)
        print(f"   PATIENT MENU -- {patient_name.upper()}")
        print("=" * 50)
        print("  1. View my medication schedule")
        print("  2. Check reminders (due & missed doses)")
        print("  3. Acknowledge a dose (confirm intake)")
        print("  4. View adherence summary (last 7 days)")
        print("  5. Back to main menu")
        print("=" * 50)

        choice = input("  Enter your choice (1-5): ").strip()

        if choice == "1":
            view_medication_schedule(patient_name)
        elif choice == "2":
            check_reminders(patient_name)
        elif choice == "3":
            acknowledge_dose(patient_name)
        elif choice == "4":
            view_adherence_summary(patient_name)
        elif choice == "5":
            print("  Returning to main menu...\n")
            break
        else:
            _err(f"'{choice}' is not a valid option. Please enter a number between 1 and 5.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    name = input("  Enter patient name to test: ").strip()
    patient_menu(name)
