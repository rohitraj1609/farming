import pymysql

def create_connection():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="raj@123",
        database="booking"
    )
    return connection

def setup_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        passenger_name VARCHAR(100),
        source VARCHAR(50),
        destination VARCHAR(50),
        journey_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)
    conn.commit()
    conn.close()

# Run this once to set up tables
setup_tables()
