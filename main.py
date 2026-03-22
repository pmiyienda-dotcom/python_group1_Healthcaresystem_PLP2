import patient
import inventory
import prescription
import Reminders

def show_menu():
    print("\nMAIN MENU:")
    print("1. Patients")
    print("2. Inventory")
    print("3. Prescriptions")
    print("4. Reports")
    print("5. Exit")

def main():
    while True:
        show_menu()
        choice = input("\nSelect (1-5): ")

        if choice == '1':
            patient.main() 
            
        elif choice == '2':
            inventory.main()
            
        elif choice == '3':
            prescription.main()
            
        elif choice == '4':
            # Add report logic here
            pass
            
        elif choice == '5':
            break
            
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
    