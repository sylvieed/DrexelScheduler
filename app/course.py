from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from flask_sqlalchemy import SQLAlchemy
import json
import re
from app.models.courses import Courses

bp = Blueprint('course', __name__, url_prefix='/course')

def get_course_data(subject_code: str, course_number: int) -> Courses:
    db: SQLAlchemy = current_app.extensions['sqlalchemy']

    course = (db.session.query(Courses)
        .filter(Courses.subject_code == subject_code.upper())) \
        .filter(Courses.course_number == course_number) \
        .first()

    return course

@bp.route('/<subject_code>-<int:course_number>')
def course(subject_code, course_number):
    course = get_course_data(subject_code, course_number)
    return render_template('course.html', course=course)

@bp.route('/tree')
def tree():
    # course = request.args.get('course')
    course_tree = get_course_tree()
    return render_template('tree.html', course_tree=course_tree, seed_course="CS-370")

@bp.route('/data')
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


