from sqlalchemy import ForeignKey

import app


class UserCourse(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    user_id = app.db.Column(app.db.Integer, ForeignKey('user.id'))
    grade = app.db.Column(app.db.String)
    course_id = app.db.Column(app.db.Integer, ForeignKey('courses.crn'), nullable=True)
    subject_code = app.db.Column(app.db.String)
    course_number = app.db.Column(app.db.String)
