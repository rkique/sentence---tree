from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    embedding = db.Column(db.PickleType, nullable=True)
    day = db.Column(db.Integer, nullable=False)