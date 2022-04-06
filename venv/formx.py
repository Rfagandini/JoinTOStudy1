from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo


class Registrationform(FlaskForm):

    email = StringField("Email:", validators=[DataRequired(),
    Length(min=5, max=50, message="Email must contain at least 5 characters"
                         " and not more than 50 characters', category='failure")])

    first_name = StringField("First name:", validators=[DataRequired(),
                 Length(min=2, max=30, message=' it\'s length must be between 2 and 30 characters'),
                 Regexp('^[a-zA-Z]+(?:\s[a-zA-Z]+)*$', message='The first name cannot contain whitespace at the beginning or end. It cannot contain digits or special characters')])

    last_name = StringField("Last name:", validators=[DataRequired(),
                Length(min=2, max=30, message=' it\'s length must be between 2 and 30 characters'),
                Regexp('^[a-zA-Z]+(?:\s[a-zA-Z]+)*$', message='The last name cannot contain whitespace at the beginning or end. It cannot contain digits or special characters')])

    password = PasswordField("Password:", validators=[DataRequired(),
               Length(min=8, max=16, message='It must also contain at least 8 characters and maximum 16'),
               Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$", message="Password must contain at least 1 uppercase, 1 lowercase, a special character and a number"),
               EqualTo('password1',message="Passwords must match")])

    password1 = PasswordField("Password confirmation:", validators=[DataRequired(), Length(min=8, max=16, message='Confirmation password must be identical to the inserted password'),
               Regexp("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$", message="Confirmation password must be identical to the inserted password")])

    submit = SubmitField("Submit")


class Loginform(FlaskForm):

    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Log-in")


class Bookingform(FlaskForm):

    email = StringField("Email:", validators=[DataRequired()])
    first_name = StringField("First name:", validators=[DataRequired()])
    last_name = StringField("First name:", validators=[DataRequired()])
    booking_date = DateField("Booking date:", format="%Y=%m-%d")

    submit = SubmitField("Book!")


class Confirmation_code(FlaskForm):

    inserted_code = StringField("Please insert the code to confirm your booking. Otherwise you are able to cancel it:", validators=[DataRequired()])

    submit = SubmitField("Check!")


class recover_password_form(FlaskForm):

    email = StringField("Email:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class code_verification_form(FlaskForm):

    code = StringField("Code:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class changing_password(FlaskForm):

    password = PasswordField("New password:", validators=[DataRequired(),
                                                      Length(min=8, max=16,
                                                             message='It must also contain at least 8 characters and maximum 16'),
                                                      Regexp(
                                                          "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$",
                                                          message="Password must contain at least 1 uppercase, 1 lowercase, a special character and a number"),
                                                      EqualTo('password1', message="Passwords must match")])

    password1 = PasswordField("Password confirmation:", validators=[DataRequired(), Length(min=8, max=16,
                                                                                           message='Confirmation password must be identical to the inserted password'),
                                                                    Regexp(
                                                                        "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,20}$",
                                                                        message="Confirmation password must be identical to the inserted password")])

    submit = SubmitField("Submit")