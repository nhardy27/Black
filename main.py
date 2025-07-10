import face_recognition
import cv2
import os
import numpy as np
from datetime import datetime
import pytz
import dlib
from scipy.spatial import distance
from db import get_connection  # import your MySQL connection

# === Load student images ===
path = 'student_images'
images = []
student_names = []
student_ids = []

for filename in os.listdir(path):
    if filename.endswith(('.jpg', '.png')):
        img = cv2.imread(f'{path}/{filename}')
        images.append(img)
        roll_no, name = filename.split('.')[0].split('_')
        student_ids.append(roll_no)
        student_names.append(name)

def encode_faces(images):
    encoded_list = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encoded_list.append(encode)
        except:
            pass
    return encoded_list

known_encodings = encode_faces(images)

# === Eye Blink Detection Helpers ===
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()
LEFT_EYE = list(range(36, 42))
RIGHT_EYE = list(range(42, 48))
EAR_THRESHOLD = 0.23
CONSEC_FRAMES = 3

frame_counter = 0
blinked_students = set()

# === Attendance Marking ===
def mark_attendance(roll_no, name):
    india_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    date = india_time.strftime("%Y-%m-%d")               
    time = india_time.strftime("%H:%M:%S") 


    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance WHERE roll_no=%s AND date=%s", (roll_no, date))
    result = cursor.fetchone()

    if result:
        cursor.execute("UPDATE attendance SET status='Present', time=%s WHERE roll_no=%s AND date=%s",
                       (time, roll_no, date))
        print(f"⏳ Updated as Present: {roll_no} - {name}")
    else:
        cursor.execute("INSERT INTO attendance (roll_no, name, date, time, status) VALUES (%s, %s, %s, %s, %s)",
                       (roll_no, name, date, time, 'Present'))
        print(f"✅ Attendance marked for {roll_no} - {name}")

    conn.commit()
    cursor.close()
    conn.close()

# === Start Camera ===
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    small_img = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    rgb_img = cv2.cvtColor(small_img, cv2.COLOR_BGR2RGB)

    faces_cur_frame = face_recognition.face_locations(rgb_img)
    encodes_cur_frame = face_recognition.face_encodings(rgb_img, faces_cur_frame)

    for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(known_encodings, encode_face)
        face_dist = face_recognition.face_distance(known_encodings, encode_face)
        match_index = np.argmin(face_dist)

        if matches[match_index]:
            name = student_names[match_index]
            roll = student_ids[match_index]

            # Skip if already marked
            if roll in blinked_students:
                continue

            face_rects = detector(rgb_img)
            for rect in face_rects:
                shape = predictor(rgb_img, rect)

                left_eye = [ (shape.part(i).x, shape.part(i).y) for i in LEFT_EYE ]
                right_eye = [ (shape.part(i).x, shape.part(i).y) for i in RIGHT_EYE ]

                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                avg_ear = (left_ear + right_ear) / 2.0

                if avg_ear < EAR_THRESHOLD:
                    frame_counter += 1
                else:
                    if frame_counter >= CONSEC_FRAMES:
                        print("👁️ Blink Detected!")
                        mark_attendance(roll, name)
                        blinked_students.add(roll)
                    frame_counter = 0

            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(img, f'{roll} {name}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow('Face Attendance System with Blink Check', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
