# Face Recognition Based Intelligent Access Control System with Attendance and Anomaly Analysis

A Final Year Project that uses face recognition for secure access control, combined with automated attendance tracking, salary calculation, and anomaly detection. Built as part of the BSIT program (Session 2021–2025) at GC University Faisalabad.

## Overview

This system replaces manual entry logging with a face-recognition-based access control pipeline. It verifies identity using deep learning, checks for liveness to prevent spoofing attempts (e.g. photo or video replay), logs attendance automatically, calculates salary based on attendance records, and flags anomalies in access patterns for review.

## Features

- Face recognition-based identity verification using DeepFace (VGG-Face model)
- Liveness detection via challenge-response head movement, to prevent spoofing
- Automated attendance logging tied to successful access events
- Salary calculation module based on attendance data
- Anomaly detection and analysis on access logs
- Desktop GUI built with Tkinter for ease of use
- Visual reports and charts generated with Matplotlib

## Tech Stack

- **Language:** Python 3.10
- **Computer Vision:** OpenCV
- **Face Recognition:** DeepFace (VGG-Face model)
- **GUI:** Tkinter
- **Data Handling:** Pandas, CSV
- **Visualization:** Matplotlib

> Note: Python 3.10 is required — DeepFace's dependencies are not compatible with newer Python versions (e.g. 3.13).

## Project Structure

```
FYP_Project/
├── gui.py                    # Main GUI application (entry point for end users)
├── main.py                   # Core application logic
├── module1_iris.py           # Module 1 component
├── module2_access.py         # Face recognition-based access control logic
├── module3_attendance.py     # Attendance tracking and logging
├── module4_salary.py         # Salary calculation based on attendance
├── module5_anomaly.py        # Anomaly detection and analysis
├── database/
│   ├── users.csv             # Registered user records
│   ├── access_logs.csv       # Access control event logs
│   └── attendance.csv        # Attendance records
├── docs/
│   └── FYP_Documentation.pdf # Full project documentation/report
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Ensure you're using **Python 3.10** (create a virtual environment if needed):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install opencv-python deepface pandas matplotlib
   ```

## Usage

Run the application from the project root:

```
python gui.py
```

This launches the main GUI, from which all modules (access control, attendance, salary, anomaly analysis) can be accessed.

## How It Works

- Each access attempt is verified against registered faces in the database using DeepFace's VGG-Face model.
- Liveness is confirmed through a challenge-response check requiring head movement, preventing spoofing via static images.
- Recognition checks run every 30 frames to balance accuracy and performance.
- Successful access events automatically update the attendance log.
- The anomaly module periodically reviews access and attendance logs to flag irregular patterns.

## Documentation

Full project documentation, including system design, methodology, and results, is available at `docs/FYP_Documentation.pdf`.

## Data Note

The CSV files included under `database/` contain sample/dummy data for demonstration purposes only.

## Contributors

- Fizza Arooj Anwer
- Ghulam Fatima

## Supervisor

Prof. DR. Rabia Saleem
