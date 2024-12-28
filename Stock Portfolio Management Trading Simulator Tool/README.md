## Stock Portfolio Management Trading Simulator Tool

#### Brief: A web application for practicing stock trading and portofolio management.
#### Video Demo:  Available at request
#### Full Description:

### Stock Portfolio Management Trading Simulator Tool
==========================

This web application is a comprehensive stock trading simulator designed to allow users to practice trading stocks and managing portofolio in a virtual environment. The app allows users to create an account, deposit virtual cash, buy and sell stocks based on real-time market data. Additionally, the app enables users to create and manage multiple portfolios, just like professional traders would in real life. Users can diversify their investments by creating separate portfolios for different investment strategies.

## Key Features
---------------

* User Registration and Login: Users can create an account and log in to access their portfolio.
* Virtual Cash Deposit: Users can deposit virtual cash into their account to start trading.
* Stock Buying and Selling: Users can buy and sell stocks based on real-time market data.
* Portfolio Management: Users can create, manage, and track multiple portfolios, including adding or removing stocks.
* Portfolio Creation: Users can create new portfolios with a specific theme, such as technology, healthcare, or finance.
* Portfolio Diversification: Users can diversify their investments by creating separate portfolios for different asset classes, such as stocks, bonds, or ETFs.
* Leaderboard: The app provides a leaderboard that ranks users based on their portfolio value.

## Functionality
--------------

* `index` function: Displays the user's portfolio, including their stock holdings and cash balance.
* `buy` function: Allows users to buy stocks by specifying the stock symbol and number of shares.
* `sell` function: Allows users to sell stocks by specifying the stock symbol and number of shares.
* `quote` function: Provides real-time market data for a specified stock symbol.
* `register` function: Allows users to create an account.
* `login` function: Allows users to log in to their account.
* `logout` function: Logs users out of their account.
* `leaderboard` function: Displays the leaderboard, ranking users by their portfolio value.
* `create_portfolio` function: Allows users to create a new portfolio with a specific theme.
* `view_portfolios` function: Displays a list of all portfolios created by the user.
* `view_stocks` function: Displays the stocks held in a specific portfolio.
* `delete_portfolio` function: Allows users to delete a portfolio.

## API Integration
-----------------

The app integrates with the Alpha Vantage API (www.alphavantage.co) to retrieve real-time market data for stocks. This allows users to make informed investment decisions based on up-to-date market information.

## Front-end Design
-----------------

The app features a beautiful and user-friendly design, built using HTML, CSS, and JavaScript. The design is responsive and works well on a variety of devices, including desktops, laptops, tablets, and mobile phones.

## Database Schema
-----------------

The app uses the following SQL tables to store data:

### users table

* `id` (primary key): Unique identifier for each user
* `username`: Username chosen by the user
* `hash`: Password hash for the user
* `cash`: Cash balance for the user

### portfolios table

* `id` (primary key): Unique identifier for each portfolio
* `user_id` (foreign key): References the `id` column in the `users` table
* `theme`: Theme of the portfolio (e.g. technology, healthcare, etc.)

### stocks table

* `symbol` (primary key): Stock symbol (e.g. AAPL, GOOG, etc.)
* `name`: Name of the stock
* `category`: Category of the stock (e.g. technology, healthcare, etc.)

### transactions table

* `id` (primary key): Unique identifier for each transaction
* `user_id` (foreign key): References the `id` column in the `users` table
* `portfolio_id` (foreign key): References the `id` column in the `portfolios` table
* `symbol` (foreign key): References the `symbol` column in the `stocks` table
* `shares`: Number of shares bought or sold
* `price`: Price of the stock at the time of the transaction
* `timestamp`: Timestamp of the transaction

### portfolio_stocks table

* `id` (primary key): Unique identifier for each portfolio stock
* `portfolio_id` (foreign key): References the `id` column in the `portfolios` table
* `stock_symbol` (foreign key): References the `symbol` column in the `stocks` table
* `shares`: Number of shares held in the portfolio

## Libraries and Frameworks
-------------------------

* Flask: A micro web framework for building web applications.
* CS50 Library: The library provided by Harvard University's CS50 course, which includes functions for interacting with a SQLite database and handling user input.
* SQLite: A lightweight relational database management system.

## Knowledge Applied
------------------------

* SQL: The app uses SQL to interact with the SQLite database, including creating tables, inserting data, and querying data.
* Python: The app is written in Python, using the Flask framework and CS50 library.
* HTML and CSS: The app uses HTML and CSS to render web pages and style the user interface.
* JavaScript: The app uses JavaScript to handle user input and update the user interface dynamically.
* Security: The app applies security principles, such as validating user input and using secure password storage.

## Additional Notes
------------------

* The app is designed for educational purposes, allowing users to practice trading stocks and managing portfolios in a simulated environment.
* The app uses real-time market data to provide a realistic trading experience.
* The app's portfolio management features allow users to develop and test different investment strategies, making it a valuable tool for both beginners and experienced traders.

