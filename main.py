from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, CafeForm, ReviewForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)  # For reviews form.
Bootstrap(app)  # Activating Bootstrap

""" Configuring Database, activating SQLAlchemy and SQLite """
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///cafes.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

""" Initialize login manager """
login_manager = LoginManager()
login_manager.init_app(app)

date = datetime.now()
year = date.year


class Cafes(db.Model):
    __tablename__ = "cafe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    map_url = db.Column(db.String(250), nullable=False, unique=True)
    img_url = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.BOOLEAN, nullable=False, default=0)
    has_toilet = db.Column(db.BOOLEAN, nullable=False, default=0)
    has_wifi = db.Column(db.BOOLEAN, nullable=False, default=0)
    can_take_calls = db.Column(db.BOOLEAN, nullable=False, default=0)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.Text, nullable=False)


# db.create_all()

@app.errorhandler(403)
def not_authorised(e):
    error = str(e).split(":")
    error_title = error[0][4:]
    error_description = error[1]
    return render_template('403.html', error_title=error_title, error_description=error_description), 403


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def homepage():
    cafes = Cafes.query.all()
    return render_template("index.html", all_cafes=cafes, year=year)


@app.route("/edit/<int:cafe_id>", methods=["GET", "POST"])
def edit_cafe(cafe_id):
    form = CafeForm()
    cafe = Cafes.query.get(cafe_id)
    if form.validate_on_submit():
        cafe_to_edit = Cafes.query.get(cafe_id)
        cafe_to_edit.name = form.name.data
        cafe_to_edit.map_url = form.map_url.data
        cafe_to_edit.img_url = form.img_url.data
        cafe_to_edit.location = form.location.data
        cafe_to_edit.has_sockets = form.has_sockets.data
        cafe_to_edit.has_toilet = form.has_toilet.data
        cafe_to_edit.has_wifi = form.has_wifi.data
        cafe_to_edit.can_take_calls = form.can_take_calls.data
        cafe_to_edit.seats = form.seats.data
        cafe_to_edit.coffee_price = form.coffee_price.data
        db.session.commit()
        return redirect(url_for('homepage'))

    return render_template("addcafe.html", form=form, cafe_id=cafe.id)


@app.route("/delete/<int:cafe_id>")
def delete_cafe(cafe_id):
    if current_user.is_authenticated and current_user.id == 1:
        cafe_to_delete = Cafes.query.get(cafe_id)
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return redirect(url_for('homepage'))
    elif current_user.is_anonymous or current_user.id != 1:
        return abort(403)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = CafeForm()
    if form.validate_on_submit():
        establishment_registration = Cafes(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data)
        db.session.add(establishment_registration)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash("This email is already registered, try to login.")
            return redirect(url_for('login'))
        else:
            password = form.password.data
            hashed_and_salted_password = generate_password_hash(password=password, method='pbkdf2:sha256',
                                                                salt_length=6)

            new_user = User(name=name,
                            email=email,
                            password=hashed_and_salted_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('homepage'))
    return render_template("sign-up.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email doesn't exist, please try again")
            return redirect(url_for('login'))
        elif user:
            password = check_password_hash(pwhash=user.password, password=password)
            if not password:
                flash("Password incorrect, please try again")
                return redirect(url_for('login'))
            elif password:
                login_user(user=user)
                return redirect(url_for('homepage'))

    return render_template("login.html", form=form)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
