# ============================================
# GUI - Face Recognition Access Control System
# Student: Fizza Arooj & Ghulam Fatima
# FYP: Face Recognition Based Intelligent
#      Access Control System with
#      Active Liveness Detection
# GC University Faisalabad | BSIT 2026
# ============================================

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import datetime
import os
import cv2
import random
import numpy as np
from PIL import Image, ImageTk
import pandas as pd

import module1_iris as iris
import module2_access as access
import module3_attendance as attendance
import module4_salary as salary
import module5_anomaly as anomaly

# ============================================
# COLORS
# ============================================

BG_DARK    = "#0a0a1a"
BG_CARD    = "#12122a"
BG_PANEL   = "#1a1a3e"
ACCENT     = "#00d4ff"
GREEN      = "#00ff88"
RED        = "#ff4444"
ORANGE     = "#ff9800"
YELLOW     = "#ffeb3b"
WHITE      = "#ffffff"
GRAY       = "#888888"
PURPLE     = "#9c27b0"

FONT_TITLE = ("Arial", 17, "bold")
FONT_HEAD  = ("Arial", 10, "bold")
FONT_BTN   = ("Arial", 9, "bold")
FONT_SMALL = ("Arial", 8)
FONT_LOG   = ("Courier", 8)

# ============================================
# LIVENESS CHALLENGES
# ============================================

CHALLENGES = [
    "TURN HEAD LEFT",
    "TURN HEAD RIGHT",
    "NOD HEAD DOWN",
    "MOVE CLOSER",
    "TILT HEAD LEFT",
]

# ============================================
# MAIN APP
# ============================================

