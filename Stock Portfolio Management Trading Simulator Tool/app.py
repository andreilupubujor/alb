import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.jinja_env.filters["usd"] = usd
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///finance.db")

# Function to get stocks by theme


def get_stocks_by_theme(theme):
    """Get stocks by theme"""
    if theme == "Technology":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Tech'")
    elif theme == "Healthcare":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Healthcare'")
    elif theme == "Green Energy":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Green Energy'")
    elif theme == "Financials":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Financials'")
    elif theme == "Real Estate":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Real Estate'")
    elif theme == "Cryptocurrency":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Cryptocurrency'")
    elif theme == "Consumer Goods":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Consumer Goods'")
    elif theme == "Energy":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Energy'")
    elif theme == "Utilities":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Utilities'")
    elif theme == "Telecommunications":
        return db.execute("SELECT symbol FROM stocks WHERE category = 'Telecommunications'")
    else:
        return []


def check_cash(user_id, amount):
    """Check if user has enough cash"""
    user_cash = db.execute("SELECT cash FROM users WHERE id = :user_id",
                           user_id=user_id)[0]["cash"]
    if user_cash < amount:
        return False
    return True

# Function to check if user has enough shares


def check_shares(user_id, portfolio_id, symbol, shares):
    """Check if user has enough shares"""
    holding = db.execute("""SELECT SUM(shares) AS total_shares
                   FROM transactions
                   WHERE user_id = :user_id AND portfolio_id = :portfolio_id AND symbol = :symbol
                   GROUP BY symbol""",
                         user_id=user_id, portfolio_id=portfolio_id, symbol=symbol)
    if not holding or holding[0]["total_shares"] < shares:
        return False
    return True


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
    stocks = db.execute("""
      SELECT symbol, SUM(shares) as total_shares
      FROM transactions
      WHERE user_id = :user_id
      GROUP BY symbol
      HAVING total_shares > 0
   """, user_id=session["user_id"])

    cash = db.execute("SELECT cash FROM users WHERE id = :user_id",
                      user_id=session["user_id"])[0]["cash"]

    total_value = 0
    grand_total = cash

    for stock in stocks:
        quote = lookup(stock["symbol"])
        if not quote:
            return apology(f"Stock data for {stock['symbol']} not found", 400)
        stock["name"] = quote["name"]
        stock["price"] = quote["price"]
        stock["value"] = stock["price"] * stock["total_shares"]
        total_value += stock["value"]
        grand_total += stock["value"]

    return render_template("index.html", stocks=stocks, cash=cash, total_value=total_value, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy_stock():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        portfolio_id = int(request.form.get("portfolio_id"))

        if not symbol or shares <= 0 or not portfolio_id:
            return apology("Invalid input", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("Invalid stock symbol", 400)

        name = stock.get("name")
        category = stock.get("category", "Unknown Category")
        price = stock.get("price", 0)
        market_cap = stock.get("market_cap", "N/A")
        sustainability_score = stock.get("sustainability_score", "N/A")

        total_cost = shares * price

        if not check_cash(session["user_id"], total_cost):
            return apology(f"Not enough cash. You need ${total_cost - db.execute('SELECT cash FROM users WHERE id = :user_id', user_id=session['user_id'])[0]['cash']:.2f} more to buy {shares} shares of {symbol}.", 400)

        db.execute("UPDATE users SET cash = cash - :total_cost WHERE id = :user_id",
                   total_cost=total_cost, user_id=session["user_id"])

        db.execute("""INSERT INTO transactions
               (user_id, portfolio_id, symbol, shares, price, timestamp)
               VALUES (:user_id, :portfolio_id, :symbol, :shares, :price, CURRENT_TIMESTAMP)""",
                   user_id=session["user_id"], portfolio_id=portfolio_id,
                   symbol=symbol, shares=shares, price=price)

        db.execute("""INSERT INTO stocks (symbol, name, category, price, market_cap, sustainability_score, portfolio_id)
              VALUES (:symbol, :name, :category, :price, :market_cap, :sustainability_score, :portfolio_id)
              """, symbol=symbol, name=name, category=category, price=price,
                   market_cap=market_cap, sustainability_score=sustainability_score, portfolio_id=portfolio_id)

        flash(f"Bought {shares} shares of {symbol} for ${total_cost:.2f}")
        return redirect("/")

    portfolios = db.execute("SELECT id, theme FROM portfolios WHERE user_id = :user_id",
                            user_id=session["user_id"])
    return render_template("buy.html", portfolios=portfolios)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = :user_id ORDER BY timestamp DESC",
        user_id=session["user_id"]
    )

    if not transactions:
        flash("No transaction history available.", "info")
        return render_template("history.html", transactions=[])

    for transaction in transactions:
        transaction['price'] = float(transaction['price'])
        transaction['shares'] = int(transaction['shares'])
        transaction['total'] = transaction['shares'] * transaction.get('price', 0.0)

        if transaction['shares'] > 0:
            transaction['type'] = 'Buy'
        elif transaction['shares'] < 0:
            transaction['type'] = 'Sell'

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        user = {}
        user["id"] = rows[0]["id"]
        session["user_id"] = user["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    session.pop('user_id')
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Must provide a stock symbol", 400)

        quote = lookup(symbol)

        if not quote:
            return apology("Invalid stock symbol", 400)

        stock_data = db.execute(
            "SELECT sustainability_score FROM stocks WHERE symbol = :symbol", symbol=symbol)

        if stock_data:
            quote['sustainability_score'] = stock_data[0].get('sustainability_score', None)
        else:
            quote['sustainability_score'] = None

        return render_template("quote.html", quote=quote)

    return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 0:
            return apology("username already exists", 400)

        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            request.form.get("username"),
            generate_password_hash(request.form.get("password"))
        )

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell_stock():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        portfolio_id = int(request.form.get("portfolio_id"))

        if not symbol or shares <= 0 or not portfolio_id:
            return apology("Invalid input", 400)

        if not check_shares(session["user_id"], portfolio_id, symbol, shares):
            return apology("Not enough shares to sell", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("Invalid stock symbol", 400)

        stock_price = stock["price"]
        total_sale = shares * stock_price

        db.execute("UPDATE users SET cash = cash + :total_sale WHERE id = :user_id",
                   total_sale=total_sale, user_id=session["user_id"])

        db.execute("""INSERT INTO transactions
               (user_id, portfolio_id, symbol, shares, price, timestamp)
               VALUES (:user_id, :portfolio_id, :symbol, :shares, :price, CURRENT_TIMESTAMP)""",
                   user_id=session["user_id"], portfolio_id=portfolio_id,
                   symbol=symbol, shares=-shares, price=stock_price)

        flash(f"Sold {shares} shares of {symbol} for ${total_sale:.2f}")
        return redirect("/")

    portfolios = db.execute("SELECT id, theme FROM portfolios WHERE user_id = :user_id",
                            user_id=session["user_id"])
    portfolio_holdings = []
    for portfolio in portfolios:
        stocks = db.execute("""SELECT symbol, SUM(shares) AS total_shares
                     FROM transactions
                     WHERE user_id = :user_id AND portfolio_id = :portfolio_id
                     GROUP BY symbol
                     HAVING total_shares > 0""",
                            user_id=session["user_id"], portfolio_id=portfolio["id"])
        portfolio_holdings.append({
            "portfolio_id": portfolio["id"],
            "theme": portfolio["theme"],
            "stocks": stocks
        })
    return render_template("sell.html", portfolios=portfolios)


@app.route("/add_cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Add cash to account"""
    if request.method == "POST":
        amount = request.form.get("amount")

        if not amount or not amount.isdigit() or float(amount) <= 0:
            return apology("Please enter a valid amount.")

        db.execute("UPDATE users SET cash = cash + :amount WHERE id = :user_id",
                   amount=float(amount), user_id=session["user_id"])

        flash(f"Added ${amount} to your account.")
        return redirect("/")

    return render_template("add_cash.html")


@app.route("/reset")
def reset():
    """Reset portfolio"""
    return render_template("reset.html")


@app.route("/education")
def education():
    """Education page"""
    return render_template("education.html")


@app.route("/view_portfolios", methods=["GET"])
@login_required
def view_portfolios():
    """View portfolios"""
    portfolios = db.execute("""
      SELECT * FROM portfolios WHERE user_id = :user_id
   """, user_id=session["user_id"])

    if not portfolios:
        return apology("No portfolios found", 404)

    return render_template("view_portfolios.html", portfolios=portfolios)


@app.route("/view_stocks/<int:portfolio_id>", methods=["GET"])
@login_required
def view_stocks(portfolio_id):
    """View stocks in portfolio"""
    stocks = db.execute("""
      SELECT s.symbol, s.name, s.category, s.price, s.market_cap, s.sustainability_score,
          SUM(t.shares) AS total_shares
      FROM stocks s
      JOIN transactions t ON s.symbol = t.symbol AND s.portfolio_id = t.portfolio_id
      WHERE s.portfolio_id = :portfolio_id
      GROUP BY s.symbol, s.name, s.category, s.price, s.market_cap, s.sustainability_score
   """, portfolio_id=portfolio_id)

    if not stocks:
        return apology("No stocks found for this portfolio", 404)

    portfolio = db.execute("""
      SELECT * FROM portfolios WHERE id = :portfolio_id
   """, portfolio_id=portfolio_id)

    if not portfolio:
        return apology("Portfolio not found", 404)

    return render_template("view_stocks.html", stocks=stocks, portfolio=portfolio[0])


@app.route("/delete_portfolio", methods=["GET", "POST"])
@login_required
def delete_portfolio():
    """Delete portfolio"""
    if request.method == "POST":
        portfolio_id = request.form.get("portfolio_id")

        portfolio = db.execute("SELECT * FROM portfolios WHERE id = :portfolio_id AND user_id = :user_id",
                               portfolio_id=portfolio_id, user_id=session["user_id"])

        if not portfolio:
            return apology("Portfolio not found or you don't have permission to delete it.", 404)

        try:
            db.execute("DELETE FROM transactions WHERE portfolio_id = :portfolio_id",
                       portfolio_id=portfolio_id)
            db.execute("DELETE FROM logs WHERE portfolio_id = :portfolio_id",
                       portfolio_id=portfolio_id)
            db.execute("DELETE FROM portfolio_stocks WHERE portfolio_id = :portfolio_id",
                       portfolio_id=portfolio_id)

            db.execute("DELETE FROM portfolios WHERE id = :portfolio_id AND user_id = :user_id",
                       portfolio_id=portfolio_id, user_id=session["user_id"])

            flash("Portfolio deleted successfully!")
            return redirect("/view_portfolios")

        except IntegrityError as e:
            flash(f"Failed to delete portfolio: {e}", "error")
            flash("This portfolio may still have associated transactions or stock holdings.", "error")
            flash("Please review and resolve any related data before attempting to delete again.", "error")
            return redirect("/view_portfolios")

    portfolios = db.execute("SELECT * FROM portfolios WHERE user_id = :user_id",
                            user_id=session["user_id"])

    return render_template("delete_portfolio.html", portfolios=portfolios)


@app.route("/create_portfolio", methods=["GET", "POST"])
@login_required
def create_portfolio_view():
    """Create portfolio"""
    if request.method == "POST":
        theme = request.form.get("theme")
        if not theme:
            return apology("Must select a theme", 400)

        stocks_in_theme = get_stocks_by_theme(theme)

        try:
            db.execute("INSERT INTO portfolios (user_id, theme) VALUES (:user_id, :theme)",
                       user_id=session["user_id"], theme=theme)

            result = db.execute("SELECT last_insert_rowid()")
            portfolio_id = result[0]["last_insert_rowid()"]

        except (IndexError, KeyError, TypeError):
            return apology("Failed to create portfolio", 500)

        for stock in stocks_in_theme:
            db.execute("INSERT INTO portfolio_stocks (portfolio_id, stock_symbol) VALUES (:portfolio_id, :stock_symbol)",
                       portfolio_id=portfolio_id, stock_symbol=stock["symbol"])

        flash(f"Your '{theme}' portfolio has been created!")
        return redirect(url_for("view_portfolios"))

    return render_template("create_portfolio.html", themes=['Technology',
                                                            'Healthcare',
                                                            'Green Energy',
                                                            'Financials',
                                                            'Real Estate',
                                                            'Cryptocurrency',
                                                            'Consumer Goods',
                                                            'Energy',
                                                            'Utilities',
                                                            'Telecommunications'])


@app.route("/leaderboard")
@login_required
def leaderboard():
    """Leaderboard"""
    users = db.execute("SELECT id, username, cash FROM users")

    leaderboard = []

    for user in users:
        stocks = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM transactions
        WHERE user_id = :user_id
        GROUP BY symbol
        HAVING total_shares > 0
      """, user_id=user["id"])

        stock_value = 0
        for stock in stocks:
            quote = lookup(stock["symbol"])

            if quote:
                stock_value += stock["total_shares"] * quote["price"]

        total_value = user["cash"] + stock_value
        leaderboard.append({"username": user["username"], "total_value": total_value})

    leaderboard.sort(key=lambda x: x["total_value"], reverse=True)

    return render_template("leaderboard.html", leaderboard=leaderboard)


@app.route('/some_route')
def some_view():
    error_occurred = True
    if error_occurred:
        return render_template('apology.html', message="An unexpected error occurred.")
