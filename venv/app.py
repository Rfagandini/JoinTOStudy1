
import os
import random
import string
import json
import datetime
import re, bcrypt

from flask import Flask, render_template, flash, session, redirect, url_for, request, jsonify
from formx import Registrationform, Loginform, Confirmation_code, recover_password_form, code_verification_form, changing_password
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy import func
from flask_mail import Mail, Message
from flask_socketio import SocketIO, join_room, leave_room, emit
from datetime import date


# try:
#     json.load()
# except ValueError:
#     print("error")

from os import path


DB_NAME = "database.db"
os.environ['password'] = "mail0480*"

app = Flask(__name__)

app.config['SECRET_KEY'] = "Management Engineering"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_USERNAME'] = "BookTOStudy@mail.com"
app.config['MAIL_PASSWORD'] = os.getenv('password')
app.config['MAIL_TLS'] = True
app.config['MAIL_SERVER'] = 'smtp.mail.com'
app.config['MAIL_PORT'] = 587

db = SQLAlchemy(app)
mail = Mail(app)
socketio = SocketIO(app, manage_session=False)

from models import *


@app.before_first_request
def create_db():

    print("entered")

    # confirmation_code="#$%303"
    # confirmation_code="609TOR"
    # confirmation_code="3TBOP4"

    if not path.exists('database.db'):
        db.drop_all()
        db.create_all()

        description_verdi="Placed in the city centre, just near Piazza Vittorio Veneto, next to Palazzo Nuovo, one of the headquarters of the University of Torino. It is a very nice place to study, quite and you can find easily electrical outlets. It is attended by university students coming from different department. It can be easily reached by different transport service and nearby you can find places to eat, drink or simply taking a break in front of river Po."
        description_grugliasco=" Located in the city of Grugliasco, in the outsides of Turin, you can book a seat in this charm study room." \
                               " Considered the calmest by the students, it can be the best choice to concentrate better "
        description_sansalvario=" Also known as the 'Bunker', it is a bit stretch but it's located in the heart of one of the most lively neighborhoods of Turin!"
        description_marcopolo=" Test study room to try capacity limitation demonstration "

        description_opera = "Study room located in the city centre, near Nizza subway station, next to the medicine"\
                            "department and chemistry departments of the University of Turin. Just by walking for a few minutes, you"\
                            "can easily reach the Valentino Park, a large park where you can"\
                            "have a relaxing break with your friends or"\
                            "simply enjoy the picturesque view beside the river. Here you can also visit Borgo Medievale and Castello del"\
                            "Valentino which is the headquarter of the architecture department of Politecnico di Torino. Nearby you can"\
                            "find everything that a student may need; supermarkets, print shops, bars, pizzerias etc"

        description_galliari= "Study room located in the city centre, just by walking for a few minutes, you can easily reach"\
                            "the Valentino Park, a large park where you can have a relaxing break with your friends or simply enjoy the"\
                            "picturesque view beside the river. Here you can also"\
                            "visit Borgo Medievale and Castello del Valentino,"\
                            "which is headquarter of the architecture department of Politecnico di Torino. By walking for a while, you"\
                            "can reach the San Salvario district, which is full of bars and other places where you can go for an aperitif,"\
                            "eat a pizza or enjoy some traditional Piedmonese dishes."
        description_comala='It is a public space that includes rehearsal rooms, a recording studio, laboratory dedicated rooms and a very large outdoor courtyard where students coming from different universities study during all day. Here you can find a place where to meet new friends, study with colleagues without disturbing the others. Inside the building it is possible to also find small study rooms, quieter than the external seats, dedicated to a more focused study. The outside seats are covered, so during rainy days the study is guaranteed as well. It is possible to find a bar inside the building. There are available places where to refill your water bottle for free, so it is a "green" place.  Around 7:00 p.m. an aperitif is started, so it is not possible to study anymore, except of the internal places. In the evening, there is the projection of some films, where you can drink a beer with your friends or meet new ones. This is the right place for a person new in Turin that wants to meet new friends. '

        description_murazzi = 'This study room is located in the city centre, in front of River Po, in the so-called "Murazzi del Po". It is a very quiet place to study, next to Piazza Vittorio Veneto. It is attended by university students coming from different departments since it is well connected and easily reachable by the city transport service. Next to it, it is possible to find any type of bars to drink cocktails in front of river Po. In some of them, there is also an aperitif service.'

        description_castelfidardo = "Two different study rooms placed in Corso Castelfidardo, part of the Politecnico di Torino, located in the first and second floor of the building. These study rooms are available only if booked by"\
                                    "PoliTo students, due to the nowadays pandemic. Each student can book these study rooms and study also"\
                                    "during the lecture breaks, since they"\
                                    "are located in the same university building. They offer a quiet place to"\
                                    "study, large seats and sockets available for each place. If you want to take a break, you can take a coffee to"\
                                    'different bars present in Politecnico or have lunch at the Mensa "Universitaria Castelfidardo".'

        description_aula_studio_1 = "Placed in the main headquarter of Politecnico di Torino, this study room is available only if booked by PoliTo students only. It is also called 'aula studio rumorosa' since here you can find a lot of students that study for project work, and so they need a place where they are able to discuss. It's the right place to study with friends. In the same building, you can find the CLUT library, for books and office suppliers, the Copysprinter, copy shop and a place to find notes written by colleagues, and different bars placed in Politecnico. Inside the university, it is also possible to find a university library to borrow books."

        nearby_places_aula_studio_1 = "La cafeteria (https://goo.gl/maps/ktHw8ZP2r3C6nRPv9)"\
                                        "Bar Denise (https://goo.gl/maps/cnSu2Ek7fgZjXqiu6)"\
                                        "Bar Tropical (https://g.page/BAR-Tropical-Torino?share)"\
                                        "Nelida bistrot (https://goo.gl/maps/qjBCXvWtoD1L7crx9)"\
                                        "Mensa Universitaria Castelfidardo (https://goo.gl/maps/cisit67UxPACJX3u5)"\
                                        "Bar Fulwer Design (https://g.page/FulwerDesignBar?share)"\
                                        "CLUT (https://goo.gl/maps/mmf2SoyTrayPEAEEA)"\
                                        "Levrotto & Bella Libreria Editrice Universitaria (https://goo.gl/maps/7wavbGYrGvtHSp2p9)"\
                                        "Copysprinter Politecnico (https://goo.gl/maps/TfonXP7tXMst3S4q6)"\
                                        "Epic s.a.s. centro appunti (https://goo.gl/maps/TnEk3DhhiDkusuLj8)."

        nearby_places_opera = "Carrefour Market (supermarket) (https://goo.gl/maps/Hiu3VHyrbfWJWfZQ9) Ins market (https://goo.gl/maps/oJzq3dx8mh96kEWX7Favuri') Quality Pizza & Street Food (https://goo.gl/maps/f6P2G1LMRFz1qNzo6) Panfe' (https://goo.gl/maps/WH7FTHXS9n6kVMpa8) Gelateria la Romana (dessert and ice creams) (https://goo.gl/maps/BUvn1vcmUbAVLSZB9) La vie en rose (https://goo.gl/maps/hsoPb49J8z5bhRr16) Caffe' degli atenei (https://g.page/caffedegliatenei?share) Copysprinter Giuria (https://g.page/copysprintergiuria?share) Copisteria & Eliografia dello Studente (https://g.page/copisteriadellostudente?share) Copirema (https://g.page/copirema?share)"

        nearby_places_verdi = "Piazza Vittorio Veneto with different bars for aperitif or drink only on both sides of the square (https://goo.gl/maps/5ZUdZL2fSn8676hR7)" \
                              "McDonald's Torino Sant'Ottavio (https://goo.gl/maps/sTKEW9RXZrBcSB1L6)"\
                              "Burger King (https://g.page/burgerkingtorinocentro?share)"\
                              "Pacific Poke Restaurant Verdi (https://g.page/pacifik-poke-restaurant?share)"\
                              "Caffe' Elena (https://goo.gl/maps/VfZJkt6VGvxuA2hGA)"\
                              "Caffe' Verdi (https://g.page/caffeverdi-to?share)"\
                              "Denim bar (https://maps.app.goo.gl/fHqFAuVy5AZUjzw1A)"\
                              "Alice Pizza Torino Universita' (https://maps.app.goo.gl/tj4bxRLTgF5D2sjh6)"\
                              "Curry & Co (https://maps.app.goo.gl/4g6xTXgAUS3AKED96)"\
                              "Ecoduemila (https://goo.gl/maps/WPKACfiZSGN3eA4z7)"\
                              "Copy Digital Snc (https://g.page/Copydigital?share)"



        nearby_places_galliari ="Nearby places"\
                                "Supermercato Carrefour Express "\
                                "(https://goo.gl/maps/poApaFNpUqujqyGMA)"\
                                "Trattoria Carmen"\
                                "(https://goo.gl/maps/fPF3yWUepvPq4vvy8) "\
                                "Trattoria Bar Coco's (https://goo.gl/maps/kLGphKJaRBB1qouu8)"\
                                "Pizza speedy (https://goo.gl/maps/bG2DjUjvJj8sMrQE6)"\
                                "Siciloso Pasticceria Siciliana (https://goo.gl/maps/21fGXTLX6vTT3ihR9)"

        nearby_places_castello = "Imbarchino (https://g.page/imbarchino?share)"\
                                "Bar Castello del Valentino (https://goo.gl/maps/4xUN1r3WkiMpckkD9)"\
                                "The River (https://g.page/the-river-torino?share)"\
                                "Il Ritrovo (https://goo.gl/maps/fyVBMSNF16Kfkfbt7)"\
                                "Ristorante Cibo Container (https://goo.gl/maps/Cd9z5okw4EoEGxMcA)"\
                                "Eliografia Rossi di Rossi Paolo (https://g.page/eliografiarossitorino?share)"\
                                "Ins Mercato (https://goo.gl/maps/6uyZRZhx81N3thJr9)"\
                                "Plottergrafica Centro Stampa (https://g.page/Plottergrafica?share)"\
                                "Copysprinter Vochieri (https://g.page/copysprinter-vochieri?share)"\
                                "B-Evolution (https://goo.gl/maps/taJj2zGakLU4i1jk9)"\
                                "Caffe 95 (https://goo.gl/maps/tBjAip28buaWqwAs5)"\
                                "La birroteca (https://goo.gl/maps/qQUf6UqmsKf7kfSX7)"

        nearby_places_murazzi = "Piazza Vittorio Veneto with different bars for aperitif or drink only on both sides of the square (https://goo.gl/maps/5ZUdZL2fSn8676hR7)"\
                                "McDonald's Torino Sant'Ottavio (https://goo.gl/maps/sTKEW9RXZrBcSB1L6)"\
                                "Burger King (https://g.page/burgerkingtorinocentro?share)"\
                                "Pizzium Torino via Bava (https://goo.gl/maps/x5mZrodZSJRGePgL9)"\
                                "Pacific Poke Restaurant Verdi (https://g.page/pacifik-poke-restaurant?share)"\
                                "Mohito bar (https://g.page/cocktail-bar-torino?share)"\
                                "The globe Coffee&Restaurant (https://goo.gl/maps/ZCyvPA7YqkGpiktg6)"\
                                "Ecoduemila (https://goo.gl/maps/WPKACfiZSGN3eA4z7)"\
                                "Copy Digital Snc (https://g.page/Copydigital?share)"\
                                "Copysprinter Rosine (https://g.page/copysprinter-rosine?share)"\

        nearby_places_comala =  "Supermercato Carrefour Express (https://goo.gl/maps/6ogPL6QK86U8zkQQ6)"\
                                "In's Mercato (https://goo.gl/maps/6uyZRZhx81N3thJr9)"\
                                "Plottergrafica Centro Stampa (https://g.page/Plottergrafica?share)"\
                                "Copysprinter Vochieri (https://g.page/copysprinter-vochieri?share)"\
                                "B-Evolution (https://goo.gl/maps/taJj2zGakLU4i1jk9)"\
                                "Caffe 95 (https://goo.gl/maps/tBjAip28buaWqwAs5)"\
                                "La birroteca (https://goo.gl/maps/qQUf6UqmsKf7kfSX7)"

        nearby_places_castelfidardo = "Mensa Universitaria Castelfidardo (https://goo.gl/maps/cisit67UxPACJX3u5)"\
                                    "Paninoteca Fuoricorso (https://g.page/paninotecafuoricorsotorino?share)"\
                                    "Paninoteca 30 e lode (https://goo.gl/maps/RPEkUR7WWZZ87L3w7)"\
                                    "Arki cafe (https://goo.gl/maps/XJWmrsPE9KDimiwU6)"\
                                    "Aldo's bakery (https://goo.gl/maps/nXY1cM3aQkFAZrZBA)"\
                                    "MixTo (https://goo.gl/maps/AKf8sgLzFUD5eJps8)"\
                                    "Plottergrafica Centro Stampa (https://g.page/Plottergrafica?share)"\
                                    "Copy Break (https://g.page/copisteria_boggio?share)"\
                                    "Copysprinter Politecnico (https://goo.gl/maps/TfonXP7tXMst3S4q6)"



        aula_verdi = Room(name="verdi", capacity=143, description=description_verdi, confirmation_code="#$%303", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes", heating_system="Yes", address="via Verdi, 26 - 10124 Torino", copy_machine="Yes", text_borrowing="No", Smartcard_services="Yes", Phone="+39 011 6531290", Opening="Monday-Friday: 8:30 AM to 00:00 AM. On public holidays, Sundays and Saturdays from 8:30 AM to 10:00 PM"
                          , nearby_places=nearby_places_verdi, location="https://www.google.com/maps/place/Via+Giuseppe+Verdi,+26,+10124+Torino+TO/@45.0673271,7.6928687,17z/data=!3m1!4b1!4m5!3m4!1s0x47886d62e84b7e0f:0x3acc507af920dd65!8m2!3d45.0673271!4d7.6950574")

        aula_galliari = Room(name="Galliari", capacity=134, description=description_galliari, confirmation_code="098765",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes",
                          heating_system="Yes", address="via Ormea 11 Bis/E-10125 Torino", copy_machine="Yes",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 011 6531291",
                          Opening="Monday-Friday: 9:00 AM to 22:00 PM. On public holidays, Sundays and Saturdays closed"
                          , nearby_places=nearby_places_galliari,
                          location="https://www.google.com/maps/place/Aula+Studio+Galliari/@45.0582907,7.6806791,16z/data=!4m9!1m2!2m1!1saula+studio+galliari+torino!3m5!1s0x47886d95c4f3c9e9:0x27e7c3f8054e41e3!8m2!3d45.0582886!4d7.6850623!15sChthdWxhIHN0dWRpbyBnYWxsaWFyaSB0b3Jpbm-SARJ1bml2ZXJzaXR5X2xpYnJhcnk")

        aula_opera = Room(name="Opera", capacity=184, description=description_opera, confirmation_code=")(*765",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes",
                          heating_system="Yes", address="via Michelangelo Buonarroti, 17 bis-10126 Torino", copy_machine = "Yes",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 0116531054",
                          Opening="Monday-Friday: 8:30 AM to 00:00 AM. On public holidays, Sundays and Saturdays from 8:30 AM to 10:00 PM", nearby_places=nearby_places_opera,
                          location="https://www.google.com/maps/place/Sala+Studio+Edisu+%22Opera%22/@45.0507869,7.6761632,17z/data=!3m1!4b1!4m5!3m4!1s0x47886d4589ff0761:0xd861e3118719bf6c!8m2!3d45.0507908!4d7.6783573")

        aula_castello = Room(name="Castello", capacity=198, description=description_opera, confirmation_code="000111",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="No", ac="Yes",
                          heating_system="Yes", address="Viale Mattioli, 39 - 10125 Torino TO ",
                          copy_machine="No",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 011 0906655",
                          Opening="Monday-Friday: 8:30 AM to 19:00 PM. On public holidays, Sundays and Saturdays it is closed",
                          nearby_places=nearby_places_castello,
                          location="https://www.google.com/maps/place/Viale+Mattioli,+39,+10125+Torino+TO/@45.0542606,7.6831836,17z/data=!3m1!4b1!4m5!3m4!1s0x47886d5ca7afffff:0x25e79696504e9779!8m2!3d45.0542568!4d7.6853723")

        # aula_grugliasco = Room(name="grugliasco", capacity=150, description=description_grugliasco, confirmation_code="609TOR", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes", heating_system="No", address="Via Berta, 5, 10095 Grugliasco TO")

        # aula_sansalvario = Room(name="sansalvario", capacity=200, description=description_sansalvario, confirmation_code="3TBOP4", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="No", ac="No", heating_system="No", address="Via Pietro Giuria, 17, 10126 Torino TO")

        # aula_test = Room(name="marcopolo", capacity=2, description=description_marcopolo, confirmation_code="123456", status=0, internet="Yes", socket="No", bathroom="No", vending_machine="Yes", ac="No", heating_system="Yes", address="Via Marco polo, 39, 10129 Torino TO")

        aula_murazzi = Room(name="Murazzi", capacity=81, description=description_murazzi, confirmation_code="123098",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="No", ac="Yes",
                          heating_system="Yes", address="Murazzi del Po Gipo Farassino, 22, 10124 Torino TO", copy_machine="No",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 22883024",
                          Opening="Monday-Friday: 9:00 AM to 20:00 PM. On public holidays, Sundays and Saturdays it is closed", nearby_places=nearby_places_murazzi,
                          location="https://www.google.com/maps/place/Murazzi+Student+Zone/@45.0661899,7.6946359,17z/data=!4m9!1m2!2m1!1saula+studio+murazzi+phone+number!3m5!1s0x47886da7642cb87b:0x2f7aaa7fbf430ad0!8m2!3d45.0654144!4d7.6985917!15sCiBhdWxhIHN0dWRpbyBtdXJhenppIHBob25lIG51bWJlciICEAFaFSITYXVsYSBzdHVkaW8gbXVyYXp6aZIBDGVzcHJlc3NvX2JhcpoBI0NoWkRTVWhOTUc5blMwVkpRMEZuU1VSdE1uUnBSazkzRUFF")

        aula_comala = Room(name="Comala", capacity=500, description=description_comala, confirmation_code="102934",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="No", ac="No",
                          heating_system="Yes", address="corso Ferrucci, 65 - 10138 Torino ", copy_machine="No",
                          text_borrowing="No", Smartcard_services="No", Phone="",
                          Opening="Monday-Sunday: 8:00 AM to 00:00 AM. ", nearby_places=nearby_places_comala,
                          location="https://www.google.com/maps/place/Comala+Cultural+Association/@45.0694231,7.6548624,18z/data=!3m1!4b1!4m5!3m4!1s0x47886d1d0e28c6e7:0x64a673dbb09c60a4!8m2!3d45.0694218!4d7.6556362")

        aula_castelfidardo = Room(name="Castelfidardo", capacity=110, description=description_castelfidardo, confirmation_code="AXE303",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes",
                          heating_system="Yes", address="corso Ferrucci, 65 - 10138 Torino ", copy_machine="No",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 011 5646106",
                          Opening="Monday-Friday: 8:30 AM to 19:00 PM. On public holidays, sundays and saturdays it is closed", nearby_places=nearby_places_castelfidardo,
                          location="https://www.google.com/maps/place/Polit%C3%A9cnico+de+Tur%C3%ADn/@45.0638292,7.6602771,17.5z/data=!4m12!1m6!3m5!1s0x47886d193f18a9f1:0xc4839badaa7c36b2!2sEDISU+-+Study+Room+Castelfidardo!8m2!3d45.0648217!4d7.65912!3m4!1s0x47886d196d531be1:0x5dbe7da5b1494e4d!8m2!3d45.0632841!4d7.6601247")

        aula_studio_1 = Room(name="Study_room1", capacity=128, description=description_aula_studio_1, confirmation_code="AXE373",
                          status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes",
                          heating_system="Yes", address="corso Duca degli Abbruzzi, 24 - 10138 Torino", copy_machine="No",
                          text_borrowing="No", Smartcard_services="No", Phone="+39 011 5646106",
                          Opening="Monday-Friday: 8:30 AM to 19:00 PM. On public holidays, sundays and saturdays it is closed", nearby_places=nearby_places_aula_studio_1,
                          location="https://www.google.com/maps/place/Politecnico+di+Torino/@45.0638292,7.6602771,17.5z/data=!4m12!1m6!3m5!1s0x47886d193f18a9f1:0xc4839badaa7c36b2!2sEDISU+-+Study+Room+Castelfidardo!8m2!3d45.0648217!4d7.65912!3m4!1s0x478620b85cabc337:0xd97006264fbdaf1b!8m2!3d45.062404!4d7.6623718")

        db.session.add_all([aula_verdi, aula_opera, aula_galliari, aula_castello, aula_murazzi, aula_comala, aula_castelfidardo, aula_studio_1])
        db.session.commit()

        S = 6
        code = ''.join(random.sample(string.ascii_uppercase + string.digits, k=S))

        CODE = Recovery_code(code=code)

        for user in User.query.all():
            user.counter_booking = 0

        db.session.add(CODE)
        db.session.commit()

        print("Database created")
    else:

        S = 6
        code = ''.join(random.sample(string.ascii_uppercase + string.digits, k=S))

        CODE = Recovery_code(code=code)

        db.session.add(CODE)

        for user in User.query.all():
            user.counter_booking = 0

        for room in Room.query.all():
            room.status = 0

        db.session.commit()

        print("Database found")


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), category='failure')


