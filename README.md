
![Hero Screenshot](static/img/.png)

## Contents ##
---

[Testing](documents/testing.md)

* UX
    * [Introduction](#introduction)
    * [User Stories](#user-stories)
    * [Design](#design)
        * [Fonts](#fonts)
        * [Icons](#icons)
        * [Colours](#colours)

* [Features](#features)
    * [Features that have been developed](#developed)
    * [Features that will be implemented in the future](#implemented)
* [Technologies](#technologies)
* [Defensive Design](#defensive)
    * [Feature Testing](#ftest)
    * [Defensive Design Testing](#dtest)
* [Issues](#issues)
* [Deployment](#deployment)
* [Credit](#credits)

<a name="introduction"></a>
## Introduction ##

One or two paragraphs providing an overview of your project.

Essentially, this part is your sales pitch.



## UX (User Experience) ##
---

<a name="user-stories"></a>
### User Stories ### 

As a user I would like:

* To be able to view recipes without having to create an account
* To be able to see popular recipes that other users have liked
* To have the option of saving favourite recipes
* To have the option to remove favourite recipes
* To have the option to share recipes
* To have the option to edit shared recipes
* To be able to change my password

In addition to these options, as the admin user I would like:

* To be able to Edit search categories
* To be able to Edit all recipes


<a name="design"></a>

## Design  ##
---
<a name="wireframes"></a>

### Wireframes ###

The webite was initially designed using [balsamiq](https://balsamiq.com/) to create wireframes representing the site structure. See link below for details


* [Desktop](documents/wireframes/desktop.md)
* [Tablet](documents/wireframes/tablet.md)
* [Mobile](documents/wireframes/mobile.md)

<a name="database"></a>

### Database ###
*

<a name="fonts"></a>

### **Fonts** ###

In order to create the feeling of handwritten recipe cards I chose the following fonts from Google fonts.

##### Logo and Recipe descriptions #####
* Dancing Script cursive
##### Titles #####
* Courgette cursive

##### Buttons and other where clairity is required #####
* Comfortaa cursive, Style: Italic

<a name="icons"></a>

### **Icons** ###

The following sites were used for icon creation

* [Font Awesome](https://fontawesome.com/)
* [Favicon.io](https://favicon.io/).
* [Materialize CSS](https://materializecss.com/)

<a name="colours"></a>

### **Colours** ###

For the majority of colours the below colour panel was used to represent different colours of the world (land, sky and sea)

[](documents/colours.png)

&nbsp;
[](documents/colour1.png)
[](documents/colour2.png)
[](documents/colour3.png)
[](documents/colour4.png)
[](documents/colour5.png)




<a name="features"></a>
## Features ## 
---


**Navigation bar**

* 

** Another feature**



<a name="technologies"></a>

## Technologies, libraries and tools used ##

**Front-End**
* [Bootstrap](https://bootstrap4.com/)
* [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)
* [Font-Awesome](https://fontawesome.com/)
* [Google fonts](https://fonts.google.com/)

* [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
* [Javascript](https://www.javascript.com/)

* [SCSS](https://sass-lang.com/)

**Back-end**
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Jinja](https://jinja.palletsprojects.com/en/2.11.x/)
* [MongoDB](https://www.mongodb.com/1)
* [Python](https://www.python.org/)
* [Werkzeug](https://werkzeug.palletsprojects.com/en/1.0.x/)

**Deployment**
* [Heroku](https://dashboard.heroku.com/)
* [Git](https://git-scm.com/)
* [Github](https://github.com/)
* [Gitpod](https://gitpod.io/)


## Testing ##
---

Details of all tests that were performed can be found [here](documents/testing.md)

<a name="issues"></a>
### Issues identified and fixed ###

* Incorrect Recipes deleting & Removing from Favourites
    * Issue was caused by a modal generation in for loop taking the same ID for every modal. Fixed by appending {{ loop.index }} to modal id
* Change Password modal trying to flash messages to deleted my account page
    * Fixed by changing modal to a Change password page where flash message can be displayed until password is successfully changed and then redirect to Home page

In addition to the tests that were completed in the testing document, all code has been tested using the following code validators.

* [JSHint](https://jshint.com/) (JS file passed validator)
* [PEP8 online](http://pep8online.com/)
* [W3C HTML Validator](https://validator.w3.org/) (all pages passed validator)
* [W3C CSS Validator](https://jigsaw.w3.org/css-validator/) (css file passed validator)







## Deployment ##
---

### Local Deployment ###

* Open browser of choice.
* Copy/Paste the address of [World Recipes](https://github.com/phil-griffith/world_recipes) in your search box.
* When on the page, click on the "Code" button.
* Copy the the [HTTPS Link](https://github.com/phil-griffith/world_recipes).
* Open your IDE and in your terminal, create a virtual environement supporting python and flask and activate it.
* Type "git clone" and paste the [HTTPS Link](https://github.com/phil-griffith/world_recipes).
* Create an environement file called "env.py" and add :
    - MONGO_URI=mongodb+srv://...
    - SECRET_KEY= [Your Secret key]
* Add your env.py to .gitignore. to avoid it being uploaded.
* In app.py, switch **debug=False** to **debug=True**
* Upgrade pip locally with the command "pip install -U pip".
* Install the modules used to run the application using "pip freeze > requirements.txt" in your terminal.
* Create a MongoDB account and create a database called **"world_recipes"**.
* Add documtents to database collection as per [database design](#database)




* You can now run your application locally by typing the command "python3 app.py" or "run app.py" in your terminal.
* You can visit the website at http://127.0.0.1:5000

## Deploying on Heroku<hr>

- Create a requirements.txt file using the command **pip3 freeze --local > requirements.txt** in your CLI.
- Create a Procfile (always with an uppercase P) through the command **echo web: python app.py > Procfile**. Commit and Push.
- Create an account on [**Heroku**](https://www.heroku.com/home).
- Create a new app with **unique name**.
- Select your **nearest region**.
- Create a **new python project** within the project.
- Link that project through your **Github repository** in the **deployment** section.
- Navigate to Haroku Settings and set up the following in **Config Vars**





* Go back to the Deploy section, select the master branch and deploy the project. 


<a name="credits"></a>
## Credits ##
---

**



