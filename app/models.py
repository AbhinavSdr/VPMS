from flask import current_app
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from random import randint


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique= True, nullable = False)
    email = db.Column(db.String(120), index=True, unique=True)
    name = db.Column(db.String(64), index = True, nullable = False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), nullable=False, index=True)
    #parkinghistorys = db.relationship('ParkingHistory')

    def __repr__(self):
        return '<User %r>' % self.id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class ParkingSlot(db.Model):
    __tablename__ = 'parkingslot'
    id = db.Column(db.Integer, primary_key=True)
    rc = db.Column(db.String(10), index = True, unique = True, nullable=False)
    phone = db.Column(db.String(10), index = True, unique = True, nullable=False)
    name = db.Column(db.String(20), index = True, nullable=False)
    entry_empname = db.Column(db.String(64), index = True, nullable=False)
    entry_time = db.Column(db.DateTime, index = True, nullable=False)
    entry_epoch = db.Column(db.Integer, index = True, nullable=False)

    def __repr__(self):
        return '<ParkingSlot %r>' % self.id

class ParkingHistory(db.Model):
    __tablename__ = 'parkinghistory'
    id = db.Column(db.Integer, primary_key= True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rc = db.Column(db.String(10), index = True, nullable = False)
    phone = db.Column(db.String(10), index = True, nullable = False)
    name = db.Column(db.String(20), index = True, nullable = False)
    entry_empname = db.Column(db.String(64), index = True, nullable = False)
    entry_time = db.Column(db.DateTime, nullable = False, index = True)
    exit_empname = db.Column(db.String(64), index = True, nullable = False)
    exit_time = db.Column(db.DateTime, nullable = False, index = True)
    time_stayed = db.Column(db.String(30), nullable=False, index=True)
    parking_charge = db.Column(db.Float, index=True, nullable = False)
    
    def __repr__(self):
        return '<ParkingHistory %r>' % self.id

class ParkingPrice(db.Model):
    __tablename__ = 'parkingprice'
    id = db.Column(db.Integer, primary_key = True)
    date_updated = db.Column(db.DateTime, nullable = False, index = True)
    charge = db.Column(db.Float, nullable = False)

    def __repr__(self):
        return '<ParkingPrice %r>' % self.id

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), index = True, nullable = False)
    charge = db.Column(db.Float, nullable = False)
    paid = db.Column(db.String(10), index = True, nullable = False)
    paymentDate = db.Column(db.DateTime, nullable = True, index = True)
    paymentType = db.Column(db.String(10), index = True, nullable = True)
    paymentID = db.Column(db.Integer)


    def __repr__(self):
        return '<Payment %r>' % self.id