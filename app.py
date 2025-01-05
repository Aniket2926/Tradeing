from flask import Flask, render_template
import yfinance as yf
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
import os

# Initialize Flask app
app = Flask(__name__)

# List of 15 Indian stocks (Yahoo Finance tickers for NSE)
STOCKS = [
    "TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFC.NS", "ICICIBANK.NS",
    "AXISBANK.NS", "SBIN.NS", "HDFCBANK.NS", "LT.NS", "BAJFINANCE.NS",
    "ITC.NS", "ONGC.NS", "TATASTEEL.NS", "BHARTIARTL.NS", "WIPRO.NS"
]

# Function to fetch and analyze stock data
def fetch_and_analyze():
    try:
        print("Fetching stock data...")
        stock_data = []
        for stock in STOCKS:
            ticker = yf.Ticker(stock)
            history = ticker.history(period="6mo")

            if not history.empty:
                # Extract latest data
                current_data = history.iloc[-1]
                close_price = current_data['Close']
                open_price = current_data['Open']
                change_percent = ((close_price - open_price) / open_price) * 100

                # Calculate SMAs
                sma_50 = history['Close'].rolling(window=50).mean().iloc[-1] if len(history) >= 50 else "N/A"
                sma_100 = history['Close'].rolling(window=100).mean().iloc[-1] if len(history) >= 100 else "N/A"
                sma_200 = history['Close'].rolling(window=200).mean().iloc[-1] if len(history) >= 200 else "N/A"

                # Determine Buy/Sell signal
                signal = "Buy" if sma_50 > sma_100 else "Sell"

                # Append row data
                stock_data.append(f"""
                    <tr>
                        <td>{stock.replace(".NS", "")}</td>
                        <td>₹{close_price:.2f}</td>
                        <td>{change_percent:.2f}%</td>
                        <td>45</td>
                        <td>{sma_50}</td>
                        <td>{sma_100}</td>
                        <td>{sma_200}</td>
                        <td>{signal}</td>
                    </tr>
                """)

            else:
                # Handle stocks with no data
                stock_data.append(f"""
                    <tr>
                        <td>{stock.replace(".NS", "")}</td>
                        <td colspan="7" style="text-align: center;">Data Not Available</td>
                    </tr>
                """)

        # Combine rows into table content
        table_content = "\n".join(stock_data)

        # Load HTML template and inject table content
        with open("templates/stock_data.html", "r") as template_file:
            html_template = template_file.read()

        updated_html = html_template.replace("{{ table_content }}", table_content)

        # Save updated HTML to the file
        with open("templates/stock_data.html", "w") as output_file:
            output_file.write(updated_html)

        print("Stock data updated successfully!")

    except Exception as e:
        print(f"Error fetching stock data: {e}")

# Scheduler to fetch and analyze data daily
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_analyze, "cron", hour=20, minute=50)  # Set to your preferred time
    scheduler.start()
    print("Scheduler started!")

# Flask route to display stock updates
@app.route("/")
def index():
    return render_template("stock_data.html")

# Run the app
if __name__ == "__main__":
    print("Starting Optimist.Trader...")
    fetch_and_analyze()  # Initial data fetch
    start_scheduler()    # Start scheduler

    # Use PORT environment variable for deployment, default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
