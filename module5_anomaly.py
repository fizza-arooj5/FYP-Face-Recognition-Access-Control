# ============================================
# Module 5 - Anomaly Detection
# Student: Fizza Arooj & Ghulam Fatima
# FYP: Face Recognition Based Intelligent
#      Access Control System
# ============================================

import csv
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')   # FIX: off-screen rendering, no GUI thread needed
import matplotlib.pyplot as plt
import datetime

# ============================================
# FOLDER PATHS
# ============================================

DATABASE_PATH   = 'F:/FYP_Project/database/'
REPORTS_PATH    = 'F:/FYP_Project/reports/'
LOGS_FILE       = DATABASE_PATH + 'access_logs.csv'
ATTENDANCE_FILE = DATABASE_PATH + 'attendance.csv'
ANOMALY_FILE    = REPORTS_PATH  + 'anomaly_report.csv'

os.makedirs(DATABASE_PATH, exist_ok=True)
os.makedirs(REPORTS_PATH,  exist_ok=True)

MAX_FAILED_PER_DAY = 3
UNUSUAL_HOUR_START = 22
UNUSUAL_HOUR_END   = 6
MIN_WORK_HOURS     = 2
MAX_WORK_HOURS     = 14
RAPID_ACCESS_MINS  = 5

def check_failed_attempts(logs_df):
    anomalies = []
    if logs_df.empty: return anomalies
    denied = logs_df[logs_df['status'] == 'DENIED']
    if denied.empty: return anomalies
    counts = denied.groupby(['name','date']).size().reset_index(name='count')
    for _, row in counts.iterrows():
        if row['count'] >= MAX_FAILED_PER_DAY:
            anomalies.append({'rule':'Rule 1','type':'Multiple Failed Attempts',
                              'name':row['name'],'date':row['date'],
                              'detail':f"{row['count']} failed attempts",'risk':'HIGH'})
    return anomalies

def check_unusual_hours(logs_df):
    anomalies = []
    if logs_df.empty: return anomalies
    granted = logs_df[logs_df['status'] == 'GRANTED']
    for _, row in granted.iterrows():
        try:
            hour = int(row['time'].split(':')[0])
            if hour >= UNUSUAL_HOUR_START or hour < UNUSUAL_HOUR_END:
                anomalies.append({'rule':'Rule 2','type':'Unusual Login Time',
                                  'name':row['name'],'date':row['date'],
                                  'detail':f"Login at {row['time']}",'risk':'MEDIUM'})
        except: continue
    return anomalies

def check_working_hours(attendance_df):
    anomalies = []
    if attendance_df.empty: return anomalies
    for _, row in attendance_df.iterrows():
        try:
            hours = float(row['hours_worked'])
            if 0 < hours < MIN_WORK_HOURS:
                anomalies.append({'rule':'Rule 3','type':'Short Working Hours',
                                  'name':row['name'],'date':row['date'],
                                  'detail':f"Only {hours} hours",'risk':'LOW'})
            if hours > MAX_WORK_HOURS:
                anomalies.append({'rule':'Rule 4','type':'Excessive Working Hours',
                                  'name':row['name'],'date':row['date'],
                                  'detail':f"{hours} hours worked",'risk':'MEDIUM'})
        except: continue
    return anomalies

def check_rapid_access(logs_df):
    anomalies = []
    if logs_df.empty: return anomalies
    granted = logs_df[logs_df['status'] == 'GRANTED'].copy()
    if granted.empty: return anomalies
    for name in granted['name'].unique():
        person    = granted[granted['name'] == name].copy()
        if len(person) < 2: continue
        person    = person.sort_values(['date','time'])
        prev_time = None
        prev_date = None
        for _, row in person.iterrows():
            try:
                curr_dt = datetime.datetime.strptime(
                    f"{row['date']} {row['time']}", '%Y-%m-%d %H:%M:%S')
                if prev_time and prev_date == row['date']:
                    diff = (curr_dt - prev_time).seconds / 60
                    if diff < RAPID_ACCESS_MINS:
                        anomalies.append({'rule':'Rule 5','type':'Rapid Multiple Access',
                                          'name':name,'date':row['date'],
                                          'detail':f"2 access in {diff:.1f} mins",'risk':'HIGH'})
                prev_time = curr_dt
                prev_date = row['date']
            except: continue
    return anomalies

