import app

class Instructors(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    name = app.db.Column(app.db.String)
    avg_difficulty = app.db.Column(app.db.Float)
    avg_rating = app.db.Column(app.db.Float)
    num_ratings = app.db.Column(app.db.Integer)
    rmp_id = app.db.Column(app.db.Integer)
