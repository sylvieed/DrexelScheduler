from app import db

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String)
    course_number = db.Column(db.String)
    title = db.Column(db.String)
    description = db.Column(db.String)
    credits = db.Column(db.String)
    prereqs = db.Column(db.String)
    repeat_status = db.Column(db.String)
    college_department = db.Column(db.String)
    restrictions = db.Column(db.String)