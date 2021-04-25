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
    top_recipes = mongo.db.recipes.find().sort("likes", -1).limit(4)
    # check if user has any favourite or liked recipes
    if session.get("user") is not None:
        user_favourites = mongo.db.users.find_one(
            {"username": session['user']})['favourites']
        user_likes = mongo.db.users.find_one(
            {"username": session['user']})['liked_recipes']
        return render_template("home.html", countries=countries,
                               categories=categories,
                               top_recipes=top_recipes,
                               user_likes=user_likes,
                               user_favourites=user_favourites)
    else:
        return render_template(
            "home.html", countries=countries,
            categories=categories, top_recipes=top_recipes)


@app.route("/get_recipes", methods=["GET", "POST"])
def get_recipes():
    # clear any stored search parameters
    if session.get("country"):
        session.pop("country")
    if session.get("query") is not None:
        session.pop("query")
    if session.get("category"):
        session.pop("category")
    if session.get("is_vegetarian"):
        session.pop("is_vegetarian")
    # create countries object for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)
    recipes = mongo.db.recipes.find()
    categories = mongo.db.categories.find()
    # check if user has any favourite or liked recipes
    if session.get("user") is not None:
        if mongo.db.users.find_one({"username": session["user"],
                                    "favourites": {"$exists": True}}):
            user_favourites = mongo.db.users.find_one(
                {"username": session['user']})['favourites']
        if mongo.db.users.find_one({"username": session["user"],
                                    "liked_recipes": {"$exists": True}}):
            user_likes = mongo.db.users.find_one(
                {"username": session['user']})['liked_recipes']
            return render_template(
                "recipes.html", recipes=recipes,
                countries=countries, categories=categories,
                user_favourites=user_favourites, user_likes=user_likes)
    else:
        return render_template(
            "recipes.html", recipes=recipes,
            countries=countries, categories=categories)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query")
        country = request.form.get("country")
        category = request.form.get("category")
        vegetarian = request.form.get("vegetarian")
        is_vegetarian = True if vegetarian else False
    # when clicking back out of recipe details
    # check session cookies for search terms
    else:
        if session.get("query") is not None:
            query = session["query"]
        else:
            query = ""
        if session.get("country"):
            country = session["country"]
        else:
            country = ""
        if session.get("category"):
            category = session["category"]
        else:
            category = ""
        if session.get("is_vegetarian"):
            is_vegetarian = True
        else:
            is_vegetarian = False

    # create countries list for country select
    countries = []
    with open("data/countries.json", "r") as json_data:
        countries = json.load(json_data)

    # create categories list for country select
    categories = mongo.db.categories.find()

    # if text query, category & country are entered
    if query:
        if category:
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "category_name": category,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
            # if text query & category are entered
            else:
                recipes = list(mongo.db.recipes.find(
                    {"category_name": category,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
        else:
            # if text query & country are entered
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
            # if text query is entered
            else:
                recipes = list(mongo.db.recipes.find(
                    {"is_vegetarian": is_vegetarian,
                     "$text": {"$search": query}}))
    # if no text query is entered
    elif not query:
        if category:
            # if category & country are entered
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "category_name": category,
                     "is_vegetarian": is_vegetarian}))
            # if category is entered
            else:
                recipes = list(mongo.db.recipes.find(
                    {"category_name": category,
                     "is_vegetarian": is_vegetarian}))
        else:
            # if country is entered
            if country:
                recipes = list(mongo.db.recipes.find(
                    {"country": country,
                     "is_vegetarian": is_vegetarian}))
            else:
                # if vegetarian selected is true
                if is_vegetarian:
                    recipes = list(mongo.db.recipes.find(
                        {"is_vegetarian": is_vegetarian}))
                # if no search parameters are entered load Recipes page
                else:
                    return redirect(url_for("get_recipes"))
    # store entered search terms in session cookie
    if country:
        session["country"] = country
    if query:
        session["query"] = query
    if category:
        session["category"] = category
    if is_vegetarian:
        session["is_vegetarian"] = is_vegetarian
    # get user likes and favourites
    if session.get("user") is not None:
        user_favourites = mongo.db.users.find_one(
            {"username": session['user']})['favourites']
        user_likes = mongo.db.users.find_one(
            {"username": session['user']})['liked_recipes']
        # load search results
        return render_template("search_results.html", recipes=recipes,
                               country=country, query=query,
                               countries=countries, category=category,
                               is_vegetarian=is_vegetarian,
                               categories=categories, user_likes=user_likes,
                               user_favourites=user_favourites)
    else:
        # load search results
        return render_template("search_results.html", recipes=recipes,
                               country=country, query=query,
                               countries=countries, category=category,
                               is_vegetarian=is_vegetarian,
                               categories=categories)


