import flask
from flask import Flask, render_template, request, jsonify, session
import yfinance as yf
import numpy as np
from flask_session import Session
from scipy.stats import norm  # Import the norm function

app = Flask(__name__)

# Configure the Flask session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
Session(app)

# ... (rest of your code remains the same)


# Create a list of example stocks
example_stocks = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "FB", "name": "Meta Platforms, Inc. (Facebook)"},
    {"symbol": "TSLA", "name": "Tesla, Inc."},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "WMT", "name": "Walmart Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc."}
]

@app.route('/')
def index():
    return render_template('index.html',example_stocks=example_stocks)

@app.route('/get_historical_stock_data', methods=['GET'])
def get_historical_stock_data():
    stock_symbol = request.args.get('stock_symbol')

    # Fetch historical stock data using yfinance
    stock_data = yf.download(stock_symbol, start="2021-01-01", end="2023-12-31")

    # Prepare data for the historical stock chart
    historical_stock_labels = stock_data.index.strftime('%Y-%m-%d').tolist()
    historical_stock_values = stock_data['Close'].tolist()

    stock_data = {
        'labels': historical_stock_labels,
        'datasets': [
            {
                'label': 'Historical Stock Data',
                'data': historical_stock_values,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            }
        ]
    }

    return jsonify(stock_data)

@app.route('/get_historical_option_data', methods=['GET'])
def get_historical_option_data():
    stock_symbol = request.args.get('stock_symbol')

    # Fetch historical option data for the selected stock symbol
    # Replace this with your data source or model
    # historical_option_data = fetch_historical_option_data(stock_symbol)

    # Placeholder data for the historical option chart
    historical_option_labels = ['2021-01-01', '2021-02-01', '2021-03-01', '2021-04-01', '2021-05-01']
    historical_option_values = [100, 110, 120, 105, 115]

    option_data = {
        'labels': historical_option_labels,
        'datasets': [
            {
                'label': 'Historical Option Data',
                'data': historical_option_values,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            }
        ]
    }

    return jsonify(option_data)


@app.route('/display_option_data', methods=['GET'])
def display_option_data():
    # Retrieve option_values_data from the session
    option_values_data = session.get('option_values_data', None)

    if option_values_data:
        # Perform actions with option_values_data, such as rendering it in a template
        return render_template('display_option_data.html', option_values_data=option_values_data)
    else:
        # Handle the case when option_values_data is not in the session
        return "Option data not found in session."

# ... (other routes and functions)


def calculate_option_values(stock_price, striking_price, maturity):
    # Modify this function to calculate option values based on your risk model
    # This is just a placeholder function
    r = 0.05  # Example interest rate (5%)
    time_values = np.linspace(0, 1, maturity)
    option_values = [max(stock_price - striking_price, 0) * np.exp(-r * t) for t in time_values]
    return option_values

@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        # Get user inputs from the form
        stock_symbol = request.form['stockSelect']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        strike_price = float(request.form['strikeInput'])
        interest_rate = float(request.form['interest_rate']) / 100.0  # Convert to decimal
        volatility = float(request.form['volatility']) / 100.0  # Convert to decimal
        position = request.form['position']
        premium = float(request.form['premium'])



        # Fetch historical stock price data using yfinance
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date)

        # Calculate call option price using the Black-Scholes model
        stock_price = stock_data['Adj Close'][-1]
        time_to_expiry = (np.datetime64(end_date) - np.datetime64(start_date)).astype('timedelta64[D]').astype(int) / 365.0


        d1 = (np.log(stock_price / strike_price) + ((interest_rate + (volatility ** 2) / 2) * time_to_expiry)) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)

        call_option_price = stock_price * norm.cdf(d1) - strike_price * np.exp(-interest_rate * time_to_expiry) * norm.cdf(d2)

         # Calculate premiums
        if position == 'long':
            long_premium = -premium
            short_premium = 0
        elif position == 'short':
            long_premium = 0
            short_premium = premium
        else:
            long_premium = 0
            short_premium = 0
        profit_loss = call_option_price + long_premium + short_premium

        # Display the results
        return render_template('result.html', call_option_price=round(call_option_price,2), position=position, long_premium=round(long_premium,2), short_premium=round(short_premium,2), profit_loss=round(profit_loss,2))

    except Exception as e:
        error_message = str(e)
        return render_template('error.html', error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)
