from flask import redirect, render_template, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import app
from .models import User, Courses, UserCourse
from app import bcrypt, db
from ai.schedule_assistant import ai_response
from ai.mapping_user_electives import ai_electives

import json
import re

@app.route("/")
def home():
    courses = db.session.query(Courses).all()
    courseSubjectCodes = []
    for course in courses:
        if course.subject_code not in courseSubjectCodes:
            courseSubjectCodes.append(course.subject_code)

    return render_template('index.html', courses=courses, courseSubjectCodes=courseSubjectCodes)

@app.route("/assistant")
def assistant():
    return render_template('assistant.html')

@app.route("/assistant", methods=['POST'])
def assistant_ajax():
    query = request.get_json()['input']
    print("Assistant - Sending query to AI: ", query)
    response = ai_response(query)['output']
    print("Assistant - AI response: ", response)
    return jsonify({'response': response})

@app.route("/electives")
def electives():
    return render_template('electives.html')

@app.route("/electives", methods=['POST'])
def electives_ajax():
    query = request.get_json()['input']
    print("Electives - Sending query to AI: ", query)
    response = ai_electives(query)
    print("Electives - AI response: ", response)
    return jsonify({'response': response})

@app.route("/prerequisites")
def prerequisites():
    return render_template('prerequisites.html')

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

    # Add the user's major and year to the database
    current_user.major = major
    current_user.year = year

    # Delete the data the user had already entered to avoid duplicates
    db.session.query(UserCourse).filter_by(user_id=current_user.id).delete()

    # Add the user's courses to the database
    for c in courses:
        # Check if the course is in the database
        save_user_course(c, current_user)
    db.session.commit()

    return redirect(url_for('home'))

# For now this is just to test the login system
@app.route("/profile")
@login_required
def profile():
    course_ids = db.session.query(UserCourse).filter_by(user_id=current_user.id).all()
    print(course_ids)
    courses = []
    for c in course_ids:
        course = db.session.query(Courses).filter_by(crn=c.course_id).first()
        courses.append(course)
    
    print(courses)
    return render_template('profile.html', user=current_user, courses=courses)

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

    login_user(new_user, remember=True)
    return redirect(url_for('setup'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/data')
def data():
    with open('data/data.json', 'r', encoding='utf-8') as f:
        _data = f.read()
    return _data

def get_course_tree():
    course_tree = {}
    course_data = json.loads(data())
        
    for crn, value in course_data.items():
        course_name = value["subject_code"] + "-" + value["course_number"]
        prereq_strings = re.split(r"AND\s|OR\s", value["prereqs"], flags=re.IGNORECASE)

        prereqs = [
            str.join("-", prereq_str.split(" ")[:2]) for prereq_str in prereq_strings
        ]

        if (len(prereqs) > 1):
            print(prereq_strings)
            print("Value: ")
            print(value)
            print("Prereqs: ")
            print(prereqs)

        if (course_name not in course_tree):
            course_tree[course_name] = {
                "course_name": course_name,
                "prereqs": prereqs
            }

    return course_tree

@app.route('/tree')
def tree():
    # course = request.args.get('course')
    course_tree = get_course_tree()
    return render_template('tree.html', course_tree=course_tree, seed_course="CS-370")