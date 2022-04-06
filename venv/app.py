
import os
import random
import string
import json

import re, bcrypt

from flask import Flask, render_template, flash, session, redirect, url_for, request, jsonify
from formx import Registrationform, Loginform, Confirmation_code, recover_password_form, code_verification_form, changing_password
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail, Message
from flask_socketio import SocketIO, join_room, leave_room, emit


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
app.config['MAIL_PASSWORD'] =  os.getenv('password')
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

        aula_verdi = Room(name="verdi", capacity=143, description=description_verdi, confirmation_code="#$%303", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes", heating_system="Yes", address="via Verdi, 26 - 10124 Torino", copy_machine="Yes", text_borrowing="No", Smartcard_services="Yes", Phone="+39 011 6531290", Opening="Monday-Friday: 8:30 AM to 00:00 AM. On public holidays, Sundays and Saturdays from 8:30 AM to 10:00 PM"
                          , nearby_places=nearby_places_verdi)

        aula_grugliasco = Room(name="grugliasco", capacity=150, description=description_grugliasco, confirmation_code="609TOR", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="Yes", ac="Yes", heating_system="No", address="Via Berta, 5, 10095 Grugliasco TO")

        aula_sansalvario = Room(name="sansalvario", capacity=200, description=description_sansalvario, confirmation_code="3TBOP4", status=0, internet="Yes", socket="Yes", bathroom="Yes", vending_machine="No", ac="No", heating_system="No", address="Via Pietro Giuria, 17, 10126 Torino TO")

        aula_test = Room(name="marcopolo", capacity=2, description=description_marcopolo, confirmation_code="123456", status=0, internet="Yes", socket="No", bathroom="No", vending_machine="Yes", ac="No", heating_system="Yes", address="Via Marco polo, 39, 10129 Torino TO")

        db.session.add_all([aula_verdi, aula_grugliasco, aula_sansalvario, aula_test])
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


@app.route('/booking', methods=['GET', 'POST'])
def booking():

    page_name = "Booking"
    room_name = session.get('room_name')
    true_code = False

    print(room_name)
    print("BOOKING1")

    # if session.get('room_name'):
    #     session['room_name'] = None

    form = Confirmation_code()
    if session.get('active_user'):

        if form.validate_on_submit():

            print("We entered here, that's already a lot! , keep going :)")

            inserted_code = form.inserted_code.data
            print(inserted_code)
            print(room_name)
            real_room = Room.query.filter_by(name=room_name).first()
            real_code = real_room.confirmation_code
            email = session.get('active_user')
            bookings = Booking.query.filter_by(email_User=email).all()
            last_booking = bookings[-1]
            user = getUser(email)

            if inserted_code == real_code:
                true_code = True
                last_booking.yes_confirmed().__init__()
                user.one_more_booking()
                db.session.commit()
                bookings = Booking.query.filter_by(email_User=email).all()
                last_booking = bookings[-1]
                print("THE ENTERED CODE IS CORRECT")
                print(true_code)
                print(last_booking.getconfirmed())

                session['room_name'] = None
                flash("Your booking has been confirmed, thank you", category='success')

                return render_template("booking.html", page_name=page_name, bookings=bookings, true_code=true_code)

            else:
                true_code = False
                print("THE CODE IS INCORRECT")
                print(last_booking.confirmed)
                print(true_code)
                print(not true_code)
                flash("The inserted code is not valid, try again", category="failure")
                return render_template("booking.html", page_name=page_name, bookings=bookings, true_code=true_code, form=form)

        else:

            email = session.get('active_user')
            user = User.query.filter_by(email=email).first()
            bookings = Booking.query.filter_by(email_User=email).all()
            counter_user = user.counter_booking

            if len(bookings) > 0:

                true_code = True
                last_booking = bookings[-1]
                print(last_booking.getconfirmed())
                print("AT THE END OF BOOKING, TRUE OR FALSE")

                if last_booking.confirmed:

                    if counter_user >= 3:
                        print("IS THIS OKAYYYYYYYYYYYYY?")
                        flash("We are sorry but you are allowed to book only 3 times a day", category='failure')

                        db.session.commit()
                        return render_template("booking.html", user=user,
                                               bookings=bookings, page_name=page_name, form=form, true_code=true_code)
                    else:

                        true_code = False
                        new_booking = Booking(name_StudyRoom=room_name, email_User=user.email)
                        new_booking.not_confirmed()
                        db.session.add(new_booking)
                        bookings = Booking.query.filter_by(email_User=email).all()
                        print("BOOKING INTENTION DECLARED")
                        Booked_room = Room.query.filter_by(name=room_name).first()
                        Booked_room.add_number_booking()
                        print(Booked_room.status)
                        db.session.commit()

                        print(new_booking.getconfirmed())
                        print("IF AT THE END OF BOOKING")
                        db.session.commit()
                        flash("Booking created, you must confirm it within 30 minutes", category="success")
                        return render_template("booking.html", new_booking=new_booking, user=user,
                                            bookings=bookings, page_name=page_name, form=form, true_code=true_code)
                else:
                    flash("You cannot have more bookings unless you confirm your last one", category="failure")

                    return render_template("booking.html", user=user,
                                   bookings=bookings, page_name=page_name, form=form)

            else:

                new_booking = Booking(name_StudyRoom=room_name, email_User=user.email)
                new_booking.not_confirmed()
                db.session.add(new_booking)
                print(new_booking.getconfirmed())
                print("ELSE AT THE END OF BOOKING")

                Booked_room = Room.query.filter_by(name=room_name).first()
                Booked_room.add_number_booking()

                bookings = Booking.query.filter_by(email_User=email).all()

                db.session.commit()
                flash("Booking created, you must confirm it within 30 minutes", category="success")
                return render_template("booking.html", new_booking=new_booking, user=user,
                                       bookings=bookings, page_name=page_name, form=form)

    else:

        return redirect(url_for("home.html"))


