from . import db, User, Courses

def get_course(course_string):
    vals = course_string.split(' ')
    if len(vals) != 2:
        return None
    subject_code, course_number = vals[0], vals[1]
    return db.session.query(Courses).filter_by(subject_code=subject_code, course_number=course_number).first()