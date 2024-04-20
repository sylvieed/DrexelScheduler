import sqlite3

try:
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    # Execute commands
    conn.commit()
except sqlite3.Error as e:
    print(e)
finally:
    conn.close()