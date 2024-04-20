import database  

if __name__ == '__main__':
    database.setup_database()
    database.add_data("data.json")
