import sys
import os
import re
import requests

from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

load_dotenv()

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = 'filesystem'
Session(app)

# Configure SQL database
db = SQL("sqlite:///playlisting.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

@app.route("/browse", methods=["GET"])
@login_required
def browse():
    """Set up database to browse songs"""
    # Grab query
    query = request.args.get('query')

    # Prepare API call - documentation provided by last.fm to set up API call
    api_key = os.getenv('LASTFM_API_KEY')
    api_url = "http://ws.audioscrobbler.com/2.0/"

    # Params - variable needed to be passed through for last.fm API
    params = {
        'method': 'track.search',
        'track': query,
        'api_key': api_key,
        'format': 'json',
        'limit': 50 
    }

    # request to last.fm API
    response = requests.get(api_url, params=params)
    data = response.json()

    # Data structure for track.search - json variable for querying tracks.
    tracks = data.get('results', {}).get('trackmatches', {}).get('track', [])

    return render_template("browse.html", 
                            tracks=tracks,
                            query=query,
                            )

# View all categories
@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    """Discussion Forum for music discovery"""
    categories = db.execute(
        "SELECT id, name, description FROM forum_categories"
    )

    return render_template("forum.html", 
                           categories=categories)

# View topics in a category
@app.route("/forum/<genre>", methods=["GET", "POST"])
@login_required
def forum_genre(genre):
    return apology("TODO", 500)

# View specific topic with all its replies
# @app.route("/forum/<genre>/<topic_id>")
# @login_required
# def forum_genre_topic():
#     return apology("TODO", 500)

# # Create New topic in a genre
# @app.route("/forum/<genre>/new", methods=["GET", "POST"])
# @login_required
# def forum_genre_new():
#     return apology("TODO", 500)

# # Add reply to existing topic
# @app.route("/forum/<genre>/<topic_id>/reply", methods=["GET", "POST"])
# @login_required
# def forum_genre_reply():
#     return apology("TODO", 500)


# Following tutorial documentation by geeksforgeeks for getting more comfortable with MySQL, slight alteration for this website.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Implement user login functionality
    Display login form if user not yet login 
    otherwise implement login and direct to homepage "/" """
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Query for username
        rows = db.execute('SELECT * FROM users WHERE username = %s', (username))
        if not check_password_hash(rows[0]["hash"], (password)):
            return apology("Invalid username and/or password", 400)

        if rows:
            session['loggedin'] = True
            session['user_id'] = rows[0]['id']
            session['username'] = rows[0]['username']
            flash('Logged in successfully!')
            return render_template("index.html")
        else:
            flash('Incorrect username/password!')
            return redirect("/login")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Allow users to change their passwords"""
    rows = db.execute(
        "SELECT * FROM users WHERE id = ?", session["user_id"]
    )

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    new_confirmation = request.form.get("new_confirmation")

    if request.method == "POST":

        if not request.form.get("old_password"):
            return apology("Must enter original password", 400)
        elif not check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            return apology("Original password does not match", 400)
        elif not request.form.get("new_password"):
            return apology("New password required", 400)
        elif not request.form.get("new_confirmation"):
            return apology("New password must be typed twice", 400)
        elif new_password != new_confirmation:
            return apology("New passwords do not match", 400)

        # once old password correctly entered, we need to delete old hash and insert new hash in the same place for same user
        new_password_hash = generate_password_hash("new_password")

        # UPDATE query for Existing values, that just need modifying/updating
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?", new_password_hash, session["user_id"]
        )

        return redirect("/")

    else:
        user_data = db.execute(
            "SELECT username FROM users WHERE id = ?", session["user_id"]
        )
        username = user_data[0].get("username")


        return render_template("profile.html",
                               user=user_data,
                               username=username)

@app.route("/liked", methods=["GET", "POST"])
@login_required
def liked():
    """Liked playlist section
    Not sure about implemenetation yet"""
    return apology("TODO", 500)

@app.route("/register", methods=["GET", "POST"])
def register():
    """"Register user"""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        rows = db.execute('SELECT * FROM users WHERE username = ?', (username))

        if rows:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only letters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            password_hash = generate_password_hash(password)
            new_user_id = db.execute('INSERT INTO users (username, hash, email) VALUES(?, ?, ?)', username, password_hash, email)

            rows = db.execute(
                "SELECT * FROM users WHERE username =?", (username))
            
            # Remember (keeps track of) which user has logged in
            new_user_id = rows[0]["id"]
            session["user_id"] = new_user_id

            flash('You have successfully registered!')
            return redirect("/")
    return render_template("register.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    return apology("TODO", 500)

@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run()  