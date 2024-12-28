import requests
from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    def escape(s):
        for old, new in [
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

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    api_key = "ADD YOUR API KEY"
    alpha_vantage_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol.upper()}&interval=5min&apikey={api_key}"

    try:
        response = requests.get(alpha_vantage_url)
        response.raise_for_status()
        data = response.json()

        if "Time Series (5min)" in data:
            latest_time = list(data["Time Series (5min)"].keys())[0]
            latest_data = data["Time Series (5min)"][latest_time]

            return {
                "name": str(latest_data["2. close"]),
                "price": float(latest_data["4. close"]),
                "symbol": symbol.upper()
            }
    except requests.RequestException as e:
        print(f"Alpha Vantage request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Alpha Vantage data parsing error: {e}")

    cs50_url = f"https://finance.cs50.io/quote?symbol={symbol.upper()}"

    try:
        response = requests.get(cs50_url)
        response.raise_for_status()
        quote_data = response.json()
        return {
            "name": quote_data["companyName"],
            "price": quote_data["latestPrice"],
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"CS50 Finance request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"CS50 Finance data parsing error: {e}")

    return None


def usd(value):
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"
