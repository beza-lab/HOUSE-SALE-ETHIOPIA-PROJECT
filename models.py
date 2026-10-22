from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class House(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(db.String(200))

    price = db.Column(db.Float)

    city = db.Column(db.String(100))

    address = db.Column(db.String(200))

    bedrooms = db.Column(db.Integer)

    bathrooms = db.Column(db.Integer)

    description = db.Column(db.Text)

    image = db.Column(db.String(300))

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    def __repr__(self):
        return f"<House {self.title}>"
        

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="seller"
    )