def detect_anomalies():
    print(f"\n{'='*45}")
    print("  ANOMALY DETECTION RUNNING...")
    print(f"{'='*45}\n")

    all_anomalies = []

    logs_df = pd.DataFrame()
    if os.path.exists(LOGS_FILE):
        logs_df = pd.read_csv(LOGS_FILE)
        print(f"✅ Loaded {len(logs_df)} access log records")
    else:
        print("⚠️  No access logs found!")

    attendance_df = pd.DataFrame()
    if os.path.exists(ATTENDANCE_FILE):
        attendance_df = pd.read_csv(ATTENDANCE_FILE)
        attendance_df['hours_worked'] = pd.to_numeric(
            attendance_df['hours_worked'], errors='coerce').fillna(0)
        print(f"✅ Loaded {len(attendance_df)} attendance records")

    all_anomalies.extend(check_failed_attempts(logs_df))
    all_anomalies.extend(check_unusual_hours(logs_df))
    all_anomalies.extend(check_working_hours(attendance_df))
    all_anomalies.extend(check_rapid_access(logs_df))

    if all_anomalies:
        df = pd.DataFrame(all_anomalies)
        df.to_csv(ANOMALY_FILE, index=False)
        print(f"\n🚨 Total Anomalies: {len(all_anomalies)}")
    else:
        print("\n✅ NO ANOMALIES DETECTED!")

    return all_anomalies

def view_anomaly_report():
    if not os.path.exists(ANOMALY_FILE):
        print("\n❌ No anomaly report! Run detection first.")
        return
    df = pd.read_csv(ANOMALY_FILE)
    if df.empty:
        print("\n✅ No anomalies found!")
        return
    high   = len(df[df['risk']=='HIGH'])
    medium = len(df[df['risk']=='MEDIUM'])
    low    = len(df[df['risk']=='LOW'])
    print(f"\nTotal: {len(df)} | 🔴 High: {high} | 🟡 Med: {medium} | 🟢 Low: {low}\n")
    for _, row in df.iterrows():
        print(f"  {row['rule']} | {row['type']} | {row['name']} | {row['risk']}")

def plot_anomaly_chart():
    if not os.path.exists(ANOMALY_FILE):
        print("\n❌ No anomaly report! Run detection first.")
        return

    df = pd.read_csv(ANOMALY_FILE)
    if df.empty:
        print("\n✅ No anomalies to plot!")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors_risk = {'HIGH':'#FF4444','MEDIUM':'#FF9800','LOW':'#4CAF50'}

    type_counts = df['type'].value_counts()
    bars = ax1.barh(type_counts.index, type_counts.values,
                   color=['#FF4444','#FF9800','#2196F3','#9C27B0','#4CAF50'])
    for bar, val in zip(bars, type_counts.values):
        ax1.text(bar.get_width() + 0.1,
                bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=10)
    ax1.set_title('Anomaly Types Detected', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Count')

    risk_counts = df['risk'].value_counts()
    risk_colors = [colors_risk.get(r, '#888888') for r in risk_counts.index]
    ax2.pie(risk_counts.values, labels=risk_counts.index,
            colors=risk_colors, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Risk Level Distribution', fontsize=13, fontweight='bold')

    plt.suptitle('Anomaly Detection Report', fontsize=15, fontweight='bold')
    plt.tight_layout()

    chart_path = REPORTS_PATH + 'anomaly_chart.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()   # FIX: close, no plt.show()
    print(f"✅ Chart saved: {chart_path}")

def add_demo_anomaly_data():
    demo_logs = [
        ['2026-04-28','09:15:00','Unknown','DENIED','Morning','Attempt 1/3'],
        ['2026-04-28','09:16:00','Unknown','DENIED','Morning','Attempt 2/3'],
        ['2026-04-28','09:17:00','Unknown','DENIED','Morning','Attempt 3/3'],
        ['2026-04-28','09:18:00','Unknown','SECURITY_ALERT','Morning','3 failed attempts'],
        ['2026-04-29','02:30:00','Ahmed','GRANTED','Night','Authorized user'],
        ['2026-04-29','23:45:00','Sara','GRANTED','Night','Authorized user'],
        ['2026-04-30','10:00:00','Ali','GRANTED','Morning','Authorized user'],
        ['2026-04-30','10:02:00','Ali','GRANTED','Morning','Authorized user'],
    ]
    file_exists = os.path.exists(LOGS_FILE)
    with open(LOGS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['date','time','name','status','time_of_day','reason'])
        writer.writerows(demo_logs)

    demo_att = [
        ['Ahmed','2026-04-28','09:00:00','10:30:00','1.5','PRESENT'],
        ['Sara', '2026-04-29','08:00:00','23:30:00','15.5','PRESENT'],
    ]
    att_exists = os.path.exists(ATTENDANCE_FILE)
    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not att_exists:
            writer.writerow(['name','date','entry_time','exit_time','hours_worked','status'])
        writer.writerows(demo_att)

    print("✅ Demo anomaly data added! Now run detection.")

if __name__ == "__main__":
    while True:
        print("\n1. Detect  2. View  3. Chart  4. Demo  5. Exit")
        c = input("Choice: ")
        if c == "1": detect_anomalies()
        elif c == "2": view_anomaly_report()
        elif c == "3": plot_anomaly_chart(); print("Chart saved to reports/")
        elif c == "4": add_demo_anomaly_data()
        elif c == "5": break
        else: print("❌ Invalid")