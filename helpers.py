from flask import redirect, render_template, session
from functools import wraps

"""
Helper functions for Playlisting music discovery platform.

login_required decorator and apology function patterns learned
from CS50 Finance problem set, adapted for this project's needs.
"""

def apology(message, code=400):
    """
    Render error message to user with music-themed styling.

    Based on CS50 Finance apology function, customised for
    music discovery platform aesthetic.
    """
    def escape(s):
        for old, new in[
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    
    return render_template("apology.html",
                           top=code,
                           bottom=escape(message)), code


def login_required(f):
    """
    Decorate routs to require login.

    Adapted from CS50 Finance problem set.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function
