from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Set up the database using SQLAlchemy
db = SQLAlchemy()
app.config['SECRET_KEY'] = 'qefjioamczuiavdbegui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)

# This will create the database file using SQLAlchemy
# (Uncomment this once to create the database file)
# from app import models
# with app.app_context():
#     db.drop_all()
#     db.create_all()

# Set up the login manager from flask_login
from .models import User
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Set up the password hashing using flask_bcrypt
bcrypt = Bcrypt(app)

from app import views