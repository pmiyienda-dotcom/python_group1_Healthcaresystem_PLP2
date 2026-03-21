import csv
import datetime


# TRY TO IMPORT INVENTORY (SAFE)

try:
    from inventory import check_stock, reduce_stock
    INVENTORY_AVAILABLE = True
except ImportError:
    print(" Inventory functions not found. Running without inventory checks.")
    INVENTORY_AVAILABLE = False


FILE = "patients.csv"


# LOAD DATA
def load_patients():
    with open(FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader)



# ADD PRESCRIPTION

def add_prescription():
    print("\n--- Add New Prescription ---")

    patient_id = input("Enter patient ID: ")
    patient_name = input("Enter patient name: ")
    age = input("Enter age: ")
    gender = input("Enter gender: ")
    phone = input("Enter phone: ")

    medication_name = input("Enter medication name: ")
    dosage = input("Enter dosage (e.g. 500mg): ")
    frequency = input("Enter frequency (e.g. Twice daily): ")
    schedule_times = input("Enter times (e.g. 08:00,20:00): ")

    prescribed_by = input("Prescribed by: ")
    prescribed_date = str(datetime.date.today())
    end_date = input("Enter end date (YYYY-MM-DD): ")

    quantity = int(input("Enter quantity needed: "))

   
    # INVENTORY CHECK (IF AVAILABLE)
   
    if INVENTORY_AVAILABLE:
        try:
            if check_stock(medication_name) < quantity:
                print("⚠ Not enough stock!")
                return
        except:
            print("⚠ Inventory check failed, continuing anyway...")

    
    # SAVE TO CSV
    
    with open(FILE, mode='a', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            patient_id, patient_name, age, gender, phone,
            medication_name, dosage, frequency, schedule_times,
            prescribed_by, prescribed_date, end_date
        ])

   
    # REDUCE STOCK (IF AVAILABLE)
    
    if INVENTORY_AVAILABLE:
        try:
            reduce_stock(medication_name, quantity)
        except:
            print("⚠ Could not update inventory.")

    print("✅ Prescription added successfully!")



# VIEW PRESCRIPTIONS

def view_patient_prescriptions(patient_id):
    patients = load_patients()
    found = False

    print("\n--- Medication Schedule ---")

    for p in patients:
        if p["patient_id"] == patient_id:
            found = True
            print(f"\nPatient: {p['patient_name']}")
            print(f"Drug: {p['medication_name']}")
            print(f"Dosage: {p['dosage']}")
            print(f"Frequency: {p['frequency']}")
            print(f"Times: {p['schedule_times']}")
            print(f"End Date: {p['end_date']}")

    if not found:
        print("No prescriptions found.")
# REMINDER SYSTEM
def check_reminders(patient_id):
    patients = load_patients()
    current_time = datetime.datetime.now().strftime("%H:%M")

    print("\n--- Medication Reminders ---")

    found = False

    for p in patients:
        if p["patient_id"] == patient_id:
            found = True
            times = p["schedule_times"].split(",")

            for t in times:
                if t.strip() == current_time:
                    print(f"⏰ TAKE NOW: {p['medication_name']} ({p['dosage']})")

    if not found:
        print("No prescriptions found.")

    print("✔ Reminder check complete.")


# SIMPLE TEST MENU
if __name__ == "__main__":
    while True:
        print("\n--- Prescription System ---")
        print("1. Add Prescription")
        print("2. View Patient Prescriptions")
        print("3. Check Reminders")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_prescription()

        elif choice == "2":
            pid = input("Enter patient ID: ")
            view_patient_prescriptions(pid)

        elif choice == "3":
            pid = input("Enter patient ID: ")
            check_reminders(pid)

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid option.")