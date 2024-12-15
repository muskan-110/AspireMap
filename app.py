from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # Importing Bcrypt

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

# Initialize Bcrypt
bcrypt = Bcrypt(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

db = SQLAlchemy(app)

# User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Student model for the database (for storing student form data)
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)
    stream = db.Column(db.String(50), nullable=False)
    subjects = db.Column(db.String(500), nullable=False)  # Store subjects as a comma-separated string
    interests = db.Column(db.String(500), nullable=True)
    skills = db.Column(db.String(500), nullable=True)

# Home page route (index.html)
@app.route('/')
def home():
    return render_template('index.html')  # This will render the index.html page

@app.route('/about')
def about():
    return render_template('about.html')

# Signup page route (signup.html)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Hash the password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in or choose a different email.', 'danger')
            return redirect(url_for('signup'))  # Redirect back to signup page if email exists

        # Create new user and add to the database
        new_user = User(email=email, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))  # Redirect to login page after successful signup
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f'Error: {e}', 'danger')
            return redirect(url_for('signup'))

    return render_template('signup.html')  # Render the signup page on GET requests

# Login page route (login.html)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()

        if user:
            # Validate the password
            if bcrypt.check_password_hash(user.password, password):
                flash('Login successful!', 'success')
                return redirect(url_for('home'))  # Redirect to the main page
            else:
                flash('Invalid password. Please try again.', 'danger')
        else:
            # User does not exist
            flash('No account found with that email. Please sign up first.', 'warning')

        # Redirect back to the login page if login fails
        return redirect(url_for('login'))

    # For GET requests, simply render the login page without any flash messages
    return render_template('login.html')


# Student form page route (student_form.html)
@app.route('/student_form', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        name = request.form['name']
        student_class = request.form['class']
        stream = ', '.join(request.form.getlist('stream'))  # Get selected streams and join them with a comma
        subjects = ', '.join(request.form.getlist('subjects'))  # Get selected subjects and join them with a comma
        interests = request.form['interests']
        skills = request.form['skills']

        # Create a new student record
        new_student = Student(
            name=name,
            student_class=student_class,
            stream=stream,
            subjects=subjects,
            interests=interests,
            skills=skills
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            flash('Student details submitted successfully!', 'success')
            return redirect(url_for('home'))  # Redirect to the home page after submission
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            flash(f'Error: {e}', 'danger')

    return render_template('student_form.html')  # Render the student form page

# Running the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create all database tables if they don't exist already
    app.run(debug=True)  # Run the Flask app in debug mode
