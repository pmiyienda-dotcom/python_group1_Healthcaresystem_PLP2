
# This file handles all patient-facing features of the Medication Management System.
# Patients can view their medication schedule, check reminders, and acknowledge doses.

import json
import os
from datetime import datetime, date, timedelta

# ─────────────────────────────────────────────
#  DATA FILE PATH
# ─────────────────────────────────────────────

PRESCRIPTIONS_FILE = "prescriptions.json"


# ─────────────────────────────────────────────
#  HELPER: LOAD PRESCRIPTIONS FROM FILE
# ─────────────────────────────────────────────

def load_prescriptions():
    """
    Loads all prescriptions from the JSON data file.
    Returns an empty list if the file does not exist yet.
    """
    if not os.path.exists(PRESCRIPTIONS_FILE):
        return []
    with open(PRESCRIPTIONS_FILE, "r") as f:
        return json.load(f)


# ─────────────────────────────────────────────
#  HELPER: SAVE PRESCRIPTIONS TO FILE
# ─────────────────────────────────────────────

def save_prescriptions(prescriptions):
    """
    Saves the updated prescriptions list back to the JSON data file.
    """
    with open(PRESCRIPTIONS_FILE, "w") as f:
        json.dump(prescriptions, f, indent=4)


# ─────────────────────────────────────────────
#  HELPER: GET PRESCRIPTIONS FOR A PATIENT
# ─────────────────────────────────────────────

def get_patient_prescriptions(patient_name):
    """
    Returns a list of all prescriptions assigned to the given patient.
    Matching is case-insensitive.
    """
    prescriptions = load_prescriptions()
    return [p for p in prescriptions if p["patient_name"].lower() == patient_name.lower()]


# ─────────────────────────────────────────────
#  FEATURE 1: VIEW MEDICATION SCHEDULE
# ─────────────────────────────────────────────

def view_medication_schedule(patient_name):
    """
    Displays all medications currently prescribed to the patient,
    including drug name, dosage, frequency, and schedule times.
    """
    patient_prescriptions = get_patient_prescriptions(patient_name)

    if not patient_prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.")
        print("  Please contact your pharmacist if you believe this is an error.\n")
        return

    print(f"\n  MEDICATION SCHEDULE FOR: {patient_name.upper()}")
    print("  " + "─" * 60)
    print(f"  {'MEDICATION':<20} {'DOSAGE':<10} {'FREQUENCY':<15} {'TIMES'}")
    print("  " + "─" * 60)

    for p in patient_prescriptions:
        times = ", ".join(p.get("schedule_times", []))
        print(f"  {p['medication_name']:<20} {p['dosage']:<10} {p['frequency']:<15} {times}")

    print("  " + "─" * 60)
    print(f"  Total medications prescribed: {len(patient_prescriptions)}\n")


# ─────────────────────────────────────────────
#  FEATURE 2: CHECK REMINDERS (DUE & MISSED DOSES)
# ─────────────────────────────────────────────