def send_mail_register(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    msg.html = render_template(template+ '.html', **kwargs )
    mail.send(msg)


def mail_recover(to, subject, template, **kwargs):

    msg = Message(subject, recipients=[to], sender=app.config['MAIL_USERNAME'])
    msg.html = render_template(template+ '.html', **kwargs)
    mail.send(msg)


def get_last_booking(email):
    bookings = Booking.query.filter_by(email_User=email).all()
    last_booking = bookings[-1]
    return last_booking


def get_bookings(email):
    bookings = Booking.query.filter_by(email_User=email).all()
    return bookings


def get_room(room_name):
    room = Room.query.filter_by(name=room_name).first()
    return room


def get_booking(id):
    booking_ = Booking.query.filter_by(id=id).first()
    return booking_


def getUser(email):
    check_expirancy()

    user = User.query.filter_by(email=email).first()
    return user


def check_email(email):
    check_expirancy()
    existent_user = getUser(email)
    if existent_user:
        return True
    else:
        return False


def check_password(inserted_password, stored_password):
    check_expirancy()

    if bcrypt.checkpw(inserted_password.encode('utf-8'), stored_password.encode('utf-8')):
        return True
    else:
        return False


def enter_code(code, room_name):


    room = get_room(room_name)
    room_code = room.confirmation_code

    if room_code == code:
        return True
    else:
        return False

def get_all_bookings():

    today_date = date.today()
    all_existent_bookings = Booking.query.filter(func.date(Booking.date)==today_date).all()
    return all_existent_bookings


def check_expirancy():

    date_now = datetime.datetime.today()

    for booking in get_all_bookings():

        if not booking.confirmed:

            room = get_room(booking.name_StudyRoom)
            delta = date_now - booking.date
            delta_minutes = delta.total_seconds()/60

            print(date_now)
            print(booking.date)
            print(delta_minutes)

            if delta_minutes >= 1:

                room.decrease_number_booking()
                db.session.delete(booking)
                db.session.commit()
                print("Successfully deleted booking")


def new_user(email, first_name, last_name, password):
    check_expirancy()

    session["active_user"] = email
    session["active_user_name"] = first_name
    hashed_password = bcrypt.hashpw((password.encode('utf-8')), bcrypt.gensalt())
    hashed_password = hashed_password.decode('utf-8')
    new_user = User(email=email, first_name=first_name, last_name=last_name, password=hashed_password)
    new_user.counter_booking = 0
    db.session.add(new_user)
    db.session.commit()


@app.route('/deactivate_booking', methods=['GET', 'POST'])
def deactivate_booking():
    check_expirancy()

    if request.method == "POST":

        booking_id = request.form["hidden"]
        booking_to = get_booking(booking_id)
        booking_to.not_active_anymore()

        room = get_room(booking_to.name_StudyRoom)
        room.decrease_number_booking()

        user = getUser(session.get('active_user'))
        bookings = get_bookings(user.email)

        db.session.commit()

        return render_template("bookings_list.html", bookings=bookings)
    else:
        return redirect("/home")


@app.route('/booking', methods=['GET', 'POST'])
def booking():

    check_expirancy()
    page_name = "Booking"
    room_name = session.get('room_name')
    true_code = False

    form = Confirmation_code()
    if session.get('active_user'):

        if form.validate_on_submit():

            inserted_code = form.inserted_code.data
            email = session.get('active_user')
            bookings = get_bookings(email)
            last_booking = get_last_booking(email)
            user = getUser(email)

            if enter_code(inserted_code, room_name):

                true_code = True
                last_booking.yes_confirmed().__init__()
                user.one_more_booking()
                db.session.commit()
                session['room_name'] = None
                flash("Your booking has been confirmed, thank you", category='success')

                return render_template("booking.html", page_name=page_name, bookings=bookings, true_code=true_code)

            else:

                true_code = False
                flash("The inserted code is not valid, try again", category="failure")
                return render_template("booking.html", page_name=page_name, bookings=bookings, true_code=true_code, form=form)

        else:

            email = session.get('active_user')
            user = getUser(email)
            bookings = get_bookings(email)
            counter_user = user.counter_booking

            if len(bookings) > 0:

                true_code = True
                last_booking = get_last_booking(email)

                if last_booking.confirmed:

                    if last_booking.currently_active:

                        flash("You already have an active booking!", category='failure')
                        return render_template("booking.html", user=user,
                                               bookings=bookings, page_name=page_name, form=form, true_code=true_code)
                    else:

                        if counter_user >= 3:

                            flash("We are sorry but you are allowed to book only 3 times a day", category='failure')

                            return render_template("booking.html", user=user,
                                                   bookings=bookings, page_name=page_name, form=form, true_code=true_code)
                        else:

                            true_code = False
                            new_booking = Booking(name_StudyRoom=room_name, email_User=user.email, date=datetime.datetime.today())
                            new_booking.not_confirmed()
                            new_booking.active()
                            db.session.add(new_booking)
                            bookings = get_bookings(email)
                            booked_room = get_room(room_name)
                            booked_room.add_number_booking()
                            db.session.commit()
                            flash("Booking created, you must confirm it within 30 minutes", category="success")

                            return render_template("booking.html", new_booking=new_booking, user=user,
                                                bookings=bookings, page_name=page_name, form=form, true_code=true_code)
                else:
                    flash("You cannot have more bookings unless you confirm your last one", category="failure")

                    return render_template("booking.html", user=user,
                                   bookings=bookings, page_name=page_name, form=form)

            else:

                new_booking = Booking(name_StudyRoom=room_name, email_User=user.email, date=datetime.datetime.today())
                new_booking.not_confirmed()
                new_booking.active()
                db.session.add(new_booking)
                booked_room = get_room(room_name)
                booked_room.add_number_booking()
                bookings = get_bookings(email)
                db.session.commit()

                flash("Booking created, you must confirm it within 30 minutes", category="success")

                return render_template("booking.html", new_booking=new_booking, user=user,
                                       bookings=bookings, page_name=page_name, form=form)

    else:

        return redirect(url_for("home.html"))


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room_chat')
    join_room(room)
    name = getUser(session.get('active_user')).first_name
    emit('status', {'msg': name + ' has entered the chat.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room_chat')
    name = getUser(session.get('active_user')).first_name
    emit('message', {'msg':  name + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room_chat')
    name = getUser(session.get('active_user')).first_name
    emit('status', {'msg': name + ' has left the chat.'}, room=room)
    leave_room(room)
    session['room_chat'] = None


@app.route('/information', methods=['GET', 'POST'])
def information():
    check_expirancy()

    rooms = Room.query.all()

    if session.get('active_user'):
        active = True
    else:
        active = False

    return render_template("information.html", active=active, rooms=rooms)


# @app.route('/marcopolo', methods=['GET','POST'])
# def marcopolo():
#     check_expirancy()
#
#     if session.get('active_user'):
#         active = True
#     else:
#         active = False
#
#     name = 'marcopolo'
#     room = get_room(name)
#     room_name = room.name
#     session["room_name"] = room_name
#
#     return render_template("deepinformation.html", active=active, room=room)

@app.route('/Castelfidardo', methods=['GET','POST'])
def Castelfidardo():
    check_expirancy()
    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Castelfidardo'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/Study_room1', methods=['GET','POST'])
def Study_room1():
    check_expirancy()
    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Study_room1'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)

@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    return 0;



@app.route('/chat', methods=['GET', 'POST'])
def chat():

    check_expirancy()
    # / < roomname >

    room = request.form["hidden"]
    session['room_chat'] = room

    return render_template("chat.html", pagename="Chat", room_chat=room)


@app.route('/personal', methods=['GET', 'POST'])
def personal():

    check_expirancy()
    user = getUser(session.get('active_user'))

    bookings = Booking.query.filter_by(email_User=user.email).all()

    return render_template("personal_information.html", user=user, bookings=bookings)


@app.route('/bookings_list', methods=['GET', 'POST'])
def bookings_list():
    check_expirancy()

    form = Confirmation_code()

    user = getUser(session.get('active_user'))

    bookings = Booking.query.filter_by(email_User=user.email).all()

    return render_template("bookings_list.html", bookings=bookings, form=form)


@app.route('/verdi', methods=['GET', 'POST'])
def verdi():
    check_expirancy()
    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'verdi'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/Murazzi', methods=['GET', 'POST'])
def Murazzi():
    check_expirancy()
    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Murazzi'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/Castello', methods=['GET', 'POST'])
def Castello():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Castello'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/Opera', methods=['GET', 'POST'])
def Opera():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Opera'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/Galliari', methods=['GET', 'POST'])
def Galliari():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Galliari'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)

