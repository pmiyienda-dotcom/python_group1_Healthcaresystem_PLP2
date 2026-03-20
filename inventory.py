#  This file contains all pharmacy drug data and the functions to manage them.
#  ALL PHARMACY DRUGS (stored as a list of dictionaries)

inventory = [
    {"medication_name": "Paracetamol",   "dosage": "500mg",  "quantity": 200, "expiration_date": "2026-12-01", "low_stock_threshold": 30},
    {"medication_name": "Amoxicillin",   "dosage": "250mg",  "quantity": 50,  "expiration_date": "2026-08-15", "low_stock_threshold": 10},
    {"medication_name": "Ibuprofen",     "dosage": "400mg",  "quantity": 150, "expiration_date": "2027-03-10", "low_stock_threshold": 20},
    {"medication_name": "Metformin",     "dosage": "850mg",  "quantity": 80,  "expiration_date": "2026-11-20", "low_stock_threshold": 15},
    {"medication_name": "Omeprazole",    "dosage": "20mg",   "quantity": 60,  "expiration_date": "2027-01-05", "low_stock_threshold": 12},
    {"medication_name": "Ciprofloxacin", "dosage": "500mg",  "quantity": 30,  "expiration_date": "2026-07-01", "low_stock_threshold": 10},
    {"medication_name": "Atorvastatin",  "dosage": "10mg",   "quantity": 120, "expiration_date": "2027-06-15", "low_stock_threshold": 20},
    {"medication_name": "Azithromycin",  "dosage": "500mg",  "quantity": 25,  "expiration_date": "2026-09-30", "low_stock_threshold": 10},
    {"medication_name": "Lisinopril",    "dosage": "5mg",    "quantity": 90,  "expiration_date": "2027-02-28", "low_stock_threshold": 15},
    {"medication_name": "Cetirizine",    "dosage": "10mg",   "quantity": 40,   "expiration_date": "2026-10-10", "low_stock_threshold": 10},
]

#  FEATURE 1: VIEW ALL MEDICATIONS
def view_inventory():
    """
    Displays all medications currently in the inventory.
    """
    if not inventory:
        print("No medications found in inventory.")
        return

    print("\n" + "=" * 70)
    print(f"{'MEDICATION':<20} {'DOSAGE':<10} {'QUANTITY':<10} {'EXPIRY DATE':<15} {'MIN STOCK'}")
    print("=" * 70)

    for med in inventory:
        print(f"{med['medication_name']:<20} {med['dosage']:<10} {med['quantity']:<10} "
              f"{med['expiration_date']:<15} {med['low_stock_threshold']}")

    print("=" * 70 + "\n")

#  FEATURE 2: ADD A NEW MEDICATION

def add_medication():
    """
    Allows the pharmacist to add a new medication to the inventory.
    """
    print("\n Add New Medication ")
    name = input("Enter medication name: ").strip()
    dosage = input("Enter dosage (e.g. 500mg): ").strip()
    quantity = input("Enter quantity in stock: ").strip()
    expiration_date = input("Enter expiration date (YYYY-MM-DD): ").strip()
    low_stock_threshold = input("Enter low stock warning threshold: ").strip()

    # Validate that quantity and threshold are numbers
    if not quantity.isdigit() or not low_stock_threshold.isdigit():
        print("Error: Quantity and threshold must be whole numbers.")
        return

    # Check if medication already exists
    for med in inventory:
        if med["medication_name"].lower() == name.lower():
            print(f"'{name}' already exists in the inventory. Use update instead.")
            return

    # Add the new medication
    new_medication = {
        "medication_name": name,
        "dosage": dosage,
        "quantity": int(quantity),
        "expiration_date": expiration_date,
        "low_stock_threshold": int(low_stock_threshold)
    }

    inventory.append(new_medication)
    print(f"'{name}' has been added to the inventory successfully.\n")


#  FEATURE 3: UPDATE MEDICATION QUANTITY

