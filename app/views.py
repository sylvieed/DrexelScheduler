from flask import redirect, render_template, request, url_for
from . import app

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/tree")
def tree():
    return render_template('tree.html')