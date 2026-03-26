import getpass
import inventory
import patient
import prescription
import Reminders
from database import get_connection


def _err(msg):
    print()
    print("  !! ERROR: " + msg)
    print()
 
 
# =============================================================
#  PHARMACIST PASSWORD — change this if needed
# =============================================================
 
PHARMACIST_PASSWORD = "123"
MAX_ATTEMPTS = 3
 
 
# =============================================================
#  HELPER — PRINT A BANNER
# =============================================================
 
def print_banner(title):
    """Prints a clean section header."""
    print()
    print("=" * 55)
    print(f"   {title}")
    print("=" * 55)
 
 
# =============================================================
#  PHARMACIST LOGIN
# =============================================================
 
def pharmacist_login():
    """
    Asks for the pharmacist password.
    3 wrong attempts locks the session.
    Returns True if password is correct, False if locked out.
    """
    print_banner("PHARMACIST LOGIN")
    print("   This area is restricted to pharmacists only.\n")
 
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            password = getpass.getpass(f"   Enter password (attempt {attempt}/{MAX_ATTEMPTS}): ")
        except Exception:
            password = input(f"   Enter password (attempt {attempt}/{MAX_ATTEMPTS}): ")
 
        if password == PHARMACIST_PASSWORD:
            print("\n   ✔  Access granted. Welcome, Pharmacist!\n")
            return True
        else:
            remaining = MAX_ATTEMPTS - attempt
            if remaining > 0:
                print(f"   ✘  Wrong password. {remaining} attempt(s) remaining.\n")
            else:
                print("\n   ✘  Too many failed attempts. Access denied.\n")
 
    return False
 
 
# =============================================================
#  PATIENT LOGIN — name only
# =============================================================
 
def patient_login():
    """
    Asks the patient for their name and checks it exists in the database.
    Returns the name string if found, otherwise None.
    """
    print_banner("PATIENT LOGIN")

    name = input("   Enter your full name: ").strip()

    if not name:
        print("   No name entered. Returning to home screen.\n")
        return None

    # Check if patient exists in the database
    patient._ensure_tables()
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT patient_name FROM patients WHERE LOWER(patient_name) = LOWER(%s)",
            (name,)
        )
        row = cursor.fetchone()
        cursor.close()
    except Exception as e:
        _err(f"Could not check patient registration: {e}")
        return None
    finally:
        conn.close()

    if not row:
        print(f"\n   !! You are not registered in the system.")
        print(f"   Please ask your pharmacist to add you first.\n")
        return None

    print(f"\n   ✔  Welcome, {name}!\n")
    return name
 
 
# =============================================================
#  PHARMACIST MENU
# =============================================================
 
def pharmacist_menu():
    """
    Full pharmacist menu — only reachable after correct password.
    Connects to inventory.py, prescription.py, and Reminders.py.
    """
    print_banner("PHARMACIST PORTAL")
 
    while True:
        print()
        print("   PHARMACIST MENU:")
        print("   1. Inventory Management")
        print("   2. Add a Prescription")
        print("   3. View a Patient's Prescriptions")
        print("   4. Check Patient Reminders")
        print("   5. Send All Patient Reminders")
        print("   6. Add New Patient")
        print("   7. Assign Medication to Patient")
        print("   8. Log out")
        print()

        choice = input("   Select (1-8): ").strip()

        if choice == "1":
            inventory.inventory_menu()

        elif choice == "2":
            prescription.add_prescription()

        elif choice == "3":
            name = input("\n   Enter Patient name to view prescriptions: ").strip()
            if name:
                prescription.view_patient_prescriptions(name)
            else:
                print("   Please enter a valid patient name.")

        elif choice == "4":
            name = input("\n   Enter Patient name to check reminders: ").strip()
            if name:
                prescription.check_reminders(name)
            else:
                print("   Please enter a valid patient name.")

        elif choice == "5":
            print_banner("SENDING REMINDERS TO ALL PATIENTS")
            Reminders.send_reminders()
            print()

        elif choice == "6":
            patient.add_patient()

        elif choice == "7":
            patient.assign_medication()

        elif choice == "8":
            print("\n   Logged out. Returning to home screen...\n")
            break

        else:
            print("   Invalid choice. Please enter a number between 1 and 8.")
 
 
# =============================================================
#  MAIN LOOP
# =============================================================
 
def main():
    """
    Opening screen — user picks Pharmacist or Patient.
    Pharmacist needs password. Patient just needs their name.
    """
    while True:
        print_banner("HEALTHCARE MEDICATION MANAGEMENT SYSTEM")
        print("   Who are you?\n")
        print("   1. Pharmacist  (password required)")
        print("   2. Patient     (name only)")
        print("   3. Exit")
        print()
 
        choice = input("   Select (1-3): ").strip()
 
        # ── PHARMACIST ───────────────────────────────────────
        if choice == "1":
            if pharmacist_login():
                pharmacist_menu()
            else:
                print("   Access denied. Returning to home screen.\n")
 
        # ── PATIENT ──────────────────────────────────────────
        elif choice == "2":
            name = patient_login()
            if name:
                patient.patient_menu(name)  # patient menu only — no pharmacy access
 
        # ── EXIT ─────────────────────────────────────────────
        elif choice == "3":
            print("\n   Goodbye! Stay healthy.\n")
            break
 
        else:
            print("\n   Invalid choice. Please enter 1, 2, or 3.\n")
 
 
# =============================================================
#  ENTRY POINT
# =============================================================
 
if __name__ == "__main__":
    main()