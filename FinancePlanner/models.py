from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))

    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    xp_needed = db.Column(db.Integer, default=100)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))
    description = db.Column(db.String(200))
    date = db.Column(db.Date, default=date.today)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    target_amount = db.Column(db.Float)
    current_amount = db.Column(db.Float, default=0)
    description = db.Column(db.String(300))
    priority = db.Column(db.Integer, default=0)


class DailyLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.Date)


class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))