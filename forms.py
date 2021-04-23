from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, PasswordField
from wtforms.validators import InputRequired, Email

class RegistrationForm(FlaskForm):
    '''form for registering a new user'''

    username = StringField('Username:', validators=[InputRequired(message="You must enter a username")])
    password = PasswordField('Password:', validators=[InputRequired(message="You have to have a password")])
    email = StringField('Email address:', validators=[InputRequired(message="You must enter an email address"), Email(message="Must be a valid email address.")])
    first_name = StringField('First Name:', validators=[InputRequired(message="Certainly you have a first name")])
    last_name = StringField('Last Name:', validators=[InputRequired(message="Certainly you have a last name")])

class LoginForm(FlaskForm):
    '''form for logging in existing user'''

    username = StringField('Username:', validators=[InputRequired(message="You must enter a username")])
    password = PasswordField('Password:', validators=[InputRequired(message="You have to have a password")])

class FeedbackForm(FlaskForm):
    '''form for creating/editing feedback'''

    title = StringField('Title:', validators=[InputRequired(message="You must enter a title")])
    content = StringField('Content:', validators=[InputRequired(message="You muse enter the body of the feedback")])
    
    