def update_quantity():
    """
    Allows the pharmacist to update the stock quantity of a medication.
    Used when new stock arrives or medication is dispensed.
    """
    print("\n Update Medication Quantity ")
    name = input("Enter the name of the medication to update: ").strip()
    new_quantity = input("Enter the new quantity: ").strip()

    if not new_quantity.isdigit():
        print("Error: Quantity must be a whole number.")
        return

    for med in inventory:
        if med["medication_name"].lower() == name.lower():
            med["quantity"] = int(new_quantity)
            print(f"Quantity for '{name}' has been updated to {new_quantity}.\n")
            return

    print(f"Medication '{name}' was not found in the inventory.\n")


#  FEATURE 4: REMOVE A MEDICATION

def remove_medication():
    """
    Allows the pharmacist to remove a discontinued medication.
    """
    print("\n Remove Medication ")
    name = input("Enter the name of the medication to remove: ").strip()

    for i, med in enumerate(inventory):
        if med["medication_name"].lower() == name.lower():
            inventory.pop(i)
            print(f"'{name}' has been removed from the inventory.\n")
            return

    print(f"Medication '{name}' was not found in the inventory.\n")


#  FEATURE 5: CHECK LOW STOCK

def check_low_stock():
    """
    Displays a warning for any medications below their minimum stock level.
    """
    low_stock_items = [med for med in inventory if med["quantity"] < med["low_stock_threshold"]]

    if not low_stock_items:
        print("All medications are sufficiently stocked.\n")
    else:
        print("\n LOW STOCK WARNING:")
        print("-" * 45)
        for med in low_stock_items:
            print(f"  {med['medication_name']} — Only {med['quantity']} left "
                  f"(minimum: {med['low_stock_threshold']})")
        print("-" * 45 + "\n")


#  FEATURE 6: CHECK EXPIRATION DATES

def check_expiration():
    """
    Displays warnings for medications expiring within 90 days or already expired.
    """
    from datetime import datetime, date
    today = date.today()
    expiring_soon = []
    already_expired = []

    for med in inventory:
        try:
            expiry = datetime.strptime(med["expiration_date"], "%Y-%m-%d").date()
            days_left = (expiry - today).days

            if days_left < 0:
                already_expired.append(med)
            elif days_left <= 90:
                expiring_soon.append((med, days_left))
        except ValueError:
            print(f"Warning: Invalid date format for '{med['medication_name']}'. Expected YYYY-MM-DD.")

    if already_expired:
        print("\n EXPIRED MEDICATIONS:")
        print("-" * 45)
        for med in already_expired:
            print(f"  {med['medication_name']} expired on {med['expiration_date']}!")
        print("-" * 45)

    if expiring_soon:
        print("\n EXPIRING SOON (within 90 days):")
        print("-" * 45)
        for med, days in expiring_soon:
            print(f"  {med['medication_name']} — expires {med['expiration_date']} ({days} days left)")
        print("-" * 45 + "\n")

    if not already_expired and not expiring_soon:
        print("No medications are expiring soon.\n")


#  INVENTORY MENU (called from main.py)

def inventory_menu():
    """
    Displays the inventory management menu.
    Called by main.py after the pharmacist logs in.
    """
    # Automatically run checks when pharmacist opens inventory
    print("\n🔔 Running automatic inventory checks...")
    check_low_stock()
    check_expiration()

    while True:
        print("=" * 40)
        print("       INVENTORY MANAGEMENT MENU")
        print("=" * 40)
        print("1. View all medications")
        print("2. Add a new medication")
        print("3. Update medication quantity")
        print("4. Remove a medication")
        print("5. Check low stock warnings")
        print("6. Check expiration dates")
        print("7. Back to main menu")
        print("=" * 40)

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            view_inventory()
        elif choice == "2":
            add_medication()
        elif choice == "3":
            update_quantity()
        elif choice == "4":
            remove_medication()
        elif choice == "5":
            check_low_stock()
        elif choice == "6":
            check_expiration()
        elif choice == "7":
            print("Returning to main menu...\n")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.\n")


#  RUN DIRECTLY (for testing only)

if __name__ == "__main__":
    inventory_menu()