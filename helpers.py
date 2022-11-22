import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


# implementing a password security check function
# !!! SADLY CHECK50 CANNOT HANDLE MORE COMPLEX PASSWORD RESTRICTIONS. PLEASE FIND A MORE APPROPRIATE PASSWORD CHECKER COMMENTED OUT BELOW !!!
def check_pwd_security(password):
    # initializing variables that count how many characters of a type are in password
    letters = 0
    numbers = 0
    special = 0

    for char in password:
        if char.isalpha():
            letters += 1
        elif char.isdigit():
            numbers += 1
        else:
            special += 1
    return (letters > 0 and numbers > 0 and special > 0)


"""def check_pwd_security(password):
    # initializing variables that count how many characters of a type are in password
    letters = 0
    numbers = 0
    special = 0

    for char in password:
        if char.isalpha():
            letters += 1
        elif char.isdigit():
            numbers += 1
        else:
            special += 1
    return (letters > 2 and numbers > 2 and special >2)"""


# implementing a helper function for getting data about the owned stocks
def owned_stocks():

    username = db.execute("SELECT username FROM users WHERE id = ?",
                          session["user_id"])[0].get("username")

    # create empty dictionaries to store the number of shares, prices and values for the owned stocks.
    # I chose to implement multiple dictionaries and not a nested one because I believe it makes it more readable
    owned_stocks_shares = {}
    owned_stocks_prices = {}
    owned_stocks_values = {}

    # iterate through the tabel of transactions that the user made and add up the number of shares the user owns
    for row in db.execute("SELECT stock, shares FROM transactions WHERE username = ?;", username):
        # just add to the key if key alread exists
        if row.get("stock") in owned_stocks_shares:
            owned_stocks_shares[row.get("stock")] += row.get("shares")
        # otherwise initialize the key
        else:
            owned_stocks_shares[row.get("stock")] = row.get("shares")

    # store the amount of cash that the user owns in the variable money
    money = db.execute("SELECT cash FROM users WHERE username = ?", username)[
        0].get("cash")

    # initialize a variable that stores the total value of stocks owned by the user
    stock_total = 0

    # iterate through the owned_stocks (please observe that shares cannot be 0 as per definition of transactions it is non-zero)
    for stock in owned_stocks_shares:
        # get the current stock price
        owned_stocks_prices[stock] = (lookup(stock).get("price"))
        # get the current value of all the owned stocks of the symbol
        owned_stocks_values[stock] = usd(
            owned_stocks_prices[stock]*owned_stocks_shares[stock])
        # increase the over all value of all owned stocks
        stock_total += (owned_stocks_prices[stock]*owned_stocks_shares[stock])

    # return a dictionary that contains all the needed data
    return {"owned_stocks_shares": owned_stocks_shares, "owned_stocks_prices": owned_stocks_prices, "owned_stocks_values": owned_stocks_values, "money": money, "stock_total": stock_total, "username": username}

