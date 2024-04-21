import json

#load json (use the sample data for now)
with open('/Users/ilsa/vscode/test/data-2.json', 'r') as file:
    data = json.load(file)

#filter out courses that have prereqs
filtered_courses = {crn: details for crn, details in data.items() if not details['prereqs']}

#save data to a new JSON file
with open('elective_courses.json', 'w') as file:
    json.dump(filtered_courses, file, indent=4)

print("Filtered courses have been saved to 'elective_courses.json'")
