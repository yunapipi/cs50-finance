import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import sqlite3

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    #POST経由で判定
    symbol = "abc"
    quote = lookup(symbol)
    symbol_symbol = quote.get("symbol")
    price = quote.get("price")
    print("buyの実験")
    print(symbol_symbol)
    print (quote)
    print(symbol)
    cash_dict = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    cash = cash_dict[0]["cash"]

    if request.method == "POST":
        shares = request.form.get("shares")
        user_id = session["user_id"]
        symbol = request.form.get(symbol)

        #symbolが空白の時
        if symbol == "":
            return apology("Stock symbol not valid, please try again")
        #symbolが存在しない場合
        elif quote == None:
            return apology("Stock symbol not valid, please try again")
        #sharesが整数のとき
        elif  isinstance(shares, int):
            #sharesがマイナスの時
            if shares < 1:
                return apology("must provide valid number of shares (integer)")
        else:
            print(price)
            #ユーザが現在の価格で株式数を購入できない場合
            if cash < price * shares:
                return apology("you have not enough money")
            else:
                total = price * shares
                #buyの処理を実行する
                try:
                    db.execute("INSERT INTO buy (Symbol, Name, Shares, Price, Total) VALUES (?, ?, ?, ?, ?)", quote, symbol_symbol, shares, price, total)
                    return redirect("/")
                except :
                    return apology("error")
    else:
        return render_template("buy.html")






    #ユーザの入力をPOST経由で/buyに送信します。


    # #ユーザが現在の価格で株式数を購入できない場合は、購入を完了せずにapologyを表示します。
    # quote = lookup(request.form.get('latestPrice'))
    # cost = shares * quote
    # #持っているお金
    # cash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
    # if cash < cost:
    #     return apology("you cannot have enough money")
    # else:
    #     db.execute(INSERT INTO users (user_id, name, shares,price, type, symbol)
    #     VALUES ('user_id', name,'shares','price', type, symbol);)
    # else:
    #     return render_template("buy.html")




@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if not symbol:
            return apology("please enter a symbol")

        elif quote == None:
            return apology("Symbol does not exist")
        else:
            brand = quote.get("name")
            price = quote.get("price")
            return render_template("quoted.html", symbol = brand, price = price)

    if request.method == "GET":
        return render_template("quote.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Missing username")
        elif not request.form.get("password") :
            return apology("Missing password")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match")

        hash = generate_password_hash(request.form.get("password"))
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",username, hash)
            return redirect("/")
        except :
            return apology("You cannot use this username")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
