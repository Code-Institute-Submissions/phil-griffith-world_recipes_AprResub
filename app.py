import os
import json
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    return render_template("sign_in.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    # form submission functionality
        if request.method == "POST":
            # check if username already exists in db
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                flash("Username already exists")
                return redirect(url_for("register"))

            # # check for password match
            # password = request.form.get("password")
            # confirm_password = request.form.get("password2")

            # if confirm_password != password:
            #     flash("Password do not match"

            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password")),
                "email": request.form.get("email").lower(),
                "country": request.form.get("country")
            }
            mongo.db.users.insert_one(register)

            # put new user into session cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
    return render_template("register.html", countries=countries)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
