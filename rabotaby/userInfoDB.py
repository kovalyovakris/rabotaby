from database import db

#бд для профиля пользователя по логину
class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    photo_path = db.Column(db.String(200))
    document_path = db.Column(db.String(200))