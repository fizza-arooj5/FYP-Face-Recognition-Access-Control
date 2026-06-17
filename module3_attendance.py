# ============================================
# Module 3 - Attendance & Stay Time Analysis
# Student: Fizza Arooj
# FYP: Face Recognition Based Intelligent
#      Access Control System
# ============================================

import csv
import os
import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # FIX: must be before pyplot import — renders off-screen, no GUI needed
import matplotlib.pyplot as plt

# ============================================
# FOLDER PATHS
# ============================================

DATABASE_PATH   = 'F:/FYP_Project/database/'
REPORTS_PATH    = 'F:/FYP_Project/reports/'
ATTENDANCE_FILE = DATABASE_PATH + 'attendance.csv'

os.makedirs(DATABASE_PATH, exist_ok=True)
os.makedirs(REPORTS_PATH,  exist_ok=True)

def record_entry(name):
    timestamp = datetime.datetime.now()
    date      = timestamp.strftime('%Y-%m-%d')
    time      = timestamp.strftime('%H:%M:%S')

    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if row[0] == name and row[1] == date and row[3] == '':
                    print(f"\n⚠️  {name} already checked in! Entry: {row[2]}")
                    return

    file_exists = os.path.exists(ATTENDANCE_FILE)
    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['name','date','entry_time','exit_time','hours_worked','status'])
        writer.writerow([name, date, time, '', '', 'PRESENT'])

    print(f"\n{'='*40}")
    print(f"  ✅ ENTRY RECORDED!")
    print(f"  Name: {name}  Date: {date}  Time: {time}")
    print(f"{'='*40}\n")

def record_exit(name):
    if not os.path.exists(ATTENDANCE_FILE):
        print("❌ No attendance records!")
        return

    timestamp = datetime.datetime.now()
    exit_time = timestamp.strftime('%H:%M:%S')
    date      = timestamp.strftime('%Y-%m-%d')

    rows = []
    with open(ATTENDANCE_FILE, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows   = list(reader)

    updated = False
    hours   = 0
    for i in range(len(rows)-1, -1, -1):
        row = rows[i]
        if row[0] == name and row[1] == date and row[3] == '':
            entry = datetime.datetime.strptime(f"{date} {row[2]}", '%Y-%m-%d %H:%M:%S')
            exit_ = datetime.datetime.strptime(f"{date} {exit_time}", '%Y-%m-%d %H:%M:%S')
            hours = round(( exit_ - entry).seconds / 3600, 2)
            rows[i][3] = exit_time
            rows[i][4] = str(hours)
            updated    = True
            break

    if not updated:
        print(f"\n⚠️  No entry found for {name} today!")
        return

    with open(ATTENDANCE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"\n{'='*40}")
    print(f"  ✅ EXIT RECORDED!  Name: {name}  Hours: {hours}")
    print(f"{'='*40}\n")

def add_demo_data():
    users_file = DATABASE_PATH + 'users.csv'
    if not os.path.exists(users_file):
        print("❌ No users registered!")
        return

    users = []
    with open(users_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            users.append(row[0])

    if not users:
        print("❌ No users found!")
        return

    today     = datetime.datetime.now()
    file_exists = os.path.exists(ATTENDANCE_FILE)
    demo_records = []

    schedules = [
        ('09:00:00', '17:30:00'),
        ('08:45:00', '17:00:00'),
        ('09:15:00', '18:00:00'),
        ('09:00:00', '16:30:00'),
        ('08:30:00', '17:00:00'),
    ]

    for user in users:
        for day in range(5, 0, -1):
            date     = (today - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
            day_name = (today - datetime.timedelta(days=day)).strftime('%A')
            if day_name in ['Saturday', 'Sunday']:
                continue
            entry_t, exit_t = schedules[day % len(schedules)]
            entry = datetime.datetime.strptime(f"{date} {entry_t}", '%Y-%m-%d %H:%M:%S')
            exit_ = datetime.datetime.strptime(f"{date} {exit_t}", '%Y-%m-%d %H:%M:%S')
            hours = round((exit_ - entry).seconds / 3600, 2)
            demo_records.append([user, date, entry_t, exit_t, str(hours), 'PRESENT'])

    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['name','date','entry_time','exit_time','hours_worked','status'])
        writer.writerows(demo_records)

    print(f"\n✅ DEMO DATA ADDED! {len(demo_records)} records for {len(users)} user(s)")

def view_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance records!")
        return

    print(f"\n{'='*65}")
    print("  ATTENDANCE RECORDS")
    print(f"{'Name':<15} {'Date':<12} {'Entry':<10} {'Exit':<10} {'Hours':<8} {'Status':<8}")
    print("-"*65)

    with open(ATTENDANCE_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)
        for row in rows:
            exit_t = row[3] if row[3] else "---"
            hours  = row[4] if row[4] else "---"
            print(f"{row[0]:<15} {row[1]:<12} {row[2]:<10} {exit_t:<10} {hours:<8} {row[5]:<8}")

    print(f"{'='*65}  Total: {len(rows)}\n")

def generate_report():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance records!")
        return None

    df = pd.read_csv(ATTENDANCE_FILE)
    df['hours_worked'] = pd.to_numeric(df['hours_worked'], errors='coerce').fillna(0)

    summary = df.groupby('name').agg(
        days_present=('date', 'count'),
        total_hours=('hours_worked', 'sum'),
        avg_hours=('hours_worked', 'mean')
    ).reset_index()

    summary['total_hours'] = summary['total_hours'].round(2)
    summary['avg_hours']   = summary['avg_hours'].round(2)

    report_path = REPORTS_PATH + 'attendance_report.csv'
    summary.to_csv(report_path, index=False)
    print(f"✅ Report saved!")
    return summary

def plot_attendance():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance records!")
        return

    df = pd.read_csv(ATTENDANCE_FILE)
    df['hours_worked'] = pd.to_numeric(df['hours_worked'], errors='coerce').fillna(0)

    summary     = df.groupby('name')['hours_worked'].sum().reset_index()
    days_summary = df.groupby('name')['date'].count().reset_index()

    if summary.empty:
        print("❌ No data to plot!")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors = ['#2196F3','#4CAF50','#FF9800','#E91E63','#9C27B0']

    bars = ax1.bar(summary['name'], summary['hours_worked'],
                   color=colors[:len(summary)])
    for bar, val in zip(bars, summary['hours_worked']):
        ax1.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.1, f'{val:.1f}h',
                ha='center', fontsize=10)
    ax1.set_title('Total Hours Worked', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Employee')
    ax1.set_ylabel('Hours')

    ax2.pie(days_summary['date'], labels=days_summary['name'],
            autopct='%1.1f%%', colors=colors[:len(days_summary)])
    ax2.set_title('Days Present Distribution', fontsize=13, fontweight='bold')

    plt.suptitle('Attendance Analysis Report', fontsize=15, fontweight='bold')
    plt.tight_layout()

    chart_path = REPORTS_PATH + 'attendance_chart.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()   # FIX: close figure to free memory, don't call plt.show()
    print(f"✅ Chart saved: {chart_path}")

def todays_summary():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance records!")
        return

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*55}")
    print(f"  TODAY'S ATTENDANCE - {today}")
    print(f"{'='*55}")
    present = 0
    with open(ATTENDANCE_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[1] == today:
                present += 1
                exit_t = row[3] if row[3] else "Still inside"
                hours  = row[4] if row[4] else "---"
                print(f"  → {row[0]:<15} In: {row[2]}  Out: {exit_t}  Hrs: {hours}")

    if present == 0:
        print("  No attendance today!")
    print(f"{'='*55}  Present: {present}\n")