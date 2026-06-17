# ============================================
# Module 1 - Face Recognition System
# With Challenge-Response Liveness Detection
# Student: Fizza Arooj & Ghulam Fatima
# FYP: Face Recognition Based Intelligent
#      Access Control System
# ============================================

import cv2
import numpy as np
import os
import csv
import datetime
import shutil
import random
from deepface import DeepFace

# ============================================
# FOLDER PATHS
# ============================================

DATABASE_PATH = 'F:/FYP_Project/database/'
IMAGES_PATH   = 'F:/FYP_Project/captured_images/'
FACES_PATH    = 'F:/FYP_Project/database/faces/'
USERS_FILE    = DATABASE_PATH + 'users.csv'

os.makedirs(DATABASE_PATH, exist_ok=True)
os.makedirs(IMAGES_PATH,   exist_ok=True)
os.makedirs(FACES_PATH,    exist_ok=True)

# ============================================
# LOAD FACE DETECTOR
# ============================================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    'haarcascade_frontalface_default.xml')

# ============================================
# FUNCTION 1 - Draw Face Box
# ============================================

def draw_face_overlay(frame, faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(frame,
                     (x, y),
                     (x+w, y+h),
                     (0, 255, 0), 2)
        cv2.putText(frame,
                   "Face Detected",
                   (x, y-10),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (0, 255, 0), 2)
    return frame

# ============================================
# FUNCTION 2 - Challenge Response Liveness
# FIX: Proper camera open/close
#      Lower threshold for better detection
#      Clear pass confirmation before exit
# ============================================

def check_liveness(camera):
    print("\n" + "="*40)
    print("  LIVENESS VERIFICATION")
    print("="*40)
    print("  Follow the instructions!")
    print("  A photo cannot move!")
    print("  Press Q to cancel")
    print("="*40 + "\n")

    all_challenges = [
        {
            'text':      'TURN HEAD LEFT',
            'direction': 'left',
            'color':     (0, 255, 255)
        },
        {
            'text':      'TURN HEAD RIGHT',
            'direction': 'right',
            'color':     (255, 165, 0)
        },
        {
            'text':      'MOVE CLOSER',
            'direction': 'closer',
            'color':     (0, 255, 0)
        },
        {
            'text':      'MOVE BACK',
            'direction': 'back',
            'color':     (255, 0, 255)
        },
    ]

    selected = random.sample(all_challenges, 2)

    for challenge in selected:
        result = run_challenge(camera, challenge)
        if not result:
            print(f"\n❌ Challenge failed: {challenge['text']}")
            return False
        print(f"✅ Challenge passed: {challenge['text']}")

    print("\n✅ LIVENESS CONFIRMED!")
    print("   Real person verified!")
    return True

# ============================================
# FUNCTION 3 - Run Single Challenge
# FIX: Robust initial face detection
#      Lower threshold (30px not 45px)
#      Proper wait after pass before closing
# ============================================

def run_challenge(camera, challenge):
    # BUG FIX: timeout in frames at ~30fps = 10 seconds
    timeout   = 300
    frames    = 0
    passed    = False
    threshold = 30   # FIX: was 45, too strict for webcams

    # FIX: Try up to 30 frames to get a valid initial face
    init_cx = None
    init_cy = None
    init_w  = None

    for attempt in range(30):
        ret, frame = camera.read()
        if not ret:
            continue
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(
            gray, 1.1, 5, minSize=(80, 80))
        if len(faces) > 0:
            (ix, iy, iw, ih) = faces[0]
            init_cx = ix + iw // 2
            init_cy = iy + ih // 2
            init_w  = iw
            break

    # FIX: If no face found after 30 tries, show message and return False
    if init_cx is None:
        # Show "No face detected" message window briefly
        blank = np.zeros((300, 500, 3), dtype=np.uint8)
        cv2.putText(blank, "NO FACE DETECTED", (50, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.putText(blank, "Move closer to camera", (60, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.imshow("Liveness Check - Follow Instruction!", blank)
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
        return False

    while frames < timeout:
        ret, frame = camera.read()
        if not ret:
            continue

        frames += 1
        display = frame.copy()
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces   = face_detector.detectMultiScale(
            gray, 1.1, 5, minSize=(80, 80))

        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)

            curr_cx = x + w // 2
            curr_cy = y + h // 2
            curr_w  = w

            move_x = curr_cx - init_cx
            move_y = curr_cy - init_cy
            move_w = curr_w  - init_w

            d = challenge['direction']

            if d == 'left' and move_x < -threshold:
                passed = True
            elif d == 'right' and move_x > threshold:
                passed = True
            elif d == 'closer' and move_w > threshold:
                passed = True
            elif d == 'back' and move_w < -threshold:
                passed = True

        # Black bar at top
        cv2.rectangle(display, (0, 0),
                     (display.shape[1], 75), (0, 0, 0), -1)

        # Challenge text
        cv2.putText(display,
                   challenge['text'],
                   (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   1.2, challenge['color'], 3)

        # Timer bar
        time_left = max(0, int((timeout - frames) / 30))
        progress  = int((frames / timeout) * 300)

        cv2.rectangle(display, (10, 85), (310, 100), (60, 60, 60), -1)
        cv2.rectangle(display, (10, 85),
                     (10 + progress, 100),
                     (0, 255, 0) if not passed else (0, 255, 255), -1)

        cv2.putText(display,
                   f"Time: {time_left}s",
                   (10, 125),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.7, (255, 255, 255), 1)

        if passed:
            cv2.putText(display,
                       "DONE! MOVE BACK TO CENTER",
                       (10, 165),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       0.8, (0, 255, 0), 2)

        cv2.imshow("Liveness Check - Follow Instruction!", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            cv2.destroyAllWindows()
            return False

        # FIX: Show "DONE" for 1 second after passing, then break
        if passed:
            cv2.waitKey(1000)
            break

    cv2.destroyAllWindows()
    return passed

# ============================================
# FUNCTION 4 - Compare Faces
# ============================================

def compare_faces(current_path, registered_path):
    try:
        result = DeepFace.verify(
            img1_path=current_path,
            img2_path=registered_path,
            model_name='VGG-Face',
            enforce_detection=False,
            silent=True)

        is_same    = result['verified']
        distance   = result['distance']
        similarity = round((1 - distance) * 100, 2)
        return is_same, similarity

    except Exception as e:
        print(f"   Error: {e}")
        return False, 0.0

# ============================================
# FUNCTION 5 - Save User
# ============================================

def save_user(name, face_path):
    file_exists = os.path.exists(USERS_FILE)
    with open(USERS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['name', 'face_path'])
        writer.writerow([name, face_path])
    print(f"✅ {name} saved!")

# ============================================
# FUNCTION 6 - Load Users
# ============================================

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    users = []
    with open(USERS_FILE, 'r') as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            return []
        for row in reader:
            if len(row) >= 2:
                users.append({
                    'name':      row[0],
                    'face_path': row[1]})
    return users

# ============================================
# FUNCTION 7 - Delete User
# ============================================

def delete_user(user_name):
    if not os.path.exists(USERS_FILE):
        print("\n❌ No users found!")
        return False

    all_rows     = []
    header       = None
    found        = False
    deleted_path = None

    with open(USERS_FILE, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                if row[0].strip().lower() == user_name.strip().lower():
                    found        = True
                    deleted_path = row[1]
                else:
                    all_rows.append(row)

    if not found:
        print(f"\n❌ {user_name} not found!")
        return False

    if deleted_path and os.path.exists(deleted_path):
        os.remove(deleted_path)

    for i in range(1, 6):
        sample = f"{FACES_PATH}{user_name}_s{i}.jpg"
        if os.path.exists(sample):
            os.remove(sample)

    with open(USERS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_rows)

    print(f"\n✅ {user_name} DELETED!")
    return True

# ============================================
# FUNCTION 8 - Save Captured Image
# ============================================

def save_captured_image(frame, face_coords, name, status):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    (x, y, w, h) = face_coords
    pad = 20
    y1  = max(0, y-pad)
    y2  = min(frame.shape[0], y+h+pad)
    x1  = max(0, x-pad)
    x2  = min(frame.shape[1], x+w+pad)
    face_crop = frame[y1:y2, x1:x2]

    if status == "AUTHORIZED":
        fname = f"Authorized_{name}_{timestamp}.jpg"
    else:
        fname = f"Unauthorized_Unknown_{timestamp}.jpg"

    fpath = IMAGES_PATH + fname
    cv2.imwrite(fpath, face_crop)
    print(f"📸 Saved: {fname}")
    return fpath

# ============================================
# FUNCTION 9 - Register New User
# ============================================

def register_user(user_name):
    users = load_users()
    for u in users:
        if u['name'].lower() == user_name.lower():
            print(f"\n⚠️  {user_name} already registered!")
            return

    camera     = cv2.VideoCapture(0)
    samples    = []
    needed     = 5
    face_found = False

    print(f"\n{'='*40}")
    print(f"  Registering: {user_name}")
    print(f"{'='*40}")
    print("📋 Instructions:")
    print("  1. Sit 30-40cm from camera")
    print("  2. Good lighting on face")
    print("  3. Look straight at camera")
    print("  4. CLICK on camera window")
    print(f"  5. Press S five times")
    print("  6. Press Q to cancel")
    print(f"{'='*40}\n")

    while len(samples) < needed:
        ret, frame = camera.read()
        if not ret:
            continue

        display = frame.copy()
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces   = face_detector.detectMultiScale(
            gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            face_found = False
            cv2.putText(display, "NO FACE DETECTED",
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                       0.9, (0, 0, 255), 2)
            cv2.putText(display, ">> Move closer",
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 255, 255), 2)
        else:
            face_found = True
            display    = draw_face_overlay(display, faces)
            cv2.putText(display,
                       f"Samples: {len(samples)}/{needed}",
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                       0.8, (0, 255, 255), 2)
            cv2.putText(display, "CLICK + PRESS S",
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                       0.9, (0, 255, 255), 2)
            cv2.putText(display, f"User: {user_name}",
                       (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (255, 255, 0), 2)

        cv2.imshow("REGISTER | Click Then S", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            if not face_found:
                print("❌ No face!")
            else:
                ret2, sf = camera.read()
                if ret2:
                    g2 = cv2.cvtColor(sf, cv2.COLOR_BGR2GRAY)
                    f2 = face_detector.detectMultiScale(
                        g2, 1.1, 5, minSize=(100, 100))
                    if len(f2) > 0:
                        (x, y, w, h) = f2[0]
                        pad = 20
                        y1  = max(0, y-pad)
                        y2  = min(sf.shape[0], y+h+pad)
                        x1  = max(0, x-pad)
                        x2  = min(sf.shape[1], x+w+pad)
                        face_img = sf[y1:y2, x1:x2]
                        spath = (f"{FACES_PATH}"
                                 f"{user_name}_s{len(samples)+1}.jpg")
                        cv2.imwrite(spath, face_img)
                        samples.append(spath)
                        print(f"✅ Sample {len(samples)}/{needed}!")

                        if len(samples) == needed:
                            final_path = f"{FACES_PATH}{user_name}.jpg"
                            shutil.copy(samples[2], final_path)
                            save_user(user_name, final_path)
                            save_captured_image(sf, (x, y, w, h),
                                                user_name, "AUTHORIZED")
                            print(f"\n{'='*40}")
                            print("  SUCCESS!")
                            print(f"  {user_name} registered!")
                            print(f"{'='*40}\n")
                    else:
                        print("❌ Face moved!")

        if key == ord('q'):
            print("\nCancelled!")
            break

    camera.release()
    cv2.destroyAllWindows()

# ============================================
# FUNCTION 10 - Recognize User
# FIX: Opens its OWN camera for liveness
#      then reuses same camera for recognition
#      Auto-exits after match found (no Q needed)
#      Press Q only to cancel manually
# ============================================

def recognize_user():
    print(f"\n{'='*40}")
    print("  FACE RECOGNITION SYSTEM")
    print(f"{'='*40}")
    print("  STEP 1: Liveness Verification")
    print("  STEP 2: Face Recognition")
    print(f"{'='*40}\n")

    users = load_users()
    if not users:
        print("❌ No users registered!")
        return "NOT RECOGNIZED", "Unknown", None

    print(f"✅ {len(users)} user(s) loaded!")

    # Open ONE camera for both liveness and recognition
    camera = cv2.VideoCapture(0)

    # ══════════════════════════
    # STEP 1: LIVENESS CHECK
    # ══════════════════════════
    print("\n⏳ STEP 1: Liveness check...")
    print("   Follow the on-screen instructions!\n")

    is_live = check_liveness(camera)

    if not is_live:
        print("\n🚨 LIVENESS FAILED!")
        print("   Presentation attack detected!")
        print("   Access DENIED!")

        ret, frame = camera.read()
        if ret:
            gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(
                gray, 1.1, 5, minSize=(100, 100))
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                save_captured_image(frame, (x, y, w, h),
                                    "SPOOF", "UNAUTHORIZED")
                print("📸 Attack captured!")

        camera.release()
        return ("NOT RECOGNIZED", "LIVENESS FAILED", None)

    # ══════════════════════════
    # STEP 2: FACE RECOGNITION
    # FIX: Auto-exit after match
    #      Max 150 frames (~5 sec) to find a face
    # ══════════════════════════
    print("\n✅ Liveness PASSED!")
    print("⏳ STEP 2: Recognizing face...")
    print("   Please look at camera!\n")

    result          = "NOT RECOGNIZED"
    recognized_name = "Unknown"
    image_captured  = False
    failed_attempts = 0
    frame_count     = 0
    compare_every   = 30
    is_authorized   = False
    best_name       = "Unknown"
    best_similarity = 0
    last_frame      = None
    MAX_FRAMES      = 300   # FIX: 10 second max, then auto-exit

    temp_path = DATABASE_PATH + 'temp_frame.jpg'

    while frame_count < MAX_FRAMES:
        ret, frame = camera.read()
        if not ret:
            continue

        last_frame  = frame.copy()
        display     = frame.copy()
        gray        = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces       = face_detector.detectMultiScale(
            gray, 1.1, 5, minSize=(100, 100))

        if len(faces) == 0:
            cv2.putText(display, "No Face Detected",
                       (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                       0.9, (0, 0, 255), 2)
            cv2.putText(display, ">> Move closer",
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                       0.7, (0, 255, 255), 2)
        else:
            frame_count += 1

        for (x, y, w, h) in faces:
            display = draw_face_overlay(display, faces)

            if frame_count % compare_every == 0:
                pad = 20
                y1  = max(0, y-pad)
                y2  = min(frame.shape[0], y+h+pad)
                x1  = max(0, x-pad)
                x2  = min(frame.shape[1], x+w+pad)
                cv2.imwrite(temp_path, frame[y1:y2, x1:x2])

                best_name       = "Unknown"
                best_similarity = 0
                is_authorized   = False

                for u in users:
                    same, sim = compare_faces(
                        temp_path, u['face_path'])
                    print(f"  vs {u['name']}: match={same} sim={sim}%")
                    if same and sim > best_similarity:
                        best_similarity = sim
                        best_name       = u['name']
                        is_authorized   = True

                if is_authorized:
                    result          = "RECOGNIZED"
                    recognized_name = best_name
                    failed_attempts = 0
                else:
                    result          = "NOT RECOGNIZED"
                    recognized_name = "Unknown"
                    failed_attempts += 1

                if failed_attempts >= 3:
                    print("\n🚨 3 FAILED!")
                    save_captured_image(display, (x, y, w, h),
                                        "Unknown", "UNAUTHORIZED")
                    failed_attempts = 0

            if is_authorized:
                color = (0, 255, 0)
                cv2.putText(display,
                           f"AUTHORIZED: {best_name}",
                           (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                           0.9, color, 2)
                cv2.putText(display,
                           f"Match: {best_similarity}%",
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, color, 2)
                cv2.putText(display, "✅ Access Granted!",
                           (10, 115), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, color, 2)
            else:
                color = (0, 0, 255)
                cv2.putText(display, "UNAUTHORIZED!",
                           (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                           0.9, color, 2)
                cv2.putText(display,
                           f"Failed: {failed_attempts}/3",
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, color, 2)
                cv2.putText(display, "❌ Access Denied!",
                           (10, 115), cv2.FONT_HERSHEY_SIMPLEX,
                           0.8, color, 2)

            if is_authorized and not image_captured:
                save_captured_image(display, (x, y, w, h),
                                    best_name, "AUTHORIZED")
                image_captured = True

            if image_captured:
                cv2.putText(display, "Image Saved ✅",
                           (10, 150), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (0, 255, 255), 2)

        # Time counter
        time_left = max(0, int((MAX_FRAMES - frame_count) / 30))
        cv2.putText(display, f"Time: {time_left}s",
                   (display.shape[1]-100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (255, 255, 0), 1)

        cv2.putText(display, "Press Q to cancel",
                   (10, display.shape[0]-15),
                   cv2.FONT_HERSHEY_SIMPLEX,
                   0.6, (255, 255, 255), 1)

        cv2.imshow("Face Recognition", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        # FIX: Auto-exit 1.5 seconds after successful match
        if is_authorized and image_captured:
            cv2.waitKey(1500)
            break

    if os.path.exists(temp_path):
        os.remove(temp_path)

    camera.release()
    cv2.destroyAllWindows()
    return result, recognized_name, last_frame

# ============================================
# MAIN MENU
# ============================================

def main():
    while True:
        print("\n" + "="*40)
        print("  FACE RECOGNITION SYSTEM")
        print("  Fizza Arooj & Ghulam Fatima")
        print("="*40)
        print("  1. Register New User")
        print("  2. Recognize User")
        print("  3. View Registered Users")
        print("  4. Delete User")
        print("  5. Exit")
        print("="*40)
        choice = input("Enter choice: ")

        if choice == "1":
            name = input("Enter name: ")
            register_user(name)
        elif choice == "2":
            result, name, frame = recognize_user()
            print(f"\n  RESULT: {result}")
            print(f"  NAME:   {name}")
        elif choice == "3":
            users = load_users()
            print("\n  Registered Users:")
            if not users:
                print("  No users yet!")
            for u in users:
                print(f"  → {u['name']}")
        elif choice == "4":
            users = load_users()
            if not users:
                print("❌ No users!")
            else:
                for u in users:
                    print(f"  → {u['name']}")
                name = input("Enter name to delete: ")
                confirm = input(f"Delete {name}? yes/no: ")
                if confirm.lower() == 'yes':
                    delete_user(name)
        elif choice == "5":
            print("\nGoodbye! 👋")
            break
        else:
            print("❌ Enter 1 to 5!")

if __name__ == "__main__":
    main()