from flask import redirect, render_template, request, url_for
from . import app

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/scheduler')
def scheduler():
    courses = Courses.query.all()
    return render_template('scheduler.html', courses=courses)