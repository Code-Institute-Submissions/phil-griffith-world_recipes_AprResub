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
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("my_account.html", username=username)

    return redirect(url_for("sign_in"))


@app.route("/sign_out")
def sign_out():
    # remove user session cookie
    flash("You are no longer Signed in")
    session.pop("user")
    return(redirect(url_for("sign_in")))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    if request.method == "POST":
        is_vegetarian = True if request.form.get("is_vegetarian") else False
        x = 1
        ingredients = []
        # loop over each added ingedient
        # https://stackoverflow.com/questions/32741216/2d-array-python-list-index-out-of-range
        while request.form.get("ingredient"+str(x)):
            row = []
            print(request.form.get("ingredient"+str(x)))
            row.append(request.form.get("ingredient"+str(x)))
            row.append(request.form.get("quantity"+str(x)))
            ingredients.append(row)
            x += 1
        method = []
        y = 1
        # loop over each added method step
        while request.form.get("step"+str(y)):
            print(request.form.get("step"+str(y)))
            method.append(request.form.get("step"+str(y)))
            y += 1
        recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "image_url": request.form.get("image_url"),
            "category_name": request.form.get("category_name"),
            "is_vegetarian": is_vegetarian,
            "recipe_description": request.form.get("recipe_description"),
            "country": request.form.get("country"),
            "ingredients": ingredients,
            "method": method,
            "recipe_story": request.form.get("recipe_story"),
            "added_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added")
        return redirect(url_for("get_recipes"))

    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "add_recipe.html", countries=countries, categories=categories)


@app.route("/my_recipes")
def my_recipes():
    my_recipes = mongo.db.recipes.find({"added_by": "green"})
    return render_template("my_recipes.html", my_recipes=my_recipes)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        is_vegetarian = True if request.form.get("is_vegetarian") else False
        x = 1
        ingredients = []
        # loop over each added ingedient
        # https://stackoverflow.com/questions/32741216/2d-array-python-list-index-out-of-range
        while request.form.get("ingredient"+str(x)):
            row = []
            print(request.form.get("ingredient"+str(x)))
            row.append(request.form.get("ingredient"+str(x)))
            row.append(request.form.get("quantity"+str(x)))
            ingredients.append(row)
            x += 1
        method = []
        y = 1
        # loop over each added method step
        while request.form.get("step"+str(y)):
            print(request.form.get("step"+str(y)))
            method.append(request.form.get("step"+str(y)))
            y += 1
        updated_recipe = {
            "recipe_name": request.form.get("recipe_name"),
            "image_url": request.form.get("image_url"),
            "category_name": request.form.get("category_name"),
            "is_vegetarian": is_vegetarian,
            "recipe_description": request.form.get("recipe_description"),
            "country": request.form.get("country"),
            "ingredients": ingredients,
            "method": method,
            "recipe_story": request.form.get("recipe_story"),
            "added_by": session["user"]
        }
        # https://stackoverflow.com/questions/30605638/why-does-upsert-a-record-using-update-one-raise-valueerror
        mongo.db.recipes.update_one({"_id": ObjectId(
            recipe_id)}, {"$set": updated_recipe}, upsert=True)
        flash("Recipe Successfully Updated")
        return redirect(url_for("my_recipes"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_recipe.html", countries=countries,
        recipe=recipe, categories=categories)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("my_recipes"))


@app.route("/get_categories")
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    return render_template("manage_categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")


@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.update_one({"_id": ObjectId(
            category_id)}, {"$set": submit}, upsert=True)
        return redirect(url_for("get_categories"))
    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