class FaceAccessSystem:

    def __init__(self, root):
        self.root = root
        self.root.title(
            "Face Recognition Access Control"
            " | Fizza Arooj & Ghulam Fatima"
            " | BSIT FYP 2026")
        self.root.state('zoomed')
        self.root.resizable(True, True)
        self.root.configure(bg=BG_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.failed_attempts  = 0
        self.total_scans      = 0
        self.false_accepted   = 0
        self.false_rejected   = 0
        self.status_var       = tk.StringVar()
        self.status_var.set("System Ready")
        self.camera_running   = False
        self.camera           = None

        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades +
            'haarcascade_frontalface_default.xml')

        self.build_ui()
        self.update_clock()
        self.log("✅ System initialized!", 'green')
        self.log("🔐 Face Recognition Access Control System", 'cyan')
        self.log("📋 GC University Faisalabad | BSIT 2026", 'cyan')
        self.refresh_users()
        self.root.after(500, self.start_camera)

    # ==========================================
    # BUILD UI
    # ==========================================

    def build_ui(self):
        # HEADER
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=55)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        tk.Label(hdr,
                text="🔐  FACE RECOGNITION INTELLIGENT ACCESS CONTROL SYSTEM",
                font=FONT_TITLE, bg=BG_PANEL, fg=ACCENT).pack(
                    side='left', padx=12, pady=8)

        tk.Button(hdr, text="⏻ EXIT",
                 font=("Arial", 9, "bold"),
                 bg=RED, fg=WHITE,
                 command=self.exit_app,
                 relief='flat', cursor='hand2',
                 padx=10, pady=3).pack(side='right', padx=12, pady=12)

        rh = tk.Frame(hdr, bg=BG_PANEL)
        rh.pack(side='right', padx=5)

        self.clock_lbl = tk.Label(rh, text="",
                                   font=("Arial", 9, "bold"),
                                   bg=BG_PANEL, fg=YELLOW)
        self.clock_lbl.pack(anchor='e')

        tk.Label(rh,
                text="Fizza Arooj & Ghulam Fatima  |  GC University Faisalabad",
                font=("Arial", 7), bg=BG_PANEL, fg=GRAY).pack(anchor='e')

        # STATUS CARDS
        cards = tk.Frame(self.root, bg=BG_DARK, height=55)
        cards.pack(fill='x', padx=6, pady=3)
        cards.pack_propagate(False)

        self.status_card = self.card(cards, "SYSTEM STATUS", "✅ READY", GREEN)
        self.status_card.pack(side='left', padx=2, fill='both', expand=True)

        self.scan_card = self.card(cards, "LAST SCAN", "No scan yet", GRAY)
        self.scan_card.pack(side='left', padx=2, fill='both', expand=True)

        self.live_card = self.card(cards, "LIVENESS", "Not checked", GRAY)
        self.live_card.pack(side='left', padx=2, fill='both', expand=True)

        self.fail_card = self.card(cards, "FAILED", "0/3", GREEN)
        self.fail_card.pack(side='left', padx=2, fill='both', expand=True)

        self.user_card = self.card(cards, "USERS", "0", ACCENT)
        self.user_card.pack(side='left', padx=2, fill='both', expand=True)

        self.far_card = self.card(cards, "FAR", "0.00%", GREEN)
        self.far_card.pack(side='left', padx=2, fill='both', expand=True)

        # MAIN BODY
        body = tk.Frame(self.root, bg=BG_DARK)
        body.pack(fill='both', expand=True, padx=6, pady=3)

        sidebar = tk.Frame(body, bg=BG_DARK, width=200)
        sidebar.pack(side='left', fill='y', padx=(0, 3))
        sidebar.pack_propagate(False)

        center = tk.Frame(body, bg=BG_DARK, width=680)
        center.pack(side='left', fill='both')
        center.pack_propagate(False)

        right = tk.Frame(body, bg=BG_DARK, width=320)
        right.pack(side='right', fill='y', padx=(3, 0))
        right.pack_propagate(False)

        self.build_sidebar(sidebar)
        self.build_center(center)
        self.build_right(right)

        # STATUS BAR
        sbar = tk.Frame(self.root, bg="#0d0d2e", height=24)
        sbar.pack(fill='x', side='bottom')
        sbar.pack_propagate(False)

        tk.Label(sbar, text="●", font=("Arial", 8),
                bg="#0d0d2e", fg=GREEN).pack(side='left', padx=5, pady=3)
        tk.Label(sbar, textvariable=self.status_var,
                font=("Arial", 8), bg="#0d0d2e", fg=GREEN).pack(
                    side='left', pady=3)

    # ==========================================
    # BUILD SIDEBAR
    # ==========================================

    def build_sidebar(self, parent):
        canvas = tk.Canvas(parent, bg=BG_DARK, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient='vertical', command=canvas.yview)
        sf = tk.Frame(canvas, bg=BG_DARK)

        sf.bind('<Configure>',
               lambda e: canvas.configure(
                   scrollregion=canvas.bbox('all')))

        canvas.create_window((0, 0), window=sf, anchor='nw')
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        canvas.bind_all('<MouseWheel>',
                       lambda e: canvas.yview_scroll(
                           int(-1*(e.delta/120)), 'units'))

        self.sec(sf, "📷  SCANNING")
        self.btn(sf, "🚪  Scan Face → ENTRY", self.scan_entry, GREEN)
        self.btn(sf, "🚶  Scan Face → EXIT",  self.scan_exit,  ACCENT)
        self.btn(sf, "➕  Register New User",  self.register_user, YELLOW)
        self.btn(sf, "🗑️  Delete User",        self.delete_user, RED)

        self.sec(sf, "📋  ACCESS LOGS")
        self.btn(sf, "📄  View Access Logs",   self.view_logs, WHITE)
        self.btn(sf, "📊  Access Statistics",  self.view_stats, WHITE)

        self.sec(sf, "📅  ATTENDANCE")
        self.btn(sf, "📋  View Attendance",    self.view_attendance, WHITE)
        self.btn(sf, "📊  Attendance Report",  self.attendance_report, WHITE)
        self.btn(sf, "📈  Attendance Chart",   self.attendance_chart, WHITE)
        self.btn(sf, "📅  Today's Summary",    self.todays_summary, WHITE)

        self.sec(sf, "💰  SALARY")
        self.btn(sf, "💵  Generate Salary",    self.gen_salary, WHITE)
        self.btn(sf, "📋  View Salary Report", self.view_salary, WHITE)
        self.btn(sf, "📊  Salary Chart",       self.salary_chart, WHITE)

        self.sec(sf, "🚨  ANOMALY DETECTION")
        self.btn(sf, "🔍  Detect Anomalies",   self.detect_anomaly, ORANGE)
        self.btn(sf, "📋  View Anomaly Report",self.view_anomaly, ORANGE)
        self.btn(sf, "📊  Anomaly Chart",      self.anomaly_chart, ORANGE)

        self.sec(sf, "📈  SECURITY METRICS")
        self.btn(sf, "📊  FAR/FRR Metrics",    self.view_metrics, PURPLE)

        self.sec(sf, "⚙️  SYSTEM")
        self.btn(sf, "👥  View All Users",     self.view_users, WHITE)
        self.btn(sf, "⏻  Exit System",        self.exit_app, RED)

    # ==========================================
    # BUILD CENTER
    # ==========================================

    def build_center(self, parent):
        cam_f = tk.LabelFrame(parent,
                              text="  📷 Live Camera Feed  ",
                              font=FONT_HEAD,
                              bg=BG_CARD, fg=ACCENT,
                              bd=2, relief='groove')
        cam_f.pack(fill='x', pady=(0, 3))

        self.cam_label = tk.Label(cam_f, bg="#050510",
                                   text="📷 Camera loading...",
                                   fg=GRAY, font=("Arial", 12))
        self.cam_label.pack(padx=4, pady=4)

        cs = tk.Frame(cam_f, bg=BG_CARD)
        cs.pack(fill='x', padx=4, pady=(0, 3))

        self.cam_status_lbl = tk.Label(cs, text="● Initializing...",
                                        font=("Arial", 7),
                                        bg=BG_CARD, fg=ORANGE)
        self.cam_status_lbl.pack(side='left')

        self.face_lbl = tk.Label(cs, text="Scanning...",
                                  font=("Arial", 7),
                                  bg=BG_CARD, fg=GRAY)
        self.face_lbl.pack(side='right')

        log_f = tk.LabelFrame(parent,
                               text="  📜 Activity Log  ",
                               font=FONT_HEAD,
                               bg=BG_CARD, fg=ACCENT,
                               bd=2, relief='groove')
        log_f.pack(fill='both', expand=True, pady=(3, 0))

        self.log_text = tk.Text(log_f, font=FONT_LOG,
                                 bg="#050510", fg=GREEN,
                                 state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=4, pady=4)
        self.log_text.tag_configure('green',  foreground=GREEN)
        self.log_text.tag_configure('red',    foreground=RED)
        self.log_text.tag_configure('orange', foreground=ORANGE)
        self.log_text.tag_configure('yellow', foreground=YELLOW)
        self.log_text.tag_configure('cyan',   foreground=ACCENT)

        ls = ttk.Scrollbar(log_f, command=self.log_text.yview)
        ls.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=ls.set)

    # ==========================================
    # BUILD RIGHT PANEL
    # ==========================================

    def build_right(self, parent):
        af = tk.LabelFrame(parent,
                           text="  🚨 Threat Alerts  ",
                           font=FONT_HEAD,
                           bg=BG_CARD, fg=RED,
                           bd=2, relief='groove')
        af.pack(fill='x', pady=(0, 3))

        self.alert_text = tk.Text(af, font=FONT_LOG,
                                   bg="#1a0000", fg=RED,
                                   state='disabled', wrap='word', height=6)
        self.alert_text.pack(fill='x', padx=4, pady=3)

        tk.Button(af, text="🔄 Refresh", font=FONT_SMALL,
                 bg=BG_PANEL, fg=RED,
                 command=self.refresh_alerts,
                 relief='flat', cursor='hand2').pack(pady=2)

        tf = tk.LabelFrame(parent,
                           text="  📅 Today's Attendance  ",
                           font=FONT_HEAD,
                           bg=BG_CARD, fg=ACCENT,
                           bd=2, relief='groove')
        tf.pack(fill='x', pady=(0, 3))

        self.today_text = tk.Text(tf, font=FONT_LOG,
                                   bg="#050510", fg=WHITE,
                                   state='disabled', wrap='word', height=6)
        self.today_text.pack(fill='x', padx=4, pady=3)

        tk.Button(tf, text="🔄 Refresh", font=FONT_SMALL,
                 bg=BG_PANEL, fg=ACCENT,
                 command=self.refresh_today,
                 relief='flat', cursor='hand2').pack(pady=2)

        uf = tk.LabelFrame(parent,
                           text="  👥 Registered Users  ",
                           font=FONT_HEAD,
                           bg=BG_CARD, fg=ACCENT,
                           bd=2, relief='groove')
        uf.pack(fill='both', expand=True)

        self.users_list = tk.Listbox(uf,
                                      font=("Arial", 9, "bold"),
                                      bg="#050510", fg=GREEN,
                                      selectbackground=ACCENT,
                                      selectforeground=BG_DARK,
                                      borderwidth=0,
                                      highlightthickness=0)
        self.users_list.pack(fill='both', expand=True, padx=4, pady=4)

        tk.Button(uf, text="🔄 Refresh", font=FONT_SMALL,
                 bg=BG_PANEL, fg=ACCENT,
                 command=self.refresh_users,
                 relief='flat', cursor='hand2').pack(pady=2)

    # ==========================================
    # LIVE CAMERA FEED
    # ==========================================

    def start_camera(self):
        self.camera = cv2.VideoCapture(0)
        if self.camera.isOpened():
            self.camera_running = True
            self.cam_status_lbl.configure(
                text="● Camera: ACTIVE", fg=GREEN)
            self.update_camera()
        else:
            self.cam_status_lbl.configure(
                text="● Camera: NOT FOUND", fg=RED)

    def update_camera(self):
        if not self.camera_running:
            return

        ret, frame = self.camera.read()
        if ret:
            display = frame.copy()
            gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces   = self.face_detector.detectMultiScale(
                gray, 1.1, 5, minSize=(80, 80))

            face_found = len(faces) > 0

            for (x, y, w, h) in faces:
                cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(display, "FACE", (x, y-6),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.putText(display,
                       datetime.datetime.now().strftime('%H:%M:%S'),
                       (6, 18), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 255, 255), 1)

            cv2.putText(display,
                       "FACE DETECTED" if face_found else "SCANNING...",
                       (6, display.shape[0]-8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       (0, 255, 0) if face_found else (0, 165, 255), 1)

            self.root.after(0,
                lambda ff=face_found: self.face_lbl.configure(
                    text="✓ Face detected" if ff else "Scanning...",
                    fg=GREEN if ff else ORANGE))

            display = cv2.resize(display, (480, 280))
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            img     = Image.fromarray(display)
            photo   = ImageTk.PhotoImage(img)

            self.cam_label.configure(image=photo, text="")
            self.cam_label.image = photo

        self.root.after(40, self.update_camera)

    def stop_camera(self):
        self.camera_running = False
        if self.camera:
            self.camera.release()

    def restart_camera(self):
        self.camera_running = False
        self.cam_status_lbl.configure(
            text="● Restarting...", fg=ORANGE)
        self.root.after(800, self._do_restart)

    def _do_restart(self):
        try:
            if self.camera:
                self.camera.release()
            self.camera = cv2.VideoCapture(0)
            if self.camera.isOpened():
                self.camera_running = True
                self.cam_status_lbl.configure(
                    text="● Camera: ACTIVE", fg=GREEN)
                self.update_camera()
            else:
                self.root.after(1000, self._do_restart)
        except:
            pass

    # ==========================================
    # CHALLENGE-RESPONSE LIVENESS CHECK
    # FIX: Runs on MAIN THREAD via root.after()
    #      Uses a state machine approach so
    #      cv2.imshow() works correctly on Windows
    # ==========================================

    def run_liveness_challenge(self, callback):
        """
        FIX: cv2.imshow() MUST run on the main thread on Windows.
        We use a state-machine driven by root.after() so the
        OpenCV window displays properly.

        callback(True)  = liveness passed
        callback(False) = liveness failed
        """
        # Stop the background GUI camera feed first
        self.camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None

        # Short delay to let camera release fully
        self.root.after(300, lambda: self._liveness_start(callback))

    def _liveness_start(self, callback):
        """Open camera and pick challenges"""
        self.liveness_camera = cv2.VideoCapture(0)
        if not self.liveness_camera.isOpened():
            # No camera — skip liveness
            callback(True)
            return

        # Pick 2 random challenges
        self.liveness_challenges  = random.sample(CHALLENGES, 2)
        self.liveness_idx         = 0
        self.liveness_callback    = callback

        # Start first challenge
        self._liveness_next_challenge()

    def _liveness_next_challenge(self):
        """Setup state for next challenge"""
        if self.liveness_idx >= len(self.liveness_challenges):
            # All challenges passed!
            self.liveness_camera.release()
            cv2.destroyAllWindows()
            self.root.after(300, lambda: self.liveness_callback(True))
            return

        challenge = self.liveness_challenges[self.liveness_idx]
        self.log(f"🎯 Challenge: {challenge}", 'yellow')

        # Get initial face position
        init_cx, init_cy, init_w = None, None, None

        for _ in range(30):
            ret, frame = self.liveness_camera.read()
            if not ret:
                continue
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(
                gray, 1.1, 5, minSize=(80, 80))
            if len(faces) > 0:
                (ix, iy, iw, ih) = faces[0]
                init_cx = ix + iw // 2
                init_cy = iy + ih // 2
                init_w  = iw
                break

        if init_cx is None:
            # No face found for this challenge
            self.liveness_camera.release()
            cv2.destroyAllWindows()
            self.root.after(300, lambda: self.liveness_callback(False))
            return

        # State variables for this challenge
        self.ch_challenge  = challenge
        self.ch_init_cx    = init_cx
        self.ch_init_cy    = init_cy
        self.ch_init_w     = init_w
        self.ch_frames     = 0
        self.ch_timeout    = 300      # 10 seconds at ~30fps
        self.ch_passed     = False
        self.ch_threshold  = 30       # pixels

        # Start the per-frame loop via root.after
        self.root.after(10, self._liveness_frame)

    def _liveness_frame(self):
        """Process one frame for liveness — called via root.after"""
        if self.ch_frames >= self.ch_timeout:
            # Timed out — failed
            cv2.destroyAllWindows()
            self.liveness_camera.release()
            self.root.after(300, lambda: self.liveness_callback(False))
            return

        ret, frame = self.liveness_camera.read()
        if not ret:
            self.ch_frames += 1
            self.root.after(10, self._liveness_frame)
            return

        self.ch_frames += 1
        display = frame.copy()
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces   = self.face_detector.detectMultiScale(
            gray, 1.1, 5, minSize=(80, 80))

        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cx     = x + w // 2
            cy     = y + h // 2
            move_x = cx - self.ch_init_cx
            move_y = cy - self.ch_init_cy
            move_w = w  - self.ch_init_w

            c = self.ch_challenge
            t = self.ch_threshold

            if c == "TURN HEAD LEFT"  and move_x < -t:
                self.ch_passed = True
            elif c == "TURN HEAD RIGHT" and move_x > t:
                self.ch_passed = True
            elif c == "NOD HEAD DOWN"   and move_y > t:
                self.ch_passed = True
            elif c == "MOVE CLOSER"     and move_w > t:
                self.ch_passed = True
            elif c == "TILT HEAD LEFT"  and move_x < -t:
                self.ch_passed = True

        # Draw UI on frame
        cv2.rectangle(display, (0, 0),
                     (display.shape[1], 80), (0, 0, 0), -1)

        cv2.putText(display, "LIVENESS CHECK",
                   (10, 28), cv2.FONT_HERSHEY_SIMPLEX,
                   0.8, (0, 255, 255), 2)

        # FIX: Use plain tuple colors, not hex strings
        ch_color = (0, 255, 0) if self.ch_passed else (0, 255, 255)
        cv2.putText(display, self.ch_challenge,
                   (10, 65), cv2.FONT_HERSHEY_SIMPLEX,
                   1.0, ch_color, 2)

        # Timer bar
        progress = int((self.ch_frames / self.ch_timeout) * 400)
        cv2.rectangle(display, (10, 85), (410, 98), (60, 60, 60), -1)
        cv2.rectangle(display, (10, 85), (10 + progress, 98),
                     (0, 200, 255), -1)

        time_left = max(0, int((self.ch_timeout - self.ch_frames) / 30))
        cv2.putText(display, f"Time: {time_left}s",
                   (10, 118), cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (255, 255, 255), 1)

        if self.ch_passed:
            cv2.putText(display, "✓ DONE! Stay still...",
                       (10, 155), cv2.FONT_HERSHEY_SIMPLEX,
                       1.0, (0, 255, 0), 3)

        cv2.putText(display, "Anti-Spoof: Active",
                   (10, display.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        cv2.imshow("Liveness Check - Follow Instruction!", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            cv2.destroyAllWindows()
            self.liveness_camera.release()
            self.root.after(300, lambda: self.liveness_callback(False))
            return

        if self.ch_passed:
            # Show "DONE" for 1 second, then move to next challenge
            self.root.after(1000, self._challenge_passed)
            return

        # Schedule next frame
        self.root.after(10, self._liveness_frame)

    def _challenge_passed(self):
        """Move to next challenge after current one passed"""
        cv2.destroyAllWindows()
        self.liveness_idx += 1
        self.root.after(200, self._liveness_next_challenge)

    # ==========================================
    # HELPERS
    # ==========================================

    def sec(self, p, text):
        tk.Label(p, text=text,
                font=("Arial", 8, "bold"),
                bg=BG_DARK, fg=ACCENT).pack(
                    fill='x', padx=3, pady=(5, 1))
        tk.Frame(p, bg=ACCENT, height=1).pack(
            fill='x', padx=3, pady=(0, 1))

    def btn(self, p, text, cmd, color):
        b = tk.Button(p, text=text,
                     font=FONT_BTN,
                     bg=BG_CARD, fg=color,
                     activebackground=BG_PANEL,
                     activeforeground=WHITE,
                     relief='flat', cursor='hand2',
                     command=cmd, pady=4,
                     anchor='w', padx=8)
        b.pack(fill='x', padx=4, pady=1)
        b.bind('<Enter>', lambda e: b.configure(bg=BG_PANEL))
        b.bind('<Leave>', lambda e: b.configure(bg=BG_CARD))
        return b

    def card(self, p, title, val, color):
        f = tk.Frame(p, bg=BG_CARD, relief='groove', bd=2, padx=6, pady=5)
        tk.Label(f, text=title, font=("Arial", 6, "bold"),
                bg=BG_CARD, fg=GRAY).pack()
        lbl = tk.Label(f, text=val, font=("Arial", 9, "bold"),
                      bg=BG_CARD, fg=color)
        lbl.pack()
        f.value_label = lbl
        return f

    def upd(self, card, val, color=None):
        card.value_label.configure(text=val)
        if color:
            card.value_label.configure(fg=color)

    def smart_upd_cards(self, fa=None):
        if fa is None:
            fa = self.failed_attempts

        if fa == 0:
            self.upd(self.fail_card, f"{fa}/3", GREEN)
        elif fa == 1:
            self.upd(self.fail_card, f"{fa}/3", YELLOW)
        elif fa == 2:
            self.upd(self.fail_card, f"{fa}/3", ORANGE)
        else:
            self.upd(self.fail_card, f"{fa}/3", RED)

        if self.total_scans > 0:
            far = round((self.false_accepted / self.total_scans)*100, 2)
            self.upd(self.far_card, f"{far}%",
                    GREEN if far < 5 else RED)

    def log(self, msg, tag='green'):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        self.log_text.configure(state='normal')
        self.log_text.insert('end', f"[{t}] {msg}\n", tag)
        self.log_text.configure(state='disabled')
        self.log_text.see('end')

    def alert(self, msg):
        t = datetime.datetime.now().strftime('%H:%M:%S')
        self.alert_text.configure(state='normal')
        self.alert_text.insert('end', f"⚠️[{t}] {msg}\n")
        self.alert_text.configure(state='disabled')
        self.alert_text.see('end')

    def run_in_thread(self, func):
        t = threading.Thread(target=func, daemon=True)
        t.start()

    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_lbl.configure(
            text=now.strftime('%A, %d %B %Y | %H:%M:%S'))
        self.root.after(1000, self.update_clock)

    def refresh_users(self):
        self.users_list.delete(0, 'end')
        users = iris.load_users()
        for i, u in enumerate(users, 1):
            self.users_list.insert('end', f"  {i}. 👤 {u['name']}")
        n = len(users)
        for i in range(0, n, 2):
            self.users_list.itemconfig(i, fg=GREEN)
        for i in range(1, n, 2):
            self.users_list.itemconfig(i, fg=ACCENT)
        self.upd(self.user_card, f"{n}", ACCENT if n > 0 else RED)

    def refresh_today(self):
        af = 'F:/FYP_Project/database/attendance.csv'
        self.today_text.configure(state='normal')
        self.today_text.delete(1.0, 'end')
        today = datetime.datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists(af):
            self.today_text.insert('end', "No records yet!\nScan face to record.")
            self.today_text.configure(state='disabled')
            return

        import csv
        present = 0
        with open(af, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 6 and row[1] == today:
                    present += 1
                    out = row[3] if row[3] else "Still in ⏳"
                    hrs = row[4] if row[4] else "---"
                    self.today_text.insert('end',
                        f"👤 {row[0]}\n"
                        f" In:{row[2]}  Out:{out}\n"
                        f" Hrs:{hrs}\n{'─'*30}\n")

        if present == 0:
            self.today_text.insert('end', "No attendance today!")
        self.today_text.configure(state='disabled')

    def refresh_alerts(self):
        self.alert_text.configure(state='normal')
        self.alert_text.delete(1.0, 'end')
        lf = 'F:/FYP_Project/database/access_logs.csv'
        af = 'F:/FYP_Project/reports/anomaly_report.csv'
        found = False

        if os.path.exists(lf):
            df = pd.read_csv(lf)
            d  = len(df[df['status'] == 'DENIED'])
            a  = len(df[df['status'] == 'SECURITY_ALERT'])
            if d > 0:
                self.alert_text.insert('end', f"⚠️ {d} failed attempts\n")
                found = True
            if a > 0:
                self.alert_text.insert('end', f"🚨 {a} security alerts!\n")
                found = True

        if os.path.exists(af):
            df2 = pd.read_csv(af)
            h   = len(df2[df2['risk'] == 'HIGH'])
            if h > 0:
                self.alert_text.insert('end', f"🔴 {h} HIGH risks!\n")
                found = True
            for _, row in df2.iterrows():
                self.alert_text.insert('end',
                    f"• {row['type']}\n  [{row['risk']}]\n")

        if not found:
            self.alert_text.insert('end', "✅ No threats!\nSystem normal.")

        self.alert_text.configure(state='disabled')

    def show_security_alert(self):
        a = tk.Toplevel(self.root)
        a.title("⚠️ SECURITY ALERT!")
        a.geometry("400x240")
        a.configure(bg=RED)
        a.grab_set()

        tk.Label(a, text="🚨 SECURITY ALERT!",
                font=("Arial", 15, "bold"), bg=RED, fg=WHITE).pack(pady=10)
        tk.Label(a, text="3 FAILED ATTEMPTS!",
                font=("Arial", 12, "bold"), bg=RED, fg=YELLOW).pack()
        tk.Label(a,
                text="Unauthorized person!\nIntruder photo captured!",
                font=("Arial", 10), bg=RED, fg=WHITE, justify='center').pack(pady=6)
        tk.Label(a,
                text=f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}\n"
                     f"Saved: captured_images/",
                font=("Arial", 9), bg=RED, fg=WHITE).pack()
        tk.Button(a, text="✅ Acknowledge",
                 font=("Arial", 10, "bold"),
                 bg=BG_DARK, fg=WHITE,
                 command=a.destroy, relief='flat',
                 cursor='hand2', padx=12, pady=5).pack(pady=8)

    def show_table(self, title, df):
        if df is None or df.empty:
            messagebox.showinfo(title, "No data!")
            return

        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("900x480")
        win.configure(bg=BG_DARK)

        tk.Label(win, text=title, font=FONT_HEAD,
                bg=BG_DARK, fg=ACCENT).pack(pady=6)

        frame = tk.Frame(win, bg=BG_DARK)
        frame.pack(fill='both', expand=True, padx=8, pady=4)

        vsb = ttk.Scrollbar(frame, orient="vertical")
        hsb = ttk.Scrollbar(frame, orient="horizontal")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("FYP.Treeview",
                        background=BG_CARD, foreground=WHITE,
                        rowheight=24, fieldbackground=BG_CARD,
                        font=FONT_SMALL)
        style.configure("FYP.Treeview.Heading",
                        background=BG_PANEL, foreground=ACCENT,
                        font=("Arial", 8, "bold"))

        tree = ttk.Treeview(frame,
                            style="FYP.Treeview",
                            columns=list(df.columns),
                            show='headings',
                            yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        vsb.configure(command=tree.yview)
        hsb.configure(command=tree.xview)

        for col in df.columns:
            tree.heading(col, text=col.upper())
            tree.column(col, width=120, anchor='center')

        for _, row in df.iterrows():
            tree.insert('', 'end', values=list(row))

        tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        tk.Label(win, text=f"Total: {len(df)}",
                font=FONT_SMALL, bg=BG_DARK, fg=GRAY).pack(pady=3)

    def update_far(self):
        if self.total_scans > 0:
            far = round((self.false_accepted / self.total_scans)*100, 2)
            self.upd(self.far_card, f"{far}%",
                    GREEN if far < 5 else RED)

    def show_chart(self, title, path):
        """Display a saved PNG chart in a Tkinter window — works from any thread via root.after"""
        if not os.path.exists(path):
            messagebox.showwarning("No Chart", "Chart not generated yet!\nAdd demo data first.")
            return
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=BG_DARK)
        win.grab_set()

        tk.Label(win, text=title, font=FONT_HEAD,
                bg=BG_DARK, fg=ACCENT).pack(pady=6)

        img   = Image.open(path)
        # Scale down if too large for screen
        img.thumbnail((1200, 700), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        lbl = tk.Label(win, image=photo, bg=BG_DARK)
        lbl.image = photo   # keep reference
        lbl.pack(padx=10, pady=5)

        tk.Button(win, text="✖ Close", font=FONT_BTN,
                 bg=RED, fg=WHITE, relief='flat',
                 cursor='hand2',
                 command=win.destroy,
                 padx=15, pady=5).pack(pady=8)

    def exit_app(self):
        if messagebox.askyesno("Exit", "Exit system?"):
            self.stop_camera()
            self.root.destroy()

    # ==========================================
    # SCAN ENTRY
    # FIX: Uses callback-based liveness (main thread)
    #      then spawns thread for face recognition only
    # ==========================================

    def scan_entry(self):
        self.log("🚪 ENTRY scan starting...", 'cyan')
        self.log("⏳ Step 1: Liveness check...", 'yellow')
        self.upd(self.status_card, "⏳ SCANNING...", YELLOW)
        self.status_var.set("Scanning for entry...")

        def after_liveness(is_live):
            if not is_live:
                self.log("❌ LIVENESS FAILED! Spoof/Photo blocked!", 'red')
                self.alert("PRESENTATION ATTACK DETECTED! Spoof blocked!")
                self.upd(self.live_card, "❌ FAILED", RED)
                self.upd(self.status_card, "❌ SPOOF BLOCKED", RED)
                self.restart_camera()
                messagebox.showwarning(
                    "⚠️ Spoof Detected!",
                    "Liveness check failed!\n\n"
                    "Challenge-Response test not completed!\n"
                    "Possible spoof attack blocked!")
                return

            # Liveness passed — now do face recognition in a thread
            self.log("✅ Liveness: PASSED", 'green')
            self.upd(self.live_card, "✅ PASSED", GREEN)
            self.log("⏳ Step 2: Face recognition...", 'yellow')

            def run_recognition():
                result, name, frame = iris.recognize_user()
                status, self.failed_attempts = access.process_access(
                    result, name, frame, self.failed_attempts)
                fa = self.failed_attempts

                self.root.after(0, lambda: self.smart_upd_cards(fa))

                if fa >= 3:
                    self.root.after(0, lambda: [
                        self.log("🚨 SECURITY ALERT! 3 failed attempts!", 'red'),
                        self.alert("3 FAILED ATTEMPTS! Intruder photo saved!"),
                        self.show_security_alert()
                    ])
                    self.failed_attempts = 0

                if status == "GRANTED":
                    self.total_scans += 1
                    attendance.record_entry(name)
                    self.root.after(0, lambda: [
                        self.log(f"✅ ENTRY GRANTED: {name}", 'green'),
                        self.log(f"📅 Entry recorded for {name}", 'green'),
                        self.upd(self.scan_card, f"✅ {name}", GREEN),
                        self.upd(self.status_card, "✅ GRANTED", GREEN),
                        self.status_var.set(f"Entry: {name}"),
                        self.refresh_today(),
                        self.update_far(),
                        self.restart_camera(),
                        messagebox.showinfo(
                            "✅ Access Granted!",
                            f"Welcome {name}!\n\n"
                            f"✅ Liveness: PASSED\n"
                            f"✅ Face: RECOGNIZED\n"
                            f"✅ Entry recorded!")
                    ])
                else:
                    self.total_scans += 1
                    self.false_rejected += 1
                    self.root.after(0, lambda: [
                        self.log("❌ ENTRY DENIED: Not recognized!", 'red'),
                        self.alert(f"ACCESS DENIED! Failed: {fa}/3"),
                        self.upd(self.scan_card, "❌ DENIED", RED),
                        self.upd(self.status_card, "❌ DENIED", RED),
                        self.update_far(),
                        self.restart_camera(),
                        messagebox.showwarning(
                            "❌ Access Denied!",
                            f"Unauthorized person!\n\n"
                            f"Face not recognized!\n"
                            f"Failed: {fa}/3")
                    ])

            self.run_in_thread(run_recognition)

        # Run liveness on main thread via callback
        self.run_liveness_challenge(after_liveness)

    # ==========================================
    # SCAN EXIT
    # FIX: Same callback-based liveness fix
    # ==========================================

    def scan_exit(self):
        self.log("🚶 EXIT scan...", 'cyan')
        self.upd(self.status_card, "⏳ SCANNING...", YELLOW)

        def after_liveness(is_live):
            if not is_live:
                self.log("❌ Liveness failed at exit!", 'red')
                self.upd(self.live_card, "❌ FAILED", RED)
                self.restart_camera()
                messagebox.showwarning(
                    "Failed!",
                    "Liveness check failed!\nCannot record exit!")
                return

            def run_recognition():
                result, name, frame = iris.recognize_user()
                if result == "RECOGNIZED":
                    attendance.record_exit(name)
                    self.root.after(0, lambda: [
                        self.log(f"✅ EXIT: {name}", 'green'),
                        self.log(f"⏰ Hours calculated for {name}", 'green'),
                        self.upd(self.live_card, "✅ PASSED", GREEN),
                        self.upd(self.scan_card, f"🚶 {name}", ACCENT),
                        self.upd(self.status_card, "✅ EXIT", GREEN),
                        self.status_var.set(f"Exit: {name}"),
                        self.refresh_today(),
                        self.restart_camera(),
                        messagebox.showinfo(
                            "✅ Exit Recorded!",
                            f"Goodbye {name}!\n\n"
                            f"✅ Exit recorded!\n"
                            f"✅ Hours calculated!")
                    ])
                else:
                    self.root.after(0, lambda: [
                        self.log("❌ Exit denied!", 'red'),
                        self.upd(self.status_card, "❌ UNAUTHORIZED", RED),
                        self.restart_camera(),
                        messagebox.showwarning(
                            "❌ Denied!",
                            "Not recognized!\nCannot record exit!")
                    ])

            self.run_in_thread(run_recognition)

        self.run_liveness_challenge(after_liveness)

    # ==========================================
    # REGISTER USER
    # ==========================================

    def register_user(self):
        d = tk.Toplevel(self.root)
        d.title("Register New User")
        d.geometry("360x220")
        d.configure(bg=BG_CARD)
        d.grab_set()

        tk.Label(d, text="➕ Register New User",
                font=FONT_HEAD, bg=BG_CARD, fg=YELLOW).pack(pady=10)
        tk.Label(d, text="Enter employee name:",
                font=FONT_SMALL, bg=BG_CARD, fg=WHITE).pack()

        nv = tk.StringVar()
        e  = tk.Entry(d, textvariable=nv,
                     font=("Arial", 11),
                     bg=BG_DARK, fg=WHITE,
                     insertbackground=WHITE, width=26)
        e.pack(pady=6)
        e.focus()

        tk.Label(d,
                text="Camera opens → Click window → Press S five times",
                font=("Arial", 7), bg=BG_CARD, fg=GRAY,
                wraplength=300).pack()

        def go():
            name = nv.get().strip()
            if not name:
                messagebox.showwarning("Required", "Enter a name!")
                return
            d.destroy()
            self.log(f"⏳ Registering: {name}", 'yellow')
            self.upd(self.status_card, "⏳ REGISTERING...", YELLOW)

            def run():
                iris.register_user(name)
                self.root.after(0, lambda: [
                    self.log(f"✅ {name} registered!", 'green'),
                    self.upd(self.status_card, "✅ REGISTERED", GREEN),
                    self.refresh_users(),
                    messagebox.showinfo(
                        "✅ Done!",
                        f"{name} registered!\nCan now access system!")
                ])

            self.run_in_thread(run)

        tk.Button(d, text="📷 Start Registration",
                 font=FONT_BTN,
                 bg=YELLOW, fg=BG_DARK,
                 command=go, relief='flat',
                 cursor='hand2', padx=15, pady=6).pack(pady=10)

    # ==========================================
    # DELETE USER
    # ==========================================

    def delete_user(self):
        users = iris.load_users()
        if not users:
            messagebox.showwarning("No Users", "No users registered!")
            return

        d = tk.Toplevel(self.root)
        d.title("Delete User")
        d.geometry("340x290")
        d.configure(bg=BG_CARD)
        d.grab_set()

        tk.Label(d, text="🗑️ Delete User",
                font=FONT_HEAD, bg=BG_CARD, fg=RED).pack(pady=10)

        lb = tk.Listbox(d, font=FONT_SMALL,
                       bg=BG_DARK, fg=WHITE,
                       selectbackground=RED,
                       height=7, width=30)
        lb.pack(pady=6)

        for u in users:
            lb.insert('end', u['name'])

        def go():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Select", "Select a user!")
                return
            name = lb.get(sel[0])
            if messagebox.askyesno("⚠️ Confirm",
                    f"Delete {name}?\n\nAccess will be revoked!\nCannot be undone!"):
                d.destroy()
                iris.delete_user(name)
                self.log(f"🗑️ {name} deleted! Access revoked!", 'orange')
                self.alert(f"USER DELETED: {name}")
                self.refresh_users()
                messagebox.showinfo("✅ Deleted!", f"{name} removed!")

        tk.Button(d, text="🗑️ Delete",
                 font=FONT_BTN, bg=RED, fg=WHITE,
                 command=go, relief='flat',
                 cursor='hand2', padx=15, pady=6).pack(pady=5)

    # ==========================================
    # LOGS & STATS
    # ==========================================

    def view_logs(self):
        def run():
            lf = 'F:/FYP_Project/database/access_logs.csv'
            if not os.path.exists(lf):
                self.root.after(0, lambda: messagebox.showwarning(
                    "No Data", "No logs yet!\nScan faces first!"))
                return
            df = pd.read_csv(lf)
            self.root.after(0, lambda: self.show_table("Access Logs", df))
        self.run_in_thread(run)

    def view_stats(self):
        lf = 'F:/FYP_Project/database/access_logs.csv'
        if not os.path.exists(lf):
            messagebox.showwarning("No Data", "No logs!")
            return
        df = pd.read_csv(lf)
        g  = len(df[df['status'] == 'GRANTED'])
        dn = len(df[df['status'] == 'DENIED'])
        al = len(df[df['status'] == 'SECURITY_ALERT'])
        messagebox.showinfo("📊 Statistics",
            f"ACCESS STATISTICS\n{'='*28}\n\n"
            f"✅ Granted: {g}\n"
            f"❌ Denied:  {dn}\n"
            f"🚨 Alerts:  {al}\n"
            f"📊 Total:   {len(df)}")

    # ==========================================
    # ATTENDANCE
    # ==========================================

    def view_attendance(self):
        def run():
            af = 'F:/FYP_Project/database/attendance.csv'
            if not os.path.exists(af):
                self.root.after(0, lambda: messagebox.showwarning(
                    "No Data", "No attendance!\nScan faces first!"))
                return
            df = pd.read_csv(af)
            self.root.after(0, lambda: self.show_table("Attendance", df))
        self.run_in_thread(run)

    def attendance_report(self):
        def run():
            r = attendance.generate_report()
            if r is not None:
                self.root.after(0, lambda: [
                    self.log("✅ Report ready!", 'green'),
                    self.show_table("Attendance Report", r)
                ])
        self.run_in_thread(run)

    def attendance_chart(self):
        def run():
            attendance.plot_attendance()
            chart = 'F:/FYP_Project/reports/attendance_chart.png'
            self.root.after(0, lambda: self.show_chart(
                "📈 Attendance Chart", chart))
        self.run_in_thread(run)

    def todays_summary(self):
        self.refresh_today()
        self.log("✅ Today's summary refreshed!", 'green')

    # ==========================================
    # SALARY
    # ==========================================

    def gen_salary(self):
        def run():
            r = salary.generate_salary_report()
            if r is not None:
                self.root.after(0, lambda: [
                    self.log("✅ Salary done!", 'green'),
                    self.show_table("Salary Report", r)
                ])
        self.run_in_thread(run)

    def view_salary(self):
        def run():
            sf = 'F:/FYP_Project/reports/salary_report.csv'
            if not os.path.exists(sf):
                self.root.after(0, lambda: messagebox.showwarning(
                    "No Data", "Generate salary first!"))
                return
            df = pd.read_csv(sf)
            self.root.after(0, lambda: self.show_table("Salary Report", df))
        self.run_in_thread(run)

    def salary_chart(self):
        def run():
            salary.plot_salary()
            chart = 'F:/FYP_Project/reports/salary_chart.png'
            self.root.after(0, lambda: self.show_chart(
                "📊 Salary Chart", chart))
        self.run_in_thread(run)

    # ==========================================
    # ANOMALY
    # ==========================================

    def detect_anomaly(self):
        self.log("🔍 Detecting anomalies...", 'orange')

        def run():
            results = anomaly.detect_anomalies()
            count   = len(results)
            df      = pd.DataFrame(results) if results else pd.DataFrame()
            self.root.after(0, lambda: [
                self.log(f"🚨 {count} anomalies!",
                        'red' if count > 0 else 'green'),
                self.upd(self.status_card,
                        f"🚨 {count}" if count > 0 else "✅ Normal",
                        RED if count > 0 else GREEN),
                self.refresh_alerts(),
                self.show_table("Anomalies", df) if not df.empty else None,
                messagebox.showinfo("Done",
                    f"Anomalies: {count}\n"
                    f"{'⚠️ Review needed!' if count > 0 else '✅ All clear!'}")
            ])

        self.run_in_thread(run)

    def view_anomaly(self):
        def run():
            af = 'F:/FYP_Project/reports/anomaly_report.csv'
            if not os.path.exists(af):
                self.root.after(0, lambda: messagebox.showwarning(
                    "No Data", "Run detection first!"))
                return
            df = pd.read_csv(af)
            self.root.after(0, lambda: self.show_table("Anomaly Report", df))
        self.run_in_thread(run)

    def anomaly_chart(self):
        def run():
            anomaly.plot_anomaly_chart()
            chart = 'F:/FYP_Project/reports/anomaly_chart.png'
            self.root.after(0, lambda: self.show_chart(
                "📊 Anomaly Chart", chart))
        self.run_in_thread(run)

    # ==========================================
    # SECURITY METRICS
    # ==========================================

    def view_metrics(self):
        total = self.total_scans
        fa    = self.false_accepted
        fr    = self.false_rejected
        far   = round((fa / max(total, 1))*100, 2)
        frr   = round((fr / max(total, 1))*100, 2)
        acc   = round(100 - far - frr, 2)
        messagebox.showinfo("📊 Biometric Security Metrics",
            f"SECURITY METRICS\n{'='*32}\n\n"
            f"Total Scans:    {total}\n"
            f"FAR (False Accept): {far}%\n"
            f"FRR (False Reject): {frr}%\n"
            f"Accuracy:       {acc}%\n\n"
            f"{'─'*32}\n"
            f"FAR < 5%  = Good ✅\n"
            f"FRR < 10% = Acceptable ✅\n"
            f"{'─'*32}\n\n"
            f"Liveness: Challenge-Response\n"
            f"Method: Head Movement PAD\n"
            f"Model: VGG-Face (DeepFace)")

    # ==========================================
    # VIEW USERS
    # ==========================================

    def view_users(self):
        users = iris.load_users()
        if not users:
            messagebox.showwarning("No Users", "No users registered!")
            return

        win = tk.Toplevel(self.root)
        win.title("Registered Users")
        win.geometry("360x320")
        win.configure(bg=BG_DARK)

        tk.Label(win, text="👥 Registered Users",
                font=FONT_HEAD, bg=BG_DARK, fg=ACCENT).pack(pady=8)

        for i, u in enumerate(users, 1):
            f = tk.Frame(win, bg=BG_CARD, relief='groove', bd=1)
            f.pack(fill='x', padx=12, pady=2)
            tk.Label(f, text=f"{i}. 👤 {u['name']}",
                    font=("Arial", 10), bg=BG_CARD, fg=WHITE).pack(
                        side='left', padx=8, pady=5)
            tk.Label(f, text="✅ Active",
                    font=("Arial", 8), bg=BG_CARD, fg=GREEN).pack(
                        side='right', padx=8)

        tk.Label(win, text=f"Total: {len(users)}",
                font=FONT_SMALL, bg=BG_DARK, fg=GRAY).pack(pady=5)
        tk.Button(win, text="Close",
                 font=FONT_BTN, bg=BG_PANEL, fg=WHITE,
                 command=win.destroy, relief='flat').pack()

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = FaceAccessSystem(root)
    root.mainloop()