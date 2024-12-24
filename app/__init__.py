import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # 'qefjioamczuiavdbegui'
        DATABASE=os.path.join(app.instance_path, 'db.sqlite'),
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite'
    )

    # This will create the database file using SQLAlchemy
    # (Uncomment this once to create the database file)
    # from app import models
    # with app.app_context():
    #     db.drop_all()
    #     db.create_all()

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    # Register blueprints
    from . import course
    app.register_blueprint(course.view_bp)
    app.register_blueprint(course.api_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)

# Set up the login manager from flask_login
from app.models.user import User
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Set up the password hashing using flask_bcrypt
bcrypt = Bcrypt(app)

from app import views
