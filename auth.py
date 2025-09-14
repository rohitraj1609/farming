from db import create_connection
import hashlib

def signup(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()
    conn.close()

def login(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user
