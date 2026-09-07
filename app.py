from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_login import UserMixin


app = Flask(__name__)

def configure():
    load_dotenv()

# general lunch menu database

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db = SQLAlchemy(app)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/')
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)
