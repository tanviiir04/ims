from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, name, position, username, password):
        self.name = name
        self.position = position
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20))
    category = db.Column(db.String(20))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20))
    resolved_at = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    sla_deadline = db.Column(db.DateTime)
