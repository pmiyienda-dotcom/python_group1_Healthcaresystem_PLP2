import datetime
from database import get_connection

try:
    from inventory import check_stock, reduce_stock
    INVENTORY_AVAILABLE = True
except ImportError:
    INVENTORY_AVAILABLE = False


def _err(msg):
    print()
    print("  !! ERROR: " + msg)
    print()


def _ensure_tables():
    """Creates the prescriptions table if it does not already exist."""
    try:
        conn = get_connection()
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
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"\n  !! ERROR: Could not ensure prescriptions table: {e}\n")


# ─────────────────────────────────────────────
#  ADD PRESCRIPTION
# ─────────────────────────────────────────────

def add_prescription():
    print("\n--- Add New Prescription ---")

    patient_name    = input("Enter patient name      : ").strip()
    medication_name = input("Enter medication name   : ").strip()
    dosage          = input("Enter dosage (e.g. 500mg): ").strip()
    frequency       = input("Enter frequency (e.g. Twice daily): ").strip()
    schedule_times  = input("Enter times (e.g. 08:00,20:00): ").strip()
    prescribed_by   = input("Prescribed by           : ").strip()
    end_date        = input("Enter end date (YYYY-MM-DD): ").strip()

    _ensure_tables()

    if not patient_name or not medication_name:
        _err("Patient name and medication name cannot be empty.")
        return

    validated_end_date = None
    if end_date:
        try:
            parsed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            if parsed < datetime.date.today():
                _err(f"End date '{end_date}' is in the past. Enter a future date.")
                return
            validated_end_date = end_date
        except ValueError:
            _err(f"Invalid date format '{end_date}'. Use YYYY-MM-DD (e.g. 2025-12-31).")
            return

    quantity_input = input("Enter quantity needed   : ").strip()
    if not quantity_input.isdigit():
        _err(f"Quantity must be a whole number. You entered: '{quantity_input}'")
        return
    quantity = int(quantity_input)

    if INVENTORY_AVAILABLE:
        try:
            stock = check_stock(medication_name)
            if stock < quantity:
                _err(f"Not enough stock for '{medication_name}'. Available: {stock}, Required: {quantity}")
                return
        except Exception as e:
            _err(f"Inventory check failed for '{medication_name}': {e}. Continuing anyway.")

    prescribed_date = str(datetime.date.today())

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO prescriptions
                (patient_name, medication_name, dosage, frequency,
                 schedule_times, prescribed_by, prescribed_date, end_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient_name, medication_name, dosage, frequency,
            schedule_times, prescribed_by, prescribed_date, validated_end_date
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        _err(f"Failed to save prescription for '{patient_name}': {e}")
        return

    if INVENTORY_AVAILABLE:
        try:
            reduce_stock(medication_name, quantity)
        except Exception as e:
            _err(f"Could not reduce stock for '{medication_name}': {e}")

    print("Prescription added successfully!")


# ─────────────────────────────────────────────
#  VIEW PRESCRIPTIONS
# ─────────────────────────────────────────────

def view_patient_prescriptions(patient_name):
    print("\n--- Medication Schedule ---")
    try:
        conn   = get_connection(dictionary=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prescriptions WHERE LOWER(patient_name) = LOWER(%s)",
            (patient_name,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        _err(f"Could not load prescriptions for '{patient_name}': {e}")
        return

    if not rows:
        print(f"No prescriptions found for '{patient_name}'.")
        return

    for p in rows:
        print(f"\nPatient  : {p['patient_name']}")
        print(f"Drug     : {p['medication_name']}")
        print(f"Dosage   : {p['dosage']}")
        print(f"Frequency: {p['frequency']}")
        print(f"Times    : {p['schedule_times']}")
        print(f"End Date : {p['end_date']}")


# ─────────────────────────────────────────────
#  REMINDER CHECK (pharmacist view)
# ─────────────────────────────────────────────

def check_reminders(patient_name):
    print("\n--- Medication Reminders ---")
    current_time = datetime.datetime.now().strftime("%H:%M")

    try:
        conn   = get_connection(dictionary=True)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM prescriptions WHERE LOWER(patient_name) = LOWER(%s)",
            (patient_name,)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        _err(f"Could not load reminders for '{patient_name}': {e}")
        return

    if not rows:
        print(f"No prescriptions found for '{patient_name}'.")
        return

    for p in rows:
        times = [t.strip() for t in (p.get("schedule_times") or "").split(",") if t.strip()]
        for t in times:
            if t == current_time:
                print(f"TAKE NOW: {p['medication_name']} ({p['dosage']})")

    print("Reminder check complete.")


# ─────────────────────────────────────────────
#  STANDALONE TEST MENU
# ─────────────────────────────────────────────

if __name__ == "__main__":
    while True:
        print("\n--- Prescription System ---")
        print("1. Add Prescription")
        print("2. View Patient Prescriptions")
        print("3. Check Reminders")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_prescription()
        elif choice == "2":
            name = input("Enter patient name: ").strip()
            view_patient_prescriptions(name)
        elif choice == "3":
            name = input("Enter patient name: ").strip()
            check_reminders(name)
        elif choice == "4":
            print("Exiting...")
            break
        else:
            _err(f"'{choice}' is not a valid option. Please enter 1, 2, 3, or 4.")