def check_reminders(patient_name):
    """
    Checks the patient's prescription schedule and shows:
    - Doses due within the next 2 hours (upcoming reminders)
    - Doses that were missed (scheduled time has passed and not acknowledged today)
    """
    patient_prescriptions = get_patient_prescriptions(patient_name)

    if not patient_prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    now = datetime.now()
    today_str = date.today().isoformat()
    upcoming = []
    missed = []

    for p in patient_prescriptions:
        schedule_times = p.get("schedule_times", [])
        acknowledged_dates = p.get("acknowledged_dates", [])  # List of "YYYY-MM-DD HH:MM" strings

        for time_str in schedule_times:
            try:
                # Build a full datetime for today's scheduled dose
                scheduled_dt = datetime.strptime(f"{today_str} {time_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                continue

            # Check if this specific dose (date + time) has already been acknowledged
            dose_key = f"{today_str} {time_str}"
            already_acknowledged = dose_key in acknowledged_dates

            if already_acknowledged:
                continue  # Skip — patient already confirmed this dose

            minutes_until = (scheduled_dt - now).total_seconds() / 60

            if -120 <= minutes_until < 0:
                # Dose time has passed within the last 2 hours → missed
                missed.append((p["medication_name"], p["dosage"], time_str))
            elif 0 <= minutes_until <= 120:
                # Dose is due within the next 2 hours → upcoming
                upcoming.append((p["medication_name"], p["dosage"], time_str))

    # ── Display upcoming reminders ──
    if upcoming:
        print(f"\n  ⏰  UPCOMING DOSES (due within 2 hours):")
        print("  " + "─" * 45)
        for name, dosage, time_str in upcoming:
            print(f"  → {name} {dosage}  at  {time_str}")
    else:
        print("\n  No upcoming doses in the next 2 hours.")

    # ── Display missed doses ──
    if missed:
        print(f"\n  ⚠️   MISSED DOSES (not yet acknowledged):")
        print("  " + "─" * 45)
        for name, dosage, time_str in missed:
            print(f"  ✗ {name} {dosage}  — was due at  {time_str}")
        print("\n  Please acknowledge missed doses or inform your pharmacist.\n")
    else:
        print("  No missed doses recorded for today.\n")


# ─────────────────────────────────────────────
#  FEATURE 3: ACKNOWLEDGE A DOSE
# ─────────────────────────────────────────────

def acknowledge_dose(patient_name):
    """
    Allows the patient to confirm that they have taken a specific dose.
    Records the acknowledgment in the prescriptions data file so the
    system can track adherence and mark the dose as completed.
    """
    patient_prescriptions = get_patient_prescriptions(patient_name)

    if not patient_prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ACKNOWLEDGE A DOSE — {patient_name.upper()}")
    print("  " + "─" * 45)

    # Show the patient their medications for easy reference
    print("  Your medications:")
    for i, p in enumerate(patient_prescriptions, 1):
        times = ", ".join(p.get("schedule_times", []))
        print(f"  {i}. {p['medication_name']} {p['dosage']}  (scheduled: {times})")

    print()
    med_name = input("  Enter the medication name you just took: ").strip()
    dose_time = input("  Enter the scheduled time for this dose (HH:MM): ").strip()

    # Find the matching prescription
    all_prescriptions = load_prescriptions()
    found = False

    for p in all_prescriptions:
        if (p["patient_name"].lower() == patient_name.lower() and
                p["medication_name"].lower() == med_name.lower()):

            # Validate the time is in their schedule
            if dose_time not in p.get("schedule_times", []):
                print(f"\n  '{dose_time}' is not a scheduled time for {med_name}.")
                print(f"  Scheduled times are: {', '.join(p.get('schedule_times', []))}\n")
                return

            # Build the dose key and check if already acknowledged
            today_str = date.today().isoformat()
            dose_key = f"{today_str} {dose_time}"

            if "acknowledged_dates" not in p:
                p["acknowledged_dates"] = []

            if dose_key in p["acknowledged_dates"]:
                print(f"\n  You have already acknowledged {med_name} at {dose_time} today.\n")
                return

            # Record the acknowledgment
            p["acknowledged_dates"].append(dose_key)
            save_prescriptions(all_prescriptions)

            print(f"\n  ✔  Dose acknowledged: {med_name} {p['dosage']} at {dose_time} — {today_str}")
            print("  Your record has been updated. Well done for staying on track!\n")
            found = True
            break

    if not found:
        print(f"\n  Medication '{med_name}' was not found in your prescriptions.\n")


# ─────────────────────────────────────────────
#  FEATURE 4: VIEW ADHERENCE SUMMARY (BONUS)
# ─────────────────────────────────────────────

def view_adherence_summary(patient_name):
    """
    Shows a summary of how many doses the patient has acknowledged
    over the past 7 days, giving a basic adherence overview.
    """
    patient_prescriptions = get_patient_prescriptions(patient_name)

    if not patient_prescriptions:
        print(f"\n  No prescriptions found for '{patient_name}'.\n")
        return

    print(f"\n  ADHERENCE SUMMARY (Last 7 Days) — {patient_name.upper()}")
    print("  " + "─" * 50)

    today = date.today()
    week_dates = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

    for p in patient_prescriptions:
        acknowledged = p.get("acknowledged_dates", [])
        total_expected = len(p.get("schedule_times", [])) * 7
        total_taken = sum(
            1 for ack in acknowledged
            if any(ack.startswith(d) for d in week_dates)
        )

        if total_expected == 0:
            adherence_pct = 0
        else:
            adherence_pct = round((total_taken / total_expected) * 100)

        bar_filled = adherence_pct // 10
        bar = "█" * bar_filled + "░" * (10 - bar_filled)

        print(f"  {p['medication_name']:<20} [{bar}] {adherence_pct}%  ({total_taken}/{total_expected} doses)")

    print()


# ─────────────────────────────────────────────
#  PATIENT MENU (called from main.py)
# ─────────────────────────────────────────────

def patient_menu(patient_name):
    """
    Displays the patient-facing menu.
    Called by main.py after the patient logs in.
    Automatically shows reminders on entry.
    """
    print(f"\n  Welcome, {patient_name}!")
    print("  Running automatic reminder check...")
    check_reminders(patient_name)

    while True:
        print("         PATIENT MENU")
        print("  1. View my medication schedule")
        print("  2. Check reminders (due & missed doses)")
        print("  3. Acknowledge a dose (confirm intake)")
        print("  4. View adherence summary (last 7 days)")
        print("  5. Back to main menu")

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
            print("  Invalid choice. Please enter a number between 1 and 5.\n")


# ─────────────────────────────────────────────
#  RUN DIRECTLY (for testing only)
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Create a sample prescriptions file for testing if one doesn't exist
    if not os.path.exists(PRESCRIPTIONS_FILE):
        sample_data = [
            {
                "patient_name": "Alice",
                "medication_name": "Paracetamol",
                "dosage": "500mg",
                "frequency": "Twice daily",
                "schedule_times": ["08:00", "20:00"],
                "acknowledged_dates": []
            },
            {
                "patient_name": "Alice",
                "medication_name": "Amoxicillin",
                "dosage": "250mg",
                "frequency": "Three times daily",
                "schedule_times": ["07:00", "13:00", "19:00"],
                "acknowledged_dates": []
            }
        ]
        save_prescriptions(sample_data)
        print("  Sample prescriptions file created for testing (prescriptions.json).")

    test_name = input("  Enter patient name to test: ").strip()
    patient_menu(test_name)
