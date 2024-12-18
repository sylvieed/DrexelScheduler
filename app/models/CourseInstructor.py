from sqlalchemy import ForeignKey

import app


class CourseInstructor(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    course_id = app.db.Column(app.db.Integer, ForeignKey('courses.crn'))
    instructor_id = app.db.Column(app.db.Integer, ForeignKey('instructors.id'))
