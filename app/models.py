import app
from sqlalchemy import ForeignKey

class Instructors(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String)
    avg_difficulty = app.db.Column(app.db.Float)
    avg_rating = app.db.Column(app.db.Float)
    num_ratings = app.db.Column(app.db.Integer)
    rmp_id = app.db.Column(app.db.Integer)
    
class Courses(app.db.Model):
    crn = app.db.Column(app.db.Integer, primary_key=True)
    subject_code = app.db.Column(app.db.String)
    course_number = app.db.Column(app.db.String)
    instruction_type = app.db.Column(app.db.String)
    instruction_method = app.db.Column(app.db.String)
    section = app.db.Column(app.db.String)
    enroll = app.db.Column(app.db.String)
    max_enroll = app.db.Column(app.db.String)
    course_title = app.db.Column(app.db.String)
    credits = app.db.Column(app.db.String)
    prereqs = app.db.Column(app.db.String)
    start_time = app.db.Column(app.db.String)
    end_time = app.db.Column(app.db.String)
    days = app.db.Column(app.db.String) # This was array in the original schema... so this is wrong

class CourseInstructor(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    course_id = app.db.Column(app.db.Integer, ForeignKey('courses.crn'))
    instructor_id = app.db.Column(app.db.Integer, ForeignKey('instructors.id'))

class User(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    email = app.db.Column(app.db.String)
    password = app.db.Column(app.db.String)
    name = app.db.Column(app.db.String)
    major = app.db.Column(app.db.String)
    year = app.db.Column(app.db.Integer)

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anoymous(self):
        return False
    def get_id(self):
        return self.id

class UserCourse(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    user_id = app.db.Column(app.db.Integer, ForeignKey('user.id'))
    grade = app.db.Column(app.db.String)
    course_id = app.db.Column(app.db.Integer, ForeignKey('courses.crn'), nullable=True)
    subject_code = app.db.Column(app.db.String)
    course_number = app.db.Column(app.db.String)
