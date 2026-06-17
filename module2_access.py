# ============================================
# Module 2 - Access Control System
# Student: Fizza Arooj & Ghulam Fatima
# FYP: Virtualized Iris-Based Intelligent
#      Access Control System
# ============================================

import csv
import os
import datetime

# ============================================
# FOLDER PATHS
# ============================================
DATABASE_PATH = 'F:/FYP_Project/database/'
LOGS_FILE     = DATABASE_PATH + 'access_logs.csv'

os.makedirs(DATABASE_PATH, exist_ok=True)

# ============================================
# FUNCTION 1 - Log Access Event
# ============================================
def log_access(name, status, reason=""):
    timestamp   = datetime.datetime.now()
    date        = timestamp.strftime('%Y-%m-%d')
    time        = timestamp.strftime('%H:%M:%S')
    hour        = timestamp.hour

    if 6 <= hour < 12:
        time_of_day = "Morning"
    elif 12 <= hour < 17:
        time_of_day = "Afternoon"
    elif 17 <= hour < 21:
        time_of_day = "Evening"
    else:
        time_of_day = "Night"

    file_exists = os.path.exists(LOGS_FILE)

    with open(LOGS_FILE, 'a',
              newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'date', 'time', 'name',
                'status', 'time_of_day',
                'reason'])
        writer.writerow([
            date, time, name,
            status, time_of_day, reason])

    print(f"📋 Logged: {name} | "
          f"{status} | {time}")

# ============================================
# FUNCTION 2 - Grant Access
# ============================================
def grant_access(name):
    print(f"\n{'='*40}")
    print(f"  ✅ ACCESS GRANTED!")
    print(f"  Welcome: {name}")
    print(f"  Time: "
          f"{datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*40}\n")

    log_access(name,
               "GRANTED",
               "Authorized user")
    return True

# ============================================
# FUNCTION 3 - Deny Access
# ============================================
def deny_access(name="Unknown",
                attempt_number=1):
    print(f"\n{'='*40}")
    print(f"  🚨 ACCESS DENIED!")
    print(f"  Person: {name}")
    print(f"  Attempt: {attempt_number}/3")
    print(f"  Time: "
          f"{datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*40}\n")

    log_access(name,
               "DENIED",
               f"Attempt {attempt_number}/3")
    return False

# ============================================
# FUNCTION 4 - Security Alert
# ============================================
def security_alert(name="Unknown"):
    timestamp = datetime.datetime.now()

    print(f"\n{'!'*40}")
    print(f"  ⚠️  SECURITY ALERT!")
    print(f"  3 failed attempts detected!")
    print(f"  Person: {name}")
    print(f"  Time: "
          f"{timestamp.strftime('%H:%M:%S')}")
    print(f"  Photo captured!")
    print(f"{'!'*40}\n")

    log_access(name,
               "SECURITY_ALERT",
               "3 failed attempts")

# ============================================
# FUNCTION 5 - Process Access Decision
# Called by main.py
# ============================================
def process_access(recognition_result,
                   recognized_name,
                   frame,
                   failed_attempts):

    if recognition_result == "RECOGNIZED":
        grant_access(recognized_name)
        return "GRANTED", 0
    else:
        failed_attempts += 1
        deny_access("Unknown",
                    failed_attempts)

        if failed_attempts >= 3:
            security_alert("Unknown")
            failed_attempts = 0

        return "DENIED", failed_attempts

# ============================================
# FUNCTION 6 - View Access Logs
# ============================================
def view_access_logs():
    if not os.path.exists(LOGS_FILE):
        print("\n❌ No logs found!")
        print("   No access attempts yet!")
        return

    print(f"\n{'='*65}")
    print("  ACCESS LOGS")
    print(f"{'='*65}")
    print(f"{'Date':<12} {'Time':<10} "
          f"{'Name':<15} {'Status':<18} "
          f"{'Period':<12}")
    print("-"*65)

    with open(LOGS_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)

        if not rows:
            print("  No records found!")
        else:
            for row in rows:
                print(
                    f"{row[0]:<12} "
                    f"{row[1]:<10} "
                    f"{row[2]:<15} "
                    f"{row[3]:<18} "
                    f"{row[4]:<12}")

    print(f"{'='*65}")
    print(f"  Total Records: {len(rows)}")
    print(f"{'='*65}\n")

# ============================================
# FUNCTION 7 - Get Statistics
# ============================================
def get_statistics():
    if not os.path.exists(LOGS_FILE):
        print("\n❌ No logs found!")
        return

    granted = 0
    denied  = 0
    alerts  = 0
    names   = {}

    with open(LOGS_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            status = row[3]
            name   = row[2]

            if status == "GRANTED":
                granted += 1
                names[name] = \
                    names.get(name, 0) + 1
            elif status == "DENIED":
                denied += 1
            elif status == "SECURITY_ALERT":
                alerts += 1

    print(f"\n{'='*40}")
    print("  ACCESS STATISTICS")
    print(f"{'='*40}")
    print(f"  Total Granted:   {granted}")
    print(f"  Total Denied:    {denied}")
    print(f"  Security Alerts: {alerts}")
    print(f"{'='*40}")
    print("  Access by Person:")
    if names:
        for name, count in names.items():
            print(f"  → {name}: "
                  f"{count} times")
    else:
        print("  No authorized access yet!")
    print(f"{'='*40}\n")

# ============================================
# TEST MENU - Run this file directly
# to test module 2 only
# ============================================
if __name__ == "__main__":
    while True:
        print("\n" + "="*40)
        print("   ACCESS CONTROL MODULE")
        print("="*40)
        print("  1. View Access Logs")
        print("  2. View Statistics")
        print("  3. Test Grant Access")
        print("  4. Test Deny Access")
        print("  5. Exit")
        print("="*40)

        choice = input("Enter choice: ")

        if choice == "1":
            view_access_logs()
        elif choice == "2":
            get_statistics()
        elif choice == "3":
            name = input("Enter name: ")
            grant_access(name)
        elif choice == "4":
            deny_access("Unknown", 1)
        elif choice == "5":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Invalid choice!")