# @app.route('/contactus', methods=['GET', 'POST'])
# def contactus():
#
#     return render_template("home.html")


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

    rooms = Room.query.all()

    if session.get('active_user'):
        active = True
    else:
        active = False

    return render_template("information.html", active=active, rooms=rooms)


@app.route('/marcopolo', methods=['GET','POST'])
def marcopolo():

    if session.get('active_user'):
        active = True
    else:
        active = False

    name = 'marcopolo'

    room = Room.query.filter_by(name=name).first()

    # if room.status >= room.capacity:
    #     user = session.get('active_user')
    #     return render_template("home.html", user=user)

    print(room.name)
    print("MARCOPOLO APPROUTE")

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # / < roomname >

    room = request.form["hidden"]
    # user = getUser(session.get('active_user'))
    session['room_chat'] = room

    return render_template("chat.html", pagename="Chat", room_chat=room)


@app.route('/personal', methods=['GET', 'POST'])
def personal():

    user = getUser(session.get('active_user'))

    bookings = Booking.query.filter_by(email_User=user.email).all()

    return render_template("personal_information.html", user=user, bookings=bookings)

@app.route('/bookings_list', methods=['GET', 'POST'])
def bookings_list():

    form = Confirmation_code()

    user = getUser(session.get('active_user'))

    bookings = Booking.query.filter_by(email_User=user.email).all()

    return render_template("bookings_list.html", bookings=bookings, form=form)


@app.route('/verdi', methods=['GET', 'POST'])
def verdi():

    # print(request.form["hidden"])

    if session.get('active_user'):
        active = True
    else:
        active = False

    # name = request.form["hidden"]
    name = 'verdi'

    room = Room.query.filter_by(name=name).first()

    # if room.status >= room.capacity:
    #     user = session.get('active_user')
    #     return render_template("home.html", user=user)

    text_nearby = ""
    super_text = []

    for i in room.nearby_places:

        if i == ")":
            text_nearby += i
            super_text.append(text_nearby)
            text_nearby = ""
            print(super_text)
        else:
            text_nearby += i




    print(room.name)
    print("VERDI APPROUTE")

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room, super_text=super_text)


@app.route('/grugliasco', methods=['GET', 'POST'])
def grugliasco():

    if session.get('active_user'):
        active = True
    else:
        active = False



    # name = request.form["hidden"]
    name = 'grugliasco'
    room = Room.query.filter_by(name=name).first()

    # if room.status >= room.capacity:
    #     user = session.get('active_user')
    #     return render_template("home.html", user=user)

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room)


@app.route('/sansalvario', methods=['GET', 'POST'])
def sansalvario():

    if session.get('active_user'):
        active = True
    else:
        active = False

    # name = request.form["hidden"]
    name = 'sansalvario'
    room = Room.query.filter_by(name=name).first()

    # if room.status >= room.capacity:
    #     user = session.get('active_user')
    #     return render_template("home.html", user=user)

    room_name = room.name
    session["room_name"] = room_name

    return render_template("deepinformation.html", active=active, room=room)


@app.route('/', methods=['GET', 'POST'])
def home():

    user = session.get('active_user')

    return render_template("home.html", user=user)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session["active_user"] = None
    session["active_user_name"] = None
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    if session.get("active_user"):

        return redirect(url_for('home'))

    else:

        form = Loginform()
        page_name = "Log-in"

        if form.validate_on_submit():

            email = form.email.data
            password = form.password.data

            existent_user = User.query.filter_by(email=email).first()

            if existent_user:

                if bcrypt.checkpw(password.encode('utf-8'), existent_user.password.encode('utf-8')):
                    session["active_user"] = email
                    user = User.query.filter_by(email=email).first()
                    session["active_user_name"] = user.first_name
                    return redirect(url_for("home"))
                else:
                    flash("Incorrect password", category='failure')
            else:
                flash(" inexistent account with the inserted email, create an account or try again", category='failure')

    return render_template("login.html", form=form, page_name=page_name)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    page_name = "Sign-up"
    form = Registrationform()

    if form.validate_on_submit():

        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = form.password.data
        password1 = form.password1.data

        existent_user = User.query.filter_by(email=email).first()

        if existent_user:
            flash("An account with the inserted email already exists, please choose another one", category="failure")
        # flash('Account created', category='success')
        else:

            session["active_user"] = email
            user = User.query.filter_by(email=email).first()
            session["active_user_name"] = first_name
            hashed_password = bcrypt.hashpw((password.encode('utf-8')), bcrypt.gensalt())
            hashed_password = hashed_password.decode('utf-8')
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=hashed_password)
            new_user.counter_booking = 0
            db.session.add(new_user)
            db.session.commit()
            send_mail_register(email, "Registration in BookTOStudy!", "mail", name=first_name)

            return redirect(url_for("home"))
    else:

        flash_errors(form)

    return render_template("signup.html", form=form, page_name=page_name)


@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():

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


def getUser(email):

    user = User.query.filter_by(email=email).first()
    return user



@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete_booking(id):

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
