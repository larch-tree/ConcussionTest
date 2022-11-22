# Configure application
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from time import ctime, time
from helpers import apology, login_required, lookup, usd, check_pwd_security, owned_stocks
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///FINAL.db")



@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # get submissions
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure username is not already taken
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("Username is already taken")

        # Ensure password and confirmation were submitted and that they match and that the password is secure
        elif not password:
            return apology("must provide password")
        elif not confirmation:
            return apology("must provide confirmation")
        elif password != confirmation:
            return apology("passwords do not match")
        elif not check_pwd_security(password):
            return apology("password must contain 1 letter, 1 number and 1 special character")

        # generate a hash
        hash = generate_password_hash(password)

        # store the new user
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?);", username, hash)

        # log user in
        session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?",
                                        username)[0]["id"]

        return redirect("/")

    return render_template("register.html")

@app.route("/conc_test", methods=["GET", "POST"])
@login_required
def conc_test():
    return render_template("conc_test.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    return render_template("history.html")