@app.route("/recipe_details", methods=["GET", "POST"])
def recipe_details():
    # get recipe id from recipe card
    recipe = request.args.get("recipe_id")
    # capture requesting page for the back button
    top_recipe = request.args.get("top_recipe")
    fav_recipe = request.args.get("fav_recipe")
    my_recipes = request.args.get("my_recipes")
    manage_recipes = request.args.get("manage_recipes")
    # get full recipe details from db
    selected_recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe)})
    # check if user has any favourite or liked recipes
    if session.get("user") is not None:
        user_favourites = mongo.db.users.find_one(
            {"username": session['user']})['favourites']
        user_likes = mongo.db.users.find_one(
            {"username": session['user']})['liked_recipes']
        # load recipe details page
        return render_template(
            "recipe_details.html", selected_recipe=selected_recipe,
            top_recipe=top_recipe, fav_recipe=fav_recipe,
            my_recipes=my_recipes, manage_recipes=manage_recipes,
            recipe_details=recipe_details, user_likes=user_likes,
            user_favourites=user_favourites)
    else:
        # load recipe details page
        return render_template(
            "recipe_details.html", selected_recipe=selected_recipe,
            top_recipe=top_recipe, fav_recipe=fav_recipe,
            my_recipes=my_recipes, manage_recipes=manage_recipes,
            recipe_details=recipe_details)


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    # prevent access if user is logged in
    if "user" in session:
        return ('', 204)
    else:
        if request.method == "POST":
            # check if user has account
            existing_user = mongo.db.users.find_one(
                {"username": request.form.get("username").lower()})

            if existing_user:
                # check for password match
                if check_password_hash(
                        existing_user["password"],
                        request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    # load home page if password is accepted
                    return redirect(
                        url_for("home", username=session["user"]))
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
    # prevent access if user is logged in
    if "user" in session:
        return ('', 204)
    else:
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
                    "country": request.form.get("country"),
                    "favourites": [],
                    "liked_recipes": []
                }
                # add user details to database
                mongo.db.users.insert_one(register)

                # put new user into session cookie
                session["user"] = request.form.get("username").lower()
                flash("Registration Successful!")
                return redirect(url_for("home", username=session["user"]))
        return render_template("register.html", countries=countries)


@app.route("/sign_out")
def sign_out():
    # check if user is logged in
    if "user" in session:
        # remove user session cookie
        flash("Goodbye")
        session.pop("user")
        return(redirect(url_for("sign_in")))
    return(redirect(url_for("sign_in")))


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    # check if user is logged in
    if "user" in session:
        if request.method == "POST":
            is_vegetarian = True if request.form.get(
                "is_vegetarian") else False
            # set ingredient number to 1
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
                # increment ingredient number by 1
                x += 1
            method = []
            # set method number to 1
            y = 1
            # loop over each added method step
            while request.form.get("step"+str(y)):
                print(request.form.get("step"+str(y)))
                method.append(request.form.get("step"+str(y)))
                # increment method number by 1
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

        # create countries list for country select
        countries = []
        with open("data/countries.json", "r") as json_data:
            countries = json.load(json_data)
        # create categories list for category select
        categories = mongo.db.categories.find().sort("category_name", 1)
        return render_template(
            "add_recipe.html", countries=countries, categories=categories)
    else:
        return redirect(url_for('sign_in'))


@app.route("/my_recipes")
def my_recipes():
    #  check if user is logged in
    if "user" in session:
        # check database for recipeds added by user
        if mongo.db.recipes.find_one({"added_by": session['user']}):
            my_added_recipes = mongo.db.recipes.find(
                {"added_by": session['user']})
            # find liked recipes
            user_likes = mongo.db.users.find_one(
                {"username": session['user']})['liked_recipes']
            return render_template("my_recipes.html",
                                   my_added_recipes=my_added_recipes,
                                   user_likes=user_likes)
        else:
            my_added_recipes = False
        return render_template("my_recipes.html",
                               my_added_recipes=my_added_recipes)
    return redirect(url_for('sign_in'))


@app.route("/favourite_recipes")
def favourite_recipes():
    # check if user is logged in
    if "user" in session:
        if mongo.db.users.find_one({"username": session["user"],
                                    "favourites": {"$exists": True}}):
            #  create list of users favourite recipe IDs
            favourite_recipes_ids = mongo.db.users.find_one(
                {"username": session['user']})['favourites']
            favourite_recipes = []
            # create list of favourite recipe objects
            for recipe_id in favourite_recipes_ids:
                favourite_recipes.append(mongo.db.recipes.find_one(
                    {"_id": ObjectId(recipe_id)}))
            # find liked recipes
            user_likes = mongo.db.users.find_one(
                {"username": session['user']})['liked_recipes']
            return render_template("favourite_recipes.html",
                                   favourite_recipes=favourite_recipes,
                                   username=session['user'],
                                   user_likes=user_likes)
        else:
            return render_template(
                "favourite_recipes.html", username=session['user'])
    return redirect(url_for('sign_in'))


@app.route("/edit_recipe/<recipe_id>",
           methods=["GET", "POST"])
