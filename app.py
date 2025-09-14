from flask import Flask, request, render_template, redirect, session, url_for
from auth import signup, login
from booking import add_booking, generate_qr_code
import datetime
import webbrowser
from threading import Timer

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Root Route
@app.route('/')
def index():
    # Redirect to the login page
    return redirect(url_for('login_page'))

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        signup(username, password)
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login(username, password)
        if user:
            session['user_id'] = user[0]
            return redirect('/booking')
        else:
            return "Login failed"
    return render_template('login.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking_page():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        passenger_name = request.form['passenger_name']
        source = request.form['source']
        destination = request.form['destination']
        journey_date = request.form['journey_date']
        user_id = session['user_id']
        add_booking(user_id, passenger_name, source, destination, journey_date)
        
        # Generate QR Code
        booking_details = f"Passenger: {passenger_name}, Source: {source}, Destination: {destination}, Date: {journey_date}"
        generate_qr_code(user_id, booking_details)
        
        return "Booking Successful! QR Code generated."
    return render_template('booking.html')

# Function to open the app in the default web browser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    # Timer to delay browser opening until the server is running
    Timer(1, open_browser).start()
    app.run(debug=True)
