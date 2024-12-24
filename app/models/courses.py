from app import db
from app.models.course_instructor import CourseInstructor
from app.models.instructors import Instructors

class Courses(db.Model):
    crn = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String)
    course_number = db.Column(db.String)
    instruction_type = db.Column(db.String)
    instruction_method = db.Column(db.String)
    section = db.Column(db.String)
    enroll = db.Column(db.String)
    max_enroll = db.Column(db.String)
    course_title = db.Column(db.String)
    credits = db.Column(db.String)
    prereqs = db.Column(db.String)
    start_time = db.Column(db.String)
    end_time = db.Column(db.String)
    days = db.Column(db.String) # Comma separated list of days
    quarter = db.Column(db.String)
    description = db.Column(db.String)

    def instructor(self):
        ins = CourseInstructor.query.filter_by(course_id=self.crn).first()
        if ins:
            return Instructors.query.filter_by(id=ins.instructor_id).first()
        return None

    def avg_rating(self):
        instructor = self.instructor()
        if instructor:
            return instructor.avg_rating
        return None

    def avg_difficulty(self):
        instructor = self.instructor()
        if instructor:
            return instructor.avg_difficulty
        return None