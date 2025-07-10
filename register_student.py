import cv2
import os
import sys
import face_recognition
import numpy as np
from db import get_connection

# ✅ Check if roll number already exists
def student_exists(roll):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE roll_no=%s", (roll,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None

# ✅ Insert new student into the database
def save_student(roll, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (roll_no, name) VALUES (%s, %s)", (roll, name))
    conn.commit()
    cursor.close()
    conn.close()

# ✅ Load existing face encodings from student_images/
def load_known_encodings():
    encodings = []
    path = 'student_images'
    for filename in os.listdir(path):
        if filename.endswith(('.jpg', '.png')):
            img_path = os.path.join(path, filename)
            img = face_recognition.load_image_file(img_path)
            try:
                encoding = face_recognition.face_encodings(img)[0]
                encodings.append(encoding)
            except:
                pass
    return encodings

# ✅ Main student registration function
def register_student(roll, name):
    if not roll or not name:
        print("❌ Roll number and name are required.")
        return

    if student_exists(roll):
        print(f"⚠️ Roll No {roll} already exists in the database.")
        return

    os.makedirs('student_images', exist_ok=True)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Could not access the camera.")
        return

    print("📸 Press 's' to capture photo | Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame from camera.")
            continue

        cv2.imshow("Capture Face - Press 's'", frame)
        key = cv2.waitKey(1)

        if key == ord('s'):
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                new_encoding = face_recognition.face_encodings(rgb_frame)[0]
            except:
                print("❌ No face detected. Try again.")
                continue

            known_encodings = load_known_encodings()
            face_distances = face_recognition.face_distance(known_encodings, new_encoding)

            if len(face_distances) > 0 and np.min(face_distances) < 0.4:
                print("❌ Face already exists with another roll number. Registration blocked.")
                break

            # ✅ Save image and DB record
            filename = f"{roll}_{name}.jpg"
            filepath = os.path.join('student_images', filename)
            cv2.imwrite(filepath, frame)
            save_student(roll, name)
            print(f"✅ Registered successfully. Photo saved as {filepath}")
            break

        elif key == ord('q'):
            print("❌ Registration cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

# ✅ Command line call
if __name__ == "__main__":
    roll = sys.argv[1]
    name = sys.argv[2]
    register_student(roll, name)
