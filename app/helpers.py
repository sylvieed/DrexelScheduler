from . import db, User, Courses
import json
import re

def get_course(course_string):
    vals = course_string.split(' ')
    if len(vals) != 2:
        return None
    subject_code, course_number = vals[0], vals[1]
    return db.session.query(Courses).filter_by(subject_code=subject_code, course_number=course_number).first()

def get_course_tree(course):
    course_tree = {}
    with open('data.json', 'r', encoding='utf-8') as data_file:
        course_data = json.load(data_file)
        
        for crn, value in course_data.items():
            course_name = value['subject_code'] + '-' + value['course_number'] + '-' + value['section']
            prereqs = re.split(r'AND|OR', value['prereqs'], flags=re.IGNORECASE)

            print(prereqs)


    return course.prerequisites.split(',')