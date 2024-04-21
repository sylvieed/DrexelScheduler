import json
from openai import OpenAI

client = OpenAI()

# Load the JSON data from a file
with open('/Users/ilsa/vscode/test/elective_courses.json', 'r') as file:
    courses = json.load(file)

# Function to create a brief description for each course
def create_course_summary(course_data):
    days = ", ".join(course_data["days"]) if course_data["days"] else "No specific days"
    if course_data['instructors'] and all(course_data['instructors']):
        instructor_names = ', '.join(instructor['name'] for instructor in course_data['instructors'] if instructor and 'name' in instructor)
    else:
        instructor_names = "No instructors listed"
    return (f"Course {course_data['subject_code']} {course_data['course_number']} titled '{course_data['course_title']}'"
            f" covers {course_data['description']} Scheduled on {days} from {course_data['start_time']} to {course_data['end_time']}"
            f" instructed by {instructor_names}.")

#create summary in one sentence & join into one string
course_descriptions = '; '.join(create_course_summary(course) for course in courses.values())

#(per response) -> connect frontend input
user_preference = "I am interested in courses about computer security, available online and only have 3 credits"

#create prompt for AI to answer
prompt = (f"Given the preferences: {user_preference}, which of these courses is the best match? {course_descriptions}")

#GPT 3.5-Turbo does the mapping/answering
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": user_preference},
        {"role": "system", "content": course_descriptions}
    ]
)

print(response)