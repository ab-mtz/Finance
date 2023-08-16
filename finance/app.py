import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


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
    """Show portfolio of stocks"""

    # Querying for stocks
    stocks = db.execute(
        "SELECT symbol, name, SUM(quantity) AS sum FROM stocks WHERE user_id = ? GROUP BY symbol", session["user_id"])

    # Querying fo cash
    cashDict = db.execute(
        "SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = cashDict[0]["cash"]
    stocksValue = 0

    # Calculating
    for sym in stocks:
        # Quote for actual price
        quotedValue = lookup(sym["symbol"])

        # Sum stocks value
        stocksValue = stocksValue + (sym["sum"]*quotedValue["price"])

        # Store quoted values into dict
        sym.update(quotedValue)

    return render_template("portafolio.html", stocks=stocks, cash=cash, stocksValue=stocksValue)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Check for a valid Symbol
        if lookup(symbol):
            result = lookup(symbol)

            # Check for a valid Share quantity
            if not shares.isdigit or not shares.isdecimal():
                return apology("Enter a valid number of shares", 400)
            else:
                n = result["price"]*int(shares)
                cashTr = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

                # Check for enough cash
                if (n > cashTr[0]["cash"]):
                    return apology("You don't have enough cash", 400)
                # Buy
                else:
                    # Register of buy into stocks data base
                    date_time = datetime.now()
                    db.execute("INSERT INTO stocks (user_id, symbol, name, quantity, price, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            session["user_id"], symbol, result["name"], shares, result["price"], "BUY", date_time)
                    # Update cash of user
                    cashTr[0]["cash"] = cashTr[0]["cash"] - n

                    db.execute("UPDATE users SET cash = ? WHERE id = ?", cashTr[0]["cash"], session["user_id"])

                    return redirect("/")
        else:
            return apology("Please enter a valid symbol", 400)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    stocks = db.execute("SELECT * FROM stocks WHERE user_id = ?", session["user_id"])

    return render_template("history.html", stocks=stocks)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        if lookup(symbol):
            result = lookup(symbol)
            return render_template("quoted.html", result=result)
        else:
            return apology("Symbol not found", 400)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted

        elif not request.form.get("password"):
            return apology("must provide password confirmation", 400)

        # Check availibilty of username

        elif db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")):
            return apology("Username already in use", 400)

        # Check that password and confirmation are equals

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Pasword and pasword confirmation are diferent", 400)

        # If everything is ok, proceed to store values into db

        else:
            username = request.form.get("username")
            password = request.form.get("password")
            hash = generate_password_hash(password)

            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Check for symbol
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Symbol not selected")

        shares = request.form.get("shares")

        # Querying db
        stocks = db.execute("SELECT symbol, SUM(quantity) AS sum FROM stocks WHERE user_id = ? and symbol = ?",
                            session["user_id"], symbol)

        # Quoting to check current price
        quoted = lookup(symbol)

        # Check for a valid Shares quantity
        if int(shares) < 1 or int(shares) > stocks[0]["sum"]:
            return apology("Enter a valid number of shares", 400)

        else:
            # Updating Cash
            cashTr = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
            n = quoted["price"] * int(shares)
            cashTr[0]["cash"] = cashTr[0]["cash"] + n
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cashTr[0]["cash"], session["user_id"])

            # Adding transaction to db
            shares = -abs(int(shares))
            date_time = datetime.now()
            db.execute("INSERT INTO stocks (user_id, symbol, name, quantity, price, type, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    session["user_id"], symbol, quoted["name"], shares, quoted["price"], 'SELL', date_time)

            return redirect("/")

    else:
        stocks = db.execute("SELECT symbol, SUM(quantity) AS sum FROM stocks WHERE user_id = ? GROUP BY symbol", session["user_id"])
        print(stocks)

        return render_template("sell.html", stocks=stocks)


@app.route("/user", methods=["GET", "POST"])
@login_required
def user():
    """Sell shares of stock"""
    if request.method == "POST":

        print("Hello world")
    else:
        userInfo = db.execute("SELECT username, cash FROM users WHERE id = ?", session["user_id"])

        print(userInfo)
        return render_template("user.html", userInfo=userInfo)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Get stock quote."""
    if request.method == "POST":
        currentPass = request.form.get("currentPass")
        newPass = request.form.get("newPass")
        confirmation = request.form.get("confirmation")
        # Check for inputs
        dbInfo = db.execute("SELECT id, hash FROM users WHERE id = ?", session["user_id"])

        if check_password_hash(dbInfo[0]["hash"], currentPass) == 0:
            return apology("The current password is incorrect", 403)

        elif newPass != confirmation:
            return apology("New password and confirmation are not equal", 403)

        elif check_password_hash(dbInfo[0]["hash"], newPass) == 1:
            return apology("New password must be different to the old one", 403)

        else:
            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newPass), session["user_id"])
            return redirect("user.html")

    else:
        user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        return render_template("pass.html", user=user)


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():

    if request.method == "POST":

        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        print(cash)
        amount = request.form.get("amount")
        print(amount)
        cash[0]["cash"] = cash[0]["cash"] + int(amount)
        print(cash)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash[0]["cash"], session["user_id"])

        # I'm deliberately omitting checking the card validity and simply exemplifying how the interface would look like with a precharged card method.

        return redirect("/")

    else:
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        username = username[0]["username"]
        return render_template("cash.html", username=username)