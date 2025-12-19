import hashlib
import MySQLdb.cursors
import sys
import os
import re
import requests

from dotenv import load_dotenv
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

load_dotenv()

# Configure application
app = Flask(__name__)

# Configure user data to use mysql
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

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

    # Prepare API call
    api_key = os.getenv('LASTFM_API_KEY')
    api_url = "http://ws.audioscrobbler.com/2.0/"

    params = {
        'method': 'track.search',
        'track': query,
        'api_key': api_key,
        'format': 'json',
        'limit': 20 
    }

    # request to last.fm API
    response = requests.get(api_url, params=params)
    data = response.json()

    # Data structure for track.search
    tracks = data.get('results', {}).get('trackmatches', {}).get('track', [])

    return render_template("browse.html", 
                            tracks=tracks,
                            query=query,
                            )


@app.route("/forum", methods=["GET", "POST"])
@login_required
def forum():
    """Discussion Forum for music discovery"""
    return apology("TODO", 500)

@app.route("/forum/category", methods=["GET", "POST"])
@login_required
def category():

    # if request.args.get('category_id'):
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
    #     cursor.execute(
    #         '''SELECT c.name, t.category_id, t.subject, t.topic_id, 
    #         t.user_id, t.created, count(p.post_id) AS total_post 
    #         FROM forum_topics as t LEFT JOIN forum_posts as p 
    #         ON t.topic_id = p.topic_id LEFT JOIN forum_category as c 
    #         ON t.category_id = c.category_id WHERE t.category_id = %s
    #         GROUP BY t.topid_id ORDER BY t.topic_id DESC''', (request.args.get('category_id'),))
            
    #     topics = cursor.fetchall()

    #     cursor.execute('''
    #     SELECT category_if, name FROM forum_category
    #     WHERE category_id = %s ''', (request.args.get('category_id'),))

    #     category = cursor.fetchone()
        
    #     return render_template("category.html", 
    #                            topics = topics,
    #                            category = category,
    #                            request=request
    #                            )
    # else:
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    #     cursor.execute('''
    #     SELECT category.category_id, category.name, category.description,
    #     count(topic.category_id) AS total_topic 
    #     FROM forum_category category LEFT JOIN forum_topics topic
    #     ON category.category_id = topic.category_id 
    #     GROUP BY category.category_id ORDER BY category_id DESC
    #     ''')
    #     categories = cursor.fetchall()
    #     return render_template("category.html",
    #                            categories = categories,
    #                            request=request) 
    return apology("TODO", 500)

@app.route("/forum/compose", methods=["GET", "POST"])
@login_required
def compose():
    # if 'loggedin' in session:
    #     if request.args.get('category_id'):
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.Dictcursor)

    #         cursor.execute('''
    #         SELECT category_id, name FROM forum_category 
    #         WHERE category_id = %s ''', (request.args.get('category_id'),))
            
    #         category = cursor.fetchone()

    #         return render_template("compose.html",
    #                                category = category)
    # return redirect("/login")
    return apology("TODO", 500)

# Following tutorial documentation by geeksforgeeks for getting more comfortable with MySQL, slight alteration for this website.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Implement user login functionality
    Display login form if user not yet login 
    otherwise implement login and direct to homepage "/" """
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return render_template("index.html",
                                   msg='Logged in successfully!')
        else:
            msg = 'Incorrect username/password!'
    return render_template("login.html", msg=msg)
    
        
@app.route("/forum/post", methods=["GET", "POST"])
@login_required
def post():
    """To list posts"""
    return apology("TODO", 500)

@app.route("/forum/save_post", methods=["GET", "POST"])
@login_required
def save_post():
    """Implement to save post
    -Create form with create post
    in a topic with action save_post to save post"""
    return apology("TODO", 500)


@app.route("/logout")
def logout():
    """Log user out"""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return apology("TODO", 500)

@app.route("/liked", methods=["GET", "POST"])
@login_required
def liked():
    """Liked playlist section
    Not sure about implemenetation yet"""
    return apology("TODO", 500)

@app.route("/register", methods=["GET", "POST"])
def register():
    """"Register user"""
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only letters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            flash('You have successfully registered!')
    return render_template("register.html", msg=msg)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    return apology("TODO", 500)

@app.route("/about")
def about():
    # return render_template("about.html")
    return apology("TODO", 500)

if __name__ == '__main__':
    app.run()  