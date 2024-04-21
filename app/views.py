from flask import redirect, render_template, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import app
from .models import User, Courses
# from .helpers import get_course
from app import bcrypt, db

@app.route("/")
def home():
    courses = db.session.query(Courses).all()
    courseSubjectCodes = []
    for course in courses:
        if course.subject_code not in courseSubjectCodes:
            courseSubjectCodes.append(course.subject_code)

    return render_template('index.html', courses=courses, courseSubjectCodes=courseSubjectCodes)

@app.route('/scheduler')
def scheduler():
    courses = Courses.query.all()
    return render_template('scheduler.html', courses=courses)

@app.route("/setup")
def setup():
    return render_template('setup.html')

@app.route("/setup", methods=['POST'])
@login_required
def setup_post():
    print (request.form)
    major = request.form.get('major')
    year = request.form.get('year')
    courses_csv = request.form.get('courses')
    courses = courses_csv.split(',')
    print (courses)

    # Add the user's major and year to the database
    current_user.major = major
    current_user.year = year

    # Add the user's courses to the database
    for c in courses:
        # Check if the course is in the database
        course = get_course(c)
        if course:
            x = UserCourse(user_id=current_user.id, course_id=course.crn)
            db.session.add(x)
    
    db.session.commit()

    return redirect(url_for('home'))

# For now this is just to test the login system
@app.route("/profile")
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not bcrypt.check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('home'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=bcrypt.generate_password_hash(password))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('setup'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
