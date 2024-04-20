import app

class Instructors(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String)
    avg_difficulty = app.db.Column(app.db.Float)
    avg_rating = app.db.Column(app.db.Float)
    num_ratings = app.db.Column(app.db.Integer)
    rpm_id = app.db.Column(app.db.Integer)
    
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
    start_time = app.db.Column(app.db.DateTime)
    end_time = app.db.Column(app.db.DateTime)
    days = app.db.Column(app.db.String) # This was array in the original schema... so this is wrong

class CourseInstructor(app.db.Model):
    course_id = app.db.Column(app.db.Integer, ForeignKey('courses.crn'))
    instructor_id = app.db.Column(app.db.Integer, ForeignKey('instructors.id'))
