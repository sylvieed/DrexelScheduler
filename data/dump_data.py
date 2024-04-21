import database

if __name__ == '__main__':
    # database.setup_database()
    print("Adding fall data")
    database.add_data("fall.json")
    # print("Adding winter data")
    # database.add_data("winter.json")
    print("completed adding data")