def edit_recipe(recipe_id):
    manage_recipes = request.args.get('manage_recipes')
    if request.method == "POST":
        is_vegetarian = True if request.form.get("is_vegetarian") else False
        x = 1
        ingredients = []
        # loop over each added ingedient
        # https://stackoverflow.com/questions/32741216/2d-array-python-list-index-out-of-range
        while request.form.get("ingredient"+str(x)):
            row = []
            row.append(request.form.get("ingredient"+str(x)))
            row.append(request.form.get("quantity"+str(x)))
            ingredients.append(row)
            x += 1
        method = []
        y = 1
        # loop over each added method step
        while request.form.get("step"+str(y)):
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
        if manage_recipes:
            return redirect(url_for("manage_recipes"))
        else:
            return redirect(url_for("my_recipes"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    # Check if logged in user created recipe before loading edit recipe page
    user = recipe['added_by']
    if session['user'] == user:
        countries = []
        with open("data/countries.json", "r") as json_data:
            countries = json.load(json_data)
        categories = mongo.db.categories.find().sort("category_name", 1)
        return render_template(
            "edit_recipe.html", countries=countries,
            recipe=recipe, categories=categories,
            manage_recipes=manage_recipes)
    else:
        # If user did not create the recipe, do nothing / reload page
        return ('', 204)


@app.route("/delete_recipe/<recipe_id>/<manage_recipes>")
def delete_recipe(recipe_id, manage_recipes):
    # remove recipe from database
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    # find all users
    users = mongo.db.users.find()
    # check each users favourites and remove recipe if found
    for user in users:
        for favourite in user.get('favourites'):
            username = user.get('username')
            if favourite == recipe_id:
                mongo.db.users.update_one({"username": username},
                                          {"$pull":
                                          {"favourites": recipe_id}})
    flash("Recipe Successfully Deleted")
    # check which page recipe was deleted from and redirect
    if manage_recipes != "False":
        manage_recipes = True
        return redirect(url_for("manage_recipes"))
    else:
        manage_recipes = False
        return redirect(url_for("my_recipes"))


@app.route("/remove_recipe/<recipe_id>")
def remove_recipe(recipe_id):
    mongo.db.users.update_one({"username": session['user']},
                              {"$pull":
                              {"favourites": recipe_id}})
    flash("Recipe Successfully Removed")
    return redirect(url_for("favourite_recipes"))


@app.route("/get_categories")
def get_categories():
    # check if user is logged in
    if "user" in session:
        # check if user is admin
        if session['user'] == "admin":
            categories = list(
                mongo.db.categories.find().sort("category_name", 1))
            return render_template(
                "manage_categories.html", categories=categories)
        else:
            # if user is not admin do nothing (prevent unauthorized access)
            return ('', 204)
    else:
        # if user is not signed, redirect to sign in page
        # (prevent unauthorized access)
        return redirect(url_for("sign_in"))


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
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
        # get recipe id from recipe page
        fav_recipe = request.args.get("recipe_id")
        # check if user has any favourites
        if mongo.db.users.find_one({"username": session["user"],
                                    "favourites": {"$exists": True}}):
            # add recipe to favourites if it doesn't already exist
            if mongo.db.users.find_one({"username": session["user"],
                                        "favourites":
                                        {"$ne": fav_recipe}}):
                mongo.db.users.update_one({"username": session['user']},
                                          {"$push":
                                          {"favourites": fav_recipe}})
        else:
            # add recipe to users favourites
            mongo.db.users.update_one({"username": session["user"]},
                                      {"$set":
                                      {"favourites": [fav_recipe]}})
    return ('', 204)


@app.route("/like_recipe", methods=["GET", "POST"])
def like_recipe():
    # check if user is logged in
    if session.get('user') is not None:
        # get recipe id from recipe page
        like_recipe = request.args.get("recipe_id")
        # check if user has liked any recipes
        if mongo.db.users.find_one({"username": session["user"],
                                    "liked_recipes": {"$exists": True}}):
            # check if user has already liked the recipe
            if mongo.db.users.find_one({"username": session["user"],
                                        "liked_recipes": like_recipe}):
                like_allowed = False
            else:
                like_allowed = True
        # create a new liked_recipe array in the user's account
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
                # update the recipes likes to likes + 1
                mongo.db.recipes.update_one({"_id": ObjectId(like_recipe)},
                                            {"$set": {"likes": likes}})
                # add recipe to users liked recipes
                mongo.db.users.update_one({"username": session["user"]},
                                          {"$push":
                                           {"liked_recipes": like_recipe}})

            else:
                # set recipe likes value to 1
                mongo.db.recipes.update_one({"_id": ObjectId(like_recipe)},
                                            {"$set": {"likes": 1}})
                # add recipe id to users liked recipes list
                mongo.db.users.update_one({"username": session["user"]},
                                          {"$push":
                                          {"liked_recipes": like_recipe}})

    # https://stackoverflow.com/questions/24295426/python-flask-intentional-empty-response
    return ('', 204)


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": session['user']})
        if check_password_hash(
            existing_user["password"],
                request.form.get("old_password")):
            if request.form.get('new_password') != request.form.get(
                            'confirm_new_password'):
                flash("Passwords do not match")
            else:
                mongo.db.users.update_one(
                    {"username": session["user"]},
                    {"$set": {"password": generate_password_hash(
                        request.form.get("new_password"))}})
                flash("Password Successfully updated")
                return redirect(url_for('home'))
        else:
            flash("Wrong old password")
            username = session['user']
            return render_template("change_password.html", username=username)
    username = session['user']
    return render_template("change_password.html", username=username)


@app.route("/manage_recipes")
def manage_recipes():
    if session.get('user') is not None:
        if session['user'] == "admin":
            # create countries object for country select
            countries = []
            with open("data/countries.json", "r") as json_data:
                countries = json.load(json_data)
            recipes = mongo.db.recipes.find()
            categories = mongo.db.categories.find()
            # identify all recipes marked as favourites
            user_favourites = mongo.db.users.find_one(
                {"username": session['user']})['favourites']
            # identify all recipes previously liked
            user_likes = mongo.db.users.find_one(
                {"username": session['user']})['liked_recipes']
            return render_template("manage_recipes.html",
                                   recipes=recipes, countries=countries,
                                   categories=categories,
                                   user_likes=user_likes,
                                   user_favourites=user_favourites)
        else:
            return ('', 204)
    else:
        return redirect(url_for('sign_in'))


# Catch 404 error and render page providing link to home page
@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
