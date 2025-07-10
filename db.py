# db.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # ← apna MySQL username likhe
        password="Hardy@271003",  # ← apna MySQL password likhe
        database="attendance_system"
    )
