from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField


class RegisterForm(FlaskForm):
    """ A class for registering users """
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class CafeForm(FlaskForm):
    """ A form for loading Cafés """
    name = StringField("Name", validators=[DataRequired()])
    map_url = StringField("Map URL", validators=[DataRequired(), URL()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired()])
    has_sockets = BooleanField("Charging Sockets")
    has_toilet = BooleanField("Has Toilet?")
    has_wifi = BooleanField("WIFI?")
    can_take_calls = BooleanField("Can Take calls?")
    seats = StringField("Number of Seats", validators=[DataRequired()])
    coffee_price = StringField("Minimum Coffee Price", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ReviewForm(FlaskForm):
    """ For capturing reviews """
    body = CKEditorField("Review", validators=[DataRequired()])
    submit = SubmitField("Submit Review")
