from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# File to store user data
USERS_FILE = 'users.json'

# Load user data from the JSON file
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save user data to the JSON file
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Route for Home Page
@app.route('/')
def index():
    return render_template('login.html')

# Route for Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        weight = request.form['weight']
        height = request.form['height']
        age = request.form['age']
        gender = request.form['gender']
        goal = request.form['goal']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))

        users = load_users()
        if username in users:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users[username] = {
            'password': hashed_password,
            'weight': weight,
            'height': height,
            'age': age,
            'gender': gender,
            'goal': goal,
            'workout_plans': []
        }
        save_users(users)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

# Route for Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username not in users or not check_password_hash(users[username]['password'], password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        session['user'] = username
        flash('Login successful', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

# Dashboard after login
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    users = load_users()
    user_data = users[user]

    # Perform necessary calculations
    weight = float(user_data['weight'])
    height = float(user_data['height']) / 100  # height in meters
    bmi = round(weight / (height ** 2), 2)  # BMI calculation

    return render_template('dashboard.html', user=user, user_data=user_data, bmi=bmi)

# Route for selecting workout plans
@app.route('/workout_plans')
def workout_plans():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    users = load_users()
    user_data = users[user]

    goal = user_data['goal']
    workout_plan = ""

    # Suggest workout plan based on goal
    if goal == 'weight_loss':
        workout_plan = "Cardio exercises: Running, Cycling, Swimming, High-Intensity Interval Training (HIIT)"
    elif goal == 'weight_gain':
        workout_plan = "Strength training: Weightlifting, Resistance exercises, Squats, Deadlifts"
    else:
        workout_plan = "General fitness: Mixed cardio and strength training."

    return render_template('workout_plans.html', user=user, workout_plan=workout_plan)

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
