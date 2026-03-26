from datetime import datetime
from database import get_connection


def _err(msg):
    print()
    print("  !! ERROR: " + msg)
    print()


def send_reminders():
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM prescriptions")
        patients = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        _err(f"Could not load prescriptions from database: {e}")
        return

    if not patients:
        print("No prescriptions on record.")
        return

    now            = datetime.now()
    today          = now.date()
    reminders_sent = False

    for p in patients:
        try:
            end_date = datetime.strptime(str(p['end_date']), "%Y-%m-%d").date()
            if today > end_date:
                continue
        except (ValueError, KeyError, TypeError) as e:
            _err(f"Invalid end_date for patient '{p.get('patient_name', 'unknown')}': {e}. Skipping.")
            continue

        times = [t.strip() for t in (p.get('schedule_times') or '').split(",") if t.strip()]
        for t in times:
            try:
                schedule_dt = datetime.strptime(t, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )
                if 0 <= (now - schedule_dt).total_seconds() <= 300:
                    print(f"Hey {p['patient_name']}! It's now time to take {p['medication_name']}")
                    print("We wish you a quick recovery")
                    reminders_sent = True
            except ValueError:
                _err(f"Invalid schedule time '{t}' for '{p.get('patient_name', 'unknown')}' — '{p.get('medication_name', '')}'. Skipping.")

    if not reminders_sent:
        print("No reminders due right now.")


if __name__ == "__main__":
    send_reminders()
