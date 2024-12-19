import app


class User(app.db.Model):
    id = app.db.Column(app.db.Integer, primary_key=True)
    email = app.db.Column(app.db.String)
    password = app.db.Column(app.db.String)
    name = app.db.Column(app.db.String)
    major = app.db.Column(app.db.String)
    year = app.db.Column(app.db.Integer)

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anoymous(self):
        return False
    def get_id(self):
        return self.id
