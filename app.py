from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

from flask_login import UserMixin, LoginManager, login_required, logout_user, login_user, current_user
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
    role = db.Column(db.String(), nullable=False)


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(254), unique=True)
    calories = db.Column(db.Integer)
    carbs = db.Column(db.Integer)
    ingredients = db.Column(db.String())
    allergens = db.Column(db.String())





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
        domain = email.data.split('@')[-1]
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
        user_role = "student" if register_form.email.data.split('@')[-1] == "students.coderva.org" else "worker"
        unique_user = User(email=register_form.email.data, password=hashed_password, role=user_role)


        db.session.add(unique_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", register_form=register_form)


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, str(user_id))


@app.route("/login", methods=["GET","POST"])
def login():
    login_form = LoginForm()

    user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar_one_or_none()


    if login_form.validate_on_submit():
        login_user(user)
        flash("Logged in successfully")

        next_page = request.args.get("next")

        return redirect(next_page or url_for("dashboard"))


    return render_template("login.html", login_form=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# @login_required: can only access dashboard if logged in.
@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():

    if current_user.role == "worker":
        return redirect(url_for("worker_dashboard"))

    elif current_user.role == "student":
        return redirect(url_for("student_dashboard"))


@app.route("/dashboard/student")
@login_required
def student_dashboard():
    user_role = current_user.role

    return render_template("dashboard.html", user_role=user_role)

@app.route("/dashboard/worker")
@login_required
def worker_dashboard():
    user_role = current_user.role

    return render_template("dashboard.html", user_role=user_role)




if __name__ == '__main__':
    app.run(debug=True)
