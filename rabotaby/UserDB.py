from database import db
from flask_login import UserMixin

# бд для рег/авторизации
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    login = db.Column(db.String(100),unique=True, nullable = False)
    password = db.Column(db.String(255), nullable = False)

    def __repr__(self):
        return '<User %r>' % self.id
