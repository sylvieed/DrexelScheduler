import sqlite3
import json

def setup_database():
    try:
        conn = sqlite3.connect('mydatabase.sqlite')
        cursor = conn.cursor()


        with open('data/setup.sql', 'r') as sql_file:
            sql_script = sql_file.read()

        cursor.executescript(sql_script)
        conn.commit()
        print('Database setup completed')
        
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()


def add_data(data_path, quarter="spring"):
    try:
        # Load data from JSON file
        with open(data_path, 'r') as file:
            data = json.load(file)


        conn = sqlite3.connect('../instance/db.sqlite')
        cursor = conn.cursor()
        
        for crn, value in data.items():
            # Check if days is a list
            days = value['days']
            if not isinstance(days, list):  # If days is not a list
                days = [days] if days is not None else []  # Convert to list or empty list if None

            days_str = ','.join(days)

            # Insert course data
            cursor.execute('''
                INSERT INTO courses (crn, subject_code, course_number, instruction_type, instruction_method, 
                    section, enroll, max_enroll, course_title, credits, prereqs, start_time, end_time, description, days, quarter) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (crn, value['subject_code'], value['course_number'], value['instruction_type'], value['instruction_method'], 
                value['section'], value['enroll'], value['max_enroll'], value['course_title'], value['credits'], value['prereqs'], 
                value['start_time'], value['end_time'], value['description'], days_str, quarter))
            
            if not value['instructors']:  # If instructors is empty
                    continue
            
            # Insert instructor data (only the first instructor)
            instructor = value['instructors'][0]

            instructor_name = instructor['name']

            if instructor['rating']:
                avg_difficulty = instructor['rating'].get('avgDifficulty')  # Could be None
                avg_rating = instructor['rating'].get('avgRating')  # Could be None
                num_ratings = instructor['rating'].get('numRatings')  # Could be None
                rmp_id = instructor['rating'].get('legacyId')  # Could be None

            cursor.execute('''
                INSERT OR IGNORE INTO instructors (name, avg_difficulty, avg_rating, num_ratings, rmp_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (instructor_name, avg_difficulty, avg_rating, num_ratings, rmp_id))
            
            instructor_id = cursor.execute('''
                SELECT id FROM instructors WHERE name = ?
            ''', (instructor_name,)).fetchone()[0]
        
            # Insert course-instructor relationship
            cursor.execute('''
                INSERT INTO course_instructor (course_id, instructor_id)
                VALUES (?, ?)
            ''', (crn, instructor_id))


        conn.commit()
        print('Data added successfully')
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()