@app.route('/Comala', methods=['GET', 'POST'])
def Comala():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'Comala'

    room = get_room(name)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""

        else:
            text_nearby += i

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/grugliasco', methods=['GET', 'POST'])
def grugliasco():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'grugliasco'
    room = get_room(name)
    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room)


@app.route('/sansalvario', methods=['GET', 'POST'])
def sansalvario():
    check_expirancy()

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'sansalvario'
    room = get_room(name)
    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room)


@app.route('/', methods=['GET', 'POST'])
def home():

    check_expirancy()
    user = session.get('active_user')
    return render_template("home.html", user=user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    check_expirancy()
    session["active_user"] = None
    session["active_user_name"] = None
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    check_expirancy()

    if session.get("active_user"):

        return redirect(url_for('home'))

    else:

        form = Loginform()
        page_name = "Log-in"

        if form.validate_on_submit():

            email = form.email.data
            password = form.password.data

            existent_user = getUser(email)

            if check_email(email):

                if check_password(password, existent_user.password):

                    session["active_user"] = email
                    session["active_user_name"] = existent_user.first_name

                    return redirect(url_for("home"))
                else:
                    flash("Incorrect password", category='failure')
            else:
                flash(" inexistent account with the inserted email, create an account or try again", category='failure')

    return render_template("login.html", form=form, page_name=page_name)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    check_expirancy()
    page_name = "Sign-up"
    form = Registrationform()

    if form.validate_on_submit():

        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        password1 = form.password1.data
        existent_user = getUser(email)

        if check_email(email):

            flash("An account with the inserted email already exists, please choose another one", category="failure")

        else:

            new_user(email=email, first_name=first_name, last_name=last_name, password=password)
            send_mail_register(email, "Registration in JoinTOStudy!", "mail", name=first_name)

            return redirect(url_for("home"))
    else:

        flash_errors(form)

    return render_template("signup.html", form=form, page_name=page_name)


@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    check_expirancy()

    page_name = "Recovery password process"
    form = recover_password_form()

    if session.get("active_user"):

        return redirect(url_for('home'))

    else:

        if form.validate_on_submit():

            email = form.email.data

            S = 6
            new_code = ''.join(random.sample(string.ascii_uppercase + string.digits, k=S))

            Code_object = Recovery_code.query.first()

            Code_object.code = new_code
            db.session.commit()

            user = getUser(email)

            if not user:

                flash("Inexistent user with the inserted email. Please control if you did not make any mistake", category='failure')
                return render_template("recover_password.html", page_name=page_name, form=form)

            else:

                mail_recover(email, "Password recovery", "mail_recover", code=new_code, name=user.first_name)

                print(new_code)
                print("Update in the database, which passes the new code as parameter and is compared with the one uploaded by the user")
                session['email_password_recovery'] = email
                page_name = "Code verification"

                return redirect(url_for("confirmation_code"))

        else:
            flash_errors(form)

    return render_template("recover_password.html", form=form, page_name=page_name)


@app.route('/confirmation_code', methods=['GET','POST'])
def confirmation_code():
    check_expirancy()

    page_name = "Recovery password process"
    form = code_verification_form()


    if session.get("active_user"):

        return redirect(url_for('home'))

    else:

        if form.validate_on_submit():

            inserted_code = form.code.data
            database_code = Recovery_code.query.first().code

            if inserted_code == database_code:

                return redirect(url_for('password_change_page'))

            else:
                flash("The inserted code is not valid, try again", category='failure')
                return render_template("confirmation_code.html", page_name=page_name, form=form)

    return render_template("confirmation_code.html", page_name=page_name, form=form)


@app.route('/password_change_page', methods=['GET', 'POST'])
def password_change_page():
    check_expirancy()
    if session.get('active_user'):
        user = getUser(session.get('active_user'))
    else:
        user = getUser(session.get('email_password_recovery'))
    name_page = "New password form"
    form = changing_password()
    done = False

    if form.validate_on_submit():

        new_password = form.password.data

        hashed_password = bcrypt.hashpw((new_password.encode('utf-8')), bcrypt.gensalt())
        hashed_password = hashed_password.decode('utf-8')

        user.password = hashed_password

        done = True

        db.session.commit()

        return render_template("password_change_page.html", done=done, name_page = name_page, form=form)

    else:
        done = False
        flash_errors(form)
        return render_template("password_change_page.html", form=form, name_page = name_page, done=done )


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_booking(id):
    check_expirancy()

    print("The booking id is: ")
    print(id)
    print("we are here boys")
    selected_booking = Booking.query.filter_by(id=id).first()
    if selected_booking:
        print ("we are here as well")
        db.session.delete(selected_booking)
        room_name_delete = selected_booking.name_StudyRoom
        db.session.commit()

        email = session.get('active_user')
        user = User.query.filter_by(email=email).first()
        bookings = Booking.query.filter_by(email_User=email).all()

        page_name = "Booking"
        true_code = False

        room = Room.query.filter_by(name=room_name_delete).first()
        room.decrease_number_booking()
        db.session.commit()

        flash("Your booking has been successfully canceled, thank you", category="success")

        # return redirect(url_for("booking"))
        return render_template("booking.html", bookings=bookings, page_name = page_name, true_code = true_code)
    else:
        print ("did not find any booking with such an id")


if __name__ == '__main__':
    # app.run()
    socketio.run(app, host="192.168.1.57")
