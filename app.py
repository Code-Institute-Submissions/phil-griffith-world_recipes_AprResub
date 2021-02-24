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
@app.route("/get_recipes", methods=["GET", "POST"])
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("recipes.html", recipes=recipes)


@app.route("/recipe_details/<recipe>", methods=["GET", "POST"])
def recipe_details(recipe):
    # get recipe id from recipe card
    recipe = request.form.get("recipe")
    # get full recipe details from db
    selected_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe)})
    return render_template(
        "recipe_details.html", selected_recipe=selected_recipe)


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        # check if user has account
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # check for password match
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(
                    url_for("account", username=session["user"]))
            else:
                # invalid password
                flash("Incorrect Username and/or Password")
                return redirect(url_for("sign_in"))
        else:
            # Username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("sign_in"))

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

            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(
                    request.form.get("password")),
                "email": request.form.get("email").lower(),
                "country": request.form.get("country")
            }
            mongo.db.users.insert_one(register)

            # put new user into session cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
            return redirect(url_for("account", username=session["user"]))
    return render_template("register.html", countries=countries)


@app.route("/account/<username>", methods=["GET", "POST"])
def account(username):
    # get session users username from db
    print("Username = " + username)
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    print("Username2 = " + username)

    if session["user"]:
        return render_template("my_account.html", username=username)

    return redirect(url_for("sign_in"))


@app.route("/sign_out")
def sign_out():
    # remove user session cookie
    flash("You are no longer Signed in")
    session.pop("user")
    return(redirect(url_for("sign_in")))


@app.route("/add_recipe")
def add_recipe():
    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "add_recipe.html", countries=countries, categories=categories)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
