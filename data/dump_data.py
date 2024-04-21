import database

if __name__ == '__main__':
    # database.setup_database()
    print("Adding fall data")
    database.add_data("fall.json", "fall")
    print("Adding spring data")
    database.add_data("spring.json", "spring")
