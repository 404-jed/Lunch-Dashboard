
from flask import Flask, render_template, url_for, redirect

from flask_sqlalchemy import SQLAlchemy, query
import os
from dotenv import load_dotenv

from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, Length,ValidationError

from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)


def configure():
    load_dotenv()

# general web menu database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)


# creating a column in my database for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)



class RegistrationForm(FlaskForm):


    email = EmailField(
        validators=[InputRequired(), Length(min=3), Email()],
        render_kw={
            "Placeholder" : "name@coderva.org"
        }
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=8, max=20)],
        render_kw={
            "Placeholder" : "Password"
        }
    )

    submit = SubmitField("Register")

    def validate_email(self, email) -> None:
        existing_user = db.session.execute(db.select(User).filter_by(email=email.data)).scalar_one_or_none()
        domain = email.data.split("@")[-1]
        if existing_user:
            raise ValidationError("Email already registered, Login or choose a different one")

        if domain not in ("coderva.org", "students.coderva.org"):
            raise ValidationError("Email must be of CodeRVA")


class LoginForm(FlaskForm):
    email = EmailField(
        validators=[InputRequired(), Length(min=3)],
        render_kw={
            "Placeholder": "name@coderva.org"
        }
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={
            "Placeholder": "Password"
        }
    )

    submit = SubmitField("Login")



@app.route('/')
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET","POST"])
def register():
    register_form = RegistrationForm()

    # On form submission our hashed password and unique user will be added and commited into the database
    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password=register_form.password.data)
        unique_user = User(email=register_form.email.data, password=hashed_password)
        db.session.add(unique_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", register_form=register_form)

@app.route("/login", methods=["GET","POST"])
def login():
    login_form = LoginForm()
    return render_template("login.html", login_form=login_form)

if __name__ == '__main__':
    app.run(debug=True)
