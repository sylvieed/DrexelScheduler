import sqlite3

try:
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()


    with open('setup.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    cursor.executescript(sql_script)
    conn.commit()
    print('Database setup completed')
    
except sqlite3.Error as e:
    print(e)
finally:
    conn.close()