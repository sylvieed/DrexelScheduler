import json
from openai import OpenAI

client = OpenAI()

# Load the JSON data from a file
with open('ai/elective_courses.json', 'r') as file:
    courses = json.load(file)

# Function to create a brief description for each course
def create_course_summary(course_data):
    days = ", ".join(course_data["days"]) if course_data["days"] else "No specific days"
    if course_data['instructors'] and all(course_data['instructors']):
        instructor_names = ', '.join(instructor['name'] for instructor in course_data['instructors'] if instructor and 'name' in instructor)
    else:
        instructor_names = "No instructors listed"
    return (f"Course {course_data['subject_code']} {course_data['course_number']} titled '{course_data['course_title']}'"
            f" covers {course_data['course_description']} Scheduled on {days} from {course_data['start_time']} to {course_data['end_time']}"
            f" instructed by {instructor_names}.")

#create summary in one sentence & join into one string
course_descriptions = '; '.join(create_course_summary(course) for course in courses.values())

def strip_response(response):
    start_index = response.find('content="') + len('content="')
    end_index = response.find('", ')
    print(start_index, end_index)
    return response[start_index:end_index] if start_index != -1 and end_index != -1 else None

def ai_electives(query):
    #create prompt for AI to answer
    prompt = (f"Given the preferences: {query}, which of these courses is the best match? {course_descriptions}")

    #GPT 3.5-Turbo does the mapping/answering
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query},
            {"role": "system", "content": course_descriptions}
        ]
    )

    print(str(response))

    return strip_response(str(response))
