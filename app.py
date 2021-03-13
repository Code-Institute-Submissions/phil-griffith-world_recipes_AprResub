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
@app.route("/home", methods=["GET", "POST"])
def home():
    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    categories = mongo.db.categories.find()
    top_recipes = mongo.db.recipes.find().sort("likes", -1).limit(3)
    return render_template(
        "home.html", countries=countries,
        categories=categories, top_recipes=top_recipes)


@app.route("/get_recipes", methods=["GET", "POST"])
def get_recipes():
    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find()
    return render_template(
        "recipes.html", recipes=recipes,
        countries=countries, categories=categories)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        print("Method is Post")
        query = request.form.get("query")
        country = request.form.get("country")
        category = request.form.get("category")
        vegetarian = request.form.get("vegetarian")
        is_vegetarian = True if vegetarian else False
    else:
        print("Method is NOT Post")
        if session.get("query") is not None:
            query = session["query"]
            session.pop("query")
        else:
            query = ""
        if session.get("country"):
            country = session["country"]
            print(country)
            session.pop("country")
        else:
            country = ""
        if session.get("category"):
            category = session["category"]
            session.pop("category")
        else:
            category = ""
        if session.get("is_vegetarian"):
            is_vegetarian = True
            session.pop("is_vegetarian")
        else:
            is_vegetarian = False

    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)

    categories = mongo.db.categories.find()
    if query:
        if category:
            if country:
                print("ALL filled in")
                print(is_vegetarian)
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "category_name": category,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
            else:
                print("No country, veg unknown")
                print(is_vegetarian)
                recipes = list(mongo.db.recipes.find(
                    {"category_name": category,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
        else:
            if country:
                print("No category, country, veg unknown")
                print(is_vegetarian)
                print(country)
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
            else:
                print("No country, veg unknown")
                print(is_vegetarian)
                print(country)
                recipes = list(mongo.db.recipes.find(
                    {"is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
    # if no text query is entered
    elif not query:
        if category:
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "category_name": category,
                     "is_vegetarian": is_vegetarian}))
            else:
                print("No query, No country, veg unknown")

                recipes = list(mongo.db.recipes.find(
                    {"category_name": category,
                     "is_vegetarian": is_vegetarian}))
        else:
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "is_vegetarian": is_vegetarian}))
            else:
                if is_vegetarian:
                    recipes = list(mongo.db.recipes.find(
                        {"is_vegetarian": is_vegetarian}))
                # if no search parameters are entered
                else:
                    return redirect(url_for("get_recipes"))
        if country:
            session["country"] = country
        elif session.get("country"):
            session.pop("country")
        if query:
            session["query"] = query
        elif session.get("query"):
            session.pop("query")
        if category:
            session["category"] = category
        elif session.get("category"):
            session.pop("category")
        if is_vegetarian:
            session["is_vegetarian"] = is_vegetarian
        elif session.get("is_vegetarian"):
            session.pop("is_vegetarian")
    return render_template("search_results.html", recipes=recipes,
                           country=country, query=query,
                           countries=countries, category=category,
                           is_vegetarian=is_vegetarian,
                           categories=categories)


@app.route("/recipe_details/<see_recipe>", methods=["GET", "POST"])
def recipe_details(see_recipe):
    # get recipe id from recipe card
    recipe = request.form.get("see_recipe")
    top_recipe = request.form.get("top_recipe")
    # get full recipe details from db
    selected_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe)})
    return render_template(
        "recipe_details.html", selected_recipe=selected_recipe,
        top_recipe=top_recipe)


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
    my_recipes = mongo.db.recipes.find({"added_by": session['user']})
    return render_template("my_recipes.html", my_recipes=my_recipes)


@app.route("/favourite_recipes")
def favourite_recipes():
    favourite_recipes_ids = mongo.db.users.find_one(
        {"username": session['user']})['favourites']
    favourite_recipes = []
    for recipe_id in favourite_recipes_ids:
        favourite_recipes.append(mongo.db.recipes.find(
            {"_id": ObjectId(recipe_id)}))
    return render_template("favourite_recipes.html",
                           favourite_recipes=favourite_recipes,
                           username=session['user'])


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
    flash("Recipe Successfully Deleted")
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


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


@app.route("/add_to_favourites", methods=["GET", "POST"])
def add_to_favourites():
    # check if user is logged in
    if session.get('user') is not None:
        if request.method == "POST":
            # get recipe id from recipe page
            fav_recipe = request.form.get("fav_recipe")
            if mongo.db.users.find_one({"username": session["user"],
                                        "favourites": {"$exists": True}}):
                flash("Recipe added to favourites")
                mongo.db.users.update_one({"username": session['user']},
                                        {"$push": {"favourites": fav_recipe}})
            else:
                flash("This user has no favourites")
                mongo.db.users.update_one({"username": session["user"]},
                                        {"$set": {"favourites": [fav_recipe]}})
    return redirect(url_for("get_recipes"))


@app.route("/like_recipe", methods=["GET", "POST"])
def like_recipe():
    # check if user is logged in
    if session.get('user') is not None:
        if request.method == "POST":
            # get recipe id from recipe page
            like_recipe = request.form.get("like_recipe")
            print(like_recipe)
            # check if user has liked any recipes
            if mongo.db.users.find_one({"username": session["user"],
                                        "liked_recipes": {"$exists": True}}):
                # check if user has already liked the recipe
                if mongo.db.users.find_one({"username": session["user"],
                                            "liked_recipes": [like_recipe]}):
                    print("You already liked")
                    like_allowed = False
                else:
                    print("You haven't liked yet")
                    like_allowed = True
            # create a liked_recipe array in the user's account
            else:
                mongo.db.users.update_one({"username": session["user"]},
                                        {"$set":
                                        {"liked_recipes": []}})
                like_allowed = True

            if like_allowed:
                # check if recipe has any likes
                if mongo.db.recipes.find_one({"_id": ObjectId(like_recipe),
                                            "likes": {"$exists": True}}):
                    # get current likes
                    current_likes = mongo.db.recipes.find_one(
                        {"_id": ObjectId(like_recipe)})["likes"]
                    likes = current_likes + 1
                    mongo.db.recipes.update_one({"_id": ObjectId(like_recipe)},
                                                {"$set": {"likes": likes}})

                    mongo.db.users.update_one({"username": session["user"]},
                                            {"$push":
                                            {"liked_recipes": like_recipe}})

                else:
                    mongo.db.recipes.update_one({"_id": ObjectId(like_recipe)},
                                                {"$set": {"likes": 1}})
                    mongo.db.users.update_one({"username": session["user"]},
                                            {"$push":
                                            {"liked_recipes": like_recipe}})
                    print("Like added")

    # https://stackoverflow.com/questions/24295426/python-flask-intentional-empty-response
    return ('', 204)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        print("hello")
        existing_user = mongo.db.users.find_one(
            {"username": session['user']})
        if check_password_hash(
            existing_user["password"],
                request.form.get("old_password")):
            mongo.db.users.update_one(
                {"username": session["user"]},
                {"$set": {"password": generate_password_hash(
                    request.form.get("new_password"))}})
            flash("Password Successfully Changed")
        else:
            flash("Wrong old password")

        username = session['user']
    return render_template("my_account.html", username=username)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
