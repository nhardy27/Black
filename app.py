import streamlit as st
import os
import subprocess

st.title("🎓 Face Attendance System")

if not os.path.exists('student_images'):
    os.makedirs('student_images')

option = st.selectbox("Select Action", ["Choose", "New Student Registration", "Mark Attendance"])

if option == "New Student Registration":
    st.header("🆕 Register a New Student")
    roll = st.text_input("Enter Roll Number")
    name = st.text_input("Enter Name")

    if st.button("Capture Photo"):
        if roll and name:
            subprocess.run(["python", "register_student.py", roll, name])
            st.success("Photo saved successfully!")
        else:
            st.error("Please enter Roll No and Name")

elif option == "Mark Attendance":
    st.header("🧑‍🎓 Face Recognition Attendance")
    if st.button("Start Face Recognition"):
        subprocess.run(["python", "main.py"])
