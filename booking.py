from db import create_connection
import qrcode

def add_booking(user_id, passenger_name, source, destination, journey_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bookings (user_id, passenger_name, source, destination, journey_date) VALUES (%s, %s, %s, %s, %s)",
        (user_id, passenger_name, source, destination, journey_date)
    )
    conn.commit()
    conn.close()

def generate_qr_code(booking_id, details):
    qr = qrcode.make(details)
    qr.save(f"booking_{booking_id}.png")
