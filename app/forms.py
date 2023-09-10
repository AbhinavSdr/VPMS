from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField, FloatField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
from app.models import User, ParkingSlot, ParkingPrice, ParkingHistory

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Regexp('[a-zA-Z]')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[(' ', 'Select your choice'),('Entry','ENTRY'),('Exit','EXIT')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_role(self, role):
        if role==" ":
            raise ValidationError('Please select a role!')

class URegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired(), Regexp('[a-zA-Z]')])
    password = StringField('Password', validators=[DataRequired(), Regexp('[a-zA-Z]')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[(' ', 'Select your choice'),('User','USER')], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_role(self, role):
        if role==" ":
            raise ValidationError('Please select a role!')


class EntryForm(FlaskForm):
    registration_no = StringField('Registration', validators=[DataRequired(), Regexp('[0-9A-Z]', message='Enter Correct Registration Number!')])
    name = StringField('Name', validators=[DataRequired(), Regexp('[a-zA-Z]', message='Enter only Name!')])
    phone = StringField('Phone Number', validators=[DataRequired(), Regexp('[0-9]', message='Enter only Number!')])
    submit = SubmitField('Entry')

    def validate_registration_no(self, registration_no):
        rc = ParkingSlot.query.filter_by(rc=registration_no.data).first()
        if rc is not None:
            raise ValidationError('This Registration Number is already logged into your Parking Facility!')

    def validate_phone(self, phone):
        phone = ParkingSlot.query.filter_by(phone=phone.data).first()
        if phone is not None:
            raise ValidationError('This Phone number is already registered into your Parking Facility!')

class ExitForm(FlaskForm):
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Validate Exit!')

    def validate_phone(self, phone):
        phone = ParkingSlot.query.filter_by(phone=phone.data).first()
        if phone is None:
            raise ValidationError('Phone Number didn\'t matched!')

class ForgetPassword(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request New Password')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is None:
            raise ValidationError('Email Address is not Registered!')


class UpdateUser(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class UpdatePrice(FlaskForm):
    charge = FloatField('Parking Charge/hr', validators=[DataRequired()])
    submit = SubmitField('Update')

class PaymentForm(FlaskForm):
    type = SelectField('Type', choices=[(' ', 'Select your choice'),('Upi','UPI'),('Net Banking','NET BANKING')], validators=[DataRequired()])
    submit = SubmitField('Pay')
    