# ============================================
# Module 4 - Salary Estimation
# Student: Fizza Arooj
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
ATTENDANCE_FILE = DATABASE_PATH + 'attendance.csv'
SALARY_FILE     = REPORTS_PATH  + 'salary_report.csv'

os.makedirs(DATABASE_PATH, exist_ok=True)
os.makedirs(REPORTS_PATH,  exist_ok=True)

DEFAULT_RATE = 150
HOURLY_RATES = {
    'Fizza':  200,
    'Ahmed':  150,
    'Sara':   180,
    'Ali':    160,
    'Ayesha': 170,
}

def get_rate(name):
    return HOURLY_RATES.get(name, DEFAULT_RATE)

def calculate_salary(name, total_hours):
    rate   = get_rate(name)
    salary = round(total_hours * rate, 2)
    return salary, rate

def generate_salary_report():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance records!")
        return None

    df = pd.read_csv(ATTENDANCE_FILE)
    df['hours_worked'] = pd.to_numeric(df['hours_worked'], errors='coerce').fillna(0)

    summary = df.groupby('name').agg(
        days_present=('date', 'count'),
        total_hours=('hours_worked', 'sum')
    ).reset_index()
    summary['total_hours'] = summary['total_hours'].round(2)

    salaries, rates = [], []
    for _, row in summary.iterrows():
        sal, rate = calculate_salary(row['name'], row['total_hours'])
        salaries.append(sal)
        rates.append(rate)

    summary['hourly_rate']  = rates
    summary['total_salary'] = salaries
    summary.to_csv(SALARY_FILE, index=False)

    print(f"\n{'='*65}")
    print("  SALARY ESTIMATION REPORT")
    print(f"{'='*65}")
    print(f"{'Name':<15} {'Days':<8} {'Hours':<10} {'Rate/Hr':<12} {'Salary (Rs.)':<15}")
    print("-"*65)
    total_payroll = 0
    for _, row in summary.iterrows():
        print(f"{row['name']:<15} {row['days_present']:<8} {row['total_hours']:<10} "
              f"Rs.{row['hourly_rate']:<10} Rs.{row['total_salary']:<15}")
        total_payroll += row['total_salary']
    print(f"{'='*65}")
    print(f"  Total Payroll: Rs. {round(total_payroll, 2)}")
    print(f"{'='*65}\n")
    return summary

def view_salary_report():
    if not os.path.exists(SALARY_FILE):
        print("\n❌ No salary report found! Generate first.")
        return
    df = pd.read_csv(SALARY_FILE)
    total = 0
    for _, row in df.iterrows():
        print(f"{row['name']:<15} Rs.{row['total_salary']}")
        total += row['total_salary']
    print(f"Total: Rs.{round(total,2)}\n")

def plot_salary():
    if not os.path.exists(SALARY_FILE):
        print("\n❌ No salary report! Generate first.")
        return

    df = pd.read_csv(SALARY_FILE)
    if df.empty:
        print("❌ No data!")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    colors = ['#2196F3','#4CAF50','#FF9800','#E91E63','#9C27B0']

    bars = ax1.bar(df['name'], df['total_salary'], color=colors[:len(df)])
    for bar, val in zip(bars, df['total_salary']):
        ax1.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 10, f'Rs.{val:.0f}',
                ha='center', fontsize=9)
    ax1.set_title('Salary Per Employee', fontsize=13, fontweight='bold')
    ax1.set_xlabel('Employee')
    ax1.set_ylabel('Salary (Rs.)')

    ax2.pie(df['total_salary'], labels=df['name'],
            autopct='%1.1f%%', colors=colors[:len(df)])
    ax2.set_title('Salary Distribution', fontsize=13, fontweight='bold')

    plt.suptitle('Salary Estimation Report', fontsize=15, fontweight='bold')
    plt.tight_layout()

    chart_path = REPORTS_PATH + 'salary_chart.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()   # FIX: close, no plt.show()
    print(f"✅ Chart saved: {chart_path}")

def salary_summary():
    if not os.path.exists(ATTENDANCE_FILE):
        print("\n❌ No attendance data!")
        return
    df = pd.read_csv(ATTENDANCE_FILE)
    df['hours_worked'] = pd.to_numeric(df['hours_worked'], errors='coerce').fillna(0)
    total_payroll = 0
    for name in df['name'].unique():
        hrs    = round(df[df['name']==name]['hours_worked'].sum(), 2)
        rate   = get_rate(name)
        salary = round(hrs * rate, 2)
        total_payroll += salary
        print(f"  {name}: {hrs}hrs × Rs.{rate} = Rs.{salary}")
    print(f"  TOTAL: Rs.{round(total_payroll,2)}\n")

def set_hourly_rate():
    name = input("Enter employee name: ")
    rate = input(f"Enter hourly rate for {name}: Rs.")
    try:
        HOURLY_RATES[name] = int(rate)
        print(f"✅ {name} = Rs.{rate}/hr")
    except:
        print("❌ Invalid rate!")

if __name__ == "__main__":
    while True:
        print("\n1. Generate  2. View  3. Chart  4. Summary  5. Rate  6. Exit")
        c = input("Choice: ")
        if c == "1": generate_salary_report()
        elif c == "2": view_salary_report()
        elif c == "3": plot_salary(); print("Chart saved to reports/")
        elif c == "4": salary_summary()
        elif c == "5": set_hourly_rate()
        elif c == "6": break
        else: print("❌ Invalid")