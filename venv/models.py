from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func, expression


class Recovery_code(db.Model):
    __tablename__ = "recovery_code"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6))


class Booking(db.Model):
    __tablename__ = "booking"
    id = db.Column(db.Integer, primary_key=True)
    name_StudyRoom = db.Column(db.String(50), db.ForeignKey('room.name'))
    email_User = db.Column(db.String(100), db.ForeignKey('user.email'))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    confirmed = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, name_StudyRoom, email_User ):
        self.name_StudyRoom = name_StudyRoom
        self.email_User = email_User
        self.confirmed = False

    def not_confirmed(self):

        self.confirmed = False

    def yes_confirmed(self):

        self.confirmed = True

    def getconfirmed(self):
        return self.confirmed.__init__()

    def __str__(self):

        return "Booking id: {self.id} - name_StudyRoom = {self.name_StudyRoom} - Date: {self.date}".format(self=self)


class Room(db.Model):
    __tablename__ = "room"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    status = db.Column(db.Integer)
    description = db.Column(db.String(500))
    confirmation_code = db.Column(db.String(10))
    requested_booking = db.relationship('Booking', backref="Room.id")
    internet = db.Column(db.String(5))
    ac = db.Column(db.String(5))
    socket = db.Column(db.String(5))
    vending_machine = db.Column(db.String(5))
    bathroom = db.Column(db.String(5))
    heating_system = db.Column(db.String(5))
    address = db.Column(db.String(200))
    text_borrowing = db.Column(db.String(5))
    copy_machine = db.Column(db.String(5))
    Smartcard_services = db.Column(db.String(5))
    Phone = db.Column(db.String(30))
    Opening = db.Column(db.String(300))
    nearby_places = db.Column(db.String(2000))

    def add_number_booking(self):
        self.status = self.status + 1

    def decrease_number_booking(self):
        self.status = self.status - 1


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.BINARY(60), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    requested_booking = db.relationship('Booking', backref="User.id")
    counter_booking = db.Column(db.Integer)

    def one_more_booking(self):

        self.counter_booking = self.counter_booking + 1
