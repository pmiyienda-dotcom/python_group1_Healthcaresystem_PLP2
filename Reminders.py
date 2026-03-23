import csv
from datetime import datetime
import time

FILE = "patients.csv"

#Reading the patients from patients.csv
def load_patients():
 with open(FILE, mode='r', newline='') as file:
  reader = csv.DictReader(file)
  return list(reader)
#Send reminders to all patients

def send_reminders():
 patients = load_patients()
 now = datetime.now()
 current_time = now.strftime("%H:%M")
 today = now.date()
 reminders_sent = False

 for p in patients:
  #Skip if prescriptions have ended
  end_date = datetime.strptime(p['end_date'], "%Y-%m-%d").date()
  if today > end_date:
   continue
  #Spilt scheduled times
  times = [t.strip() for t in p['schedule_times'].split(",")]
  for t in times:
   schedule_dt = datetime.strptime(t, "%H:%M").replace(
    year=now.year, month=now.month, day=now.day
    )
   #Send reminder within 5 minutes
   if 0 <= (now-schedule_dt).total_seconds() <= 300:
    print(f"Hey {p['patient_name']}! its now time to take {p['medication_name']}")
    print("We wish you a quick recovery")
    reminders_sent = True

 if not reminders_sent:
  print("No reminders now")

if __name__ == "__main__":
    send_reminders()

   

 





        


