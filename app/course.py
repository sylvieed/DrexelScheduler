from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, jsonify
)
from flask_sqlalchemy import SQLAlchemy
import json
import re
from app.models.courses import Courses
from app.prereq_ast_generator import (
    get_prereq_ast, get_all_courses, get_all_courses_w_ast, Course
)

view_bp = Blueprint('course', __name__, url_prefix='/course')
api_bp = Blueprint('api', __name__, url_prefix='/api')

def get_course(subject_code: str, course_number: int) -> Courses:
    db: SQLAlchemy = current_app.extensions['sqlalchemy']

    course = (db.session.query(Courses)
        .filter(Courses.subject_code == subject_code.upper())) \
        .filter(Courses.course_number == course_number) \
        .first()

    return course

@view_bp.route('/<subject_code>-<int:course_number>')
def course(subject_code, course_number):
    course = get_course(subject_code, course_number)
    return render_template('course.html', course=course)

@view_bp.route('/tree')
def tree():
    # course = request.args.get('course')
    course_tree = get_course_tree()
    return render_template('tree.html', course_tree=course_tree, seed_course="CS-370")

@view_bp.route('/data')
def data():
    with open('data/data.json', 'r', encoding='utf-8') as f:
        _data = f.read()
    return _data

def get_course_name(course: Courses):
    return f'{course.subject_code}-{course.course_number}'

def get_course_prereq_dict(seed_course: Courses, prereq_dict={}):
    try:
        prereq_tree = get_prereq_ast(seed_course.prereqs)
    except:
        # TODO: Somehow show that the prerequisites couldn't be parsed
        # so that the endpoint knows that there might be more prereqs.
        return prereq_dict

    seed_course_name = get_course_name(seed_course)
    prereq_dict[seed_course_name] = prereq_tree

    for course_ast in get_all_courses_w_ast(prereq_tree):
        course = get_course(course_ast.subject_code, course_ast.course_number)

        if course is not None:
            course_name = get_course_name(course)

            if course_name not in prereq_dict:
                get_course_prereq_dict(course, prereq_dict)

    return prereq_dict

@api_bp.route('/get_course_tree/<subject_code>-<int:course_number>')
def get_course_tree_api(subject_code, course_number):
    seed_course = get_course(subject_code, course_number)

    if seed_course is None:
        return jsonify({})

    course_json = {
        "subject_code": seed_course.subject_code,
        "course_number": seed_course.course_number,
        "seed_course": get_course_name(seed_course),
        "prereq_trees": get_course_prereq_dict(seed_course)
    }

    # TODO: Figure out how to convert all objects in the json to dictionaries in a better way.
    # This feels very weird converting to a json string and back to a dictionary just to use
    # the encoder.
    course_json = json.loads(json.dumps(course_json, default=lambda o: o.__dict__))

    return jsonify(course_json)

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

@view_bp.route('/test_tree/<subject_code>-<int:course_number>')
def test_tree(subject_code, course_number):
    seed_course = get_course(subject_code, course_number)
    return render_template('test_tree.html', seed_course=seed_course)