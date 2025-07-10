# Black
# 🎓 Face Recognition Attendance System

This is a Python + Streamlit based **Face Recognition Attendance System** that:

- Detects and recognizes student faces using webcam
- Marks attendance with date & time in CSV or MySQL
- Prevents fake attendance using liveness detection (blink detection)
- Has a user-friendly Streamlit interface

---

## 🚀 Features

✅ Register new students with photos  
✅ Real-time face recognition  
✅ Blink detection for liveness  
✅ Prevents duplicate attendance on the same day  
✅ Saves attendance in CSV and/or MySQL  
✅ Streamlit UI — No technical knowledge needed to use

---

## 🛠️ Project Structure

face-attendance-system/
├── app.py
├── main.py
├── db.py
├── register_student.py
├── download_model.py # optional: auto-download dlib model
├── requirements.txt
├── README.md
├── student_images/ # folder to store student face photos
└── shape_predictor_68_face_landmarks.dat # required for blink detection

pip install -r requirements.txt

Download Required File (for blink detection)
This app uses dlib’s 68-point facial landmark model for liveness detection.

📥 Download from official site:

👉 Download shape_predictor_68_face_landmarks.dat.bz2

Then extract it using any tool or:
bunzip2 shape_predictor_68_face_landmarks.dat.bz2

▶️ Run the App Locally
streamlit run app.py
