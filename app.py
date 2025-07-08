from flask import Flask, request, jsonify
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Stock Volatility Anomaly Detection API</h1>
    <p>Available endpoint: <code>/volatility?symbol=SYMBOL&start=YYYY-MM-DD&end=YYYY-MM-DD</code></p>
    <p>Example: <a href="/volatility?symbol=AAPL&start=2023-01-01&end=2023-12-31">/volatility?symbol=AAPL&start=2023-01-01&end=2023-12-31</a></p>
    """

def validate_stock_symbol(symbol):
    """Validate the stock symbol format"""
    if not isinstance(symbol, str) or not symbol.isalpha():
        raise ValueError("Stock symbol must be alphabetic characters only")
    return symbol.upper()

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")

def fetch_data(symbol, start, end):
    """Fetch and clean stock data"""
    try:
        # Validate inputs
        symbol = validate_stock_symbol(symbol)
        start_date = validate_date(start)
        end_date = validate_date(end)
        
        if start_date >= end_date:
            raise ValueError("End date must be after start date")

        # Download data with validation
        data = yf.Ticker(symbol)
        df = data.history(start=start, end=end)
        
        if df.empty:
            raise ValueError(f"No data available for {symbol} between {start} and {end}")
            
        # Process data
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        df = df.dropna(subset=['Close'])
        df['Return'] = df['Close'].pct_change()
        df['Volatility'] = df['Return'].rolling(window=10).std()
        df = df.dropna()
        
        return df
        
    except Exception as e:
        raise ValueError(f"Data fetch error: {str(e)}")

def detect_anomalies(df, threshold=2.0):
    """Detect volatility anomalies"""
    try:
        df['Volatility'] = pd.to_numeric(df['Volatility'], errors='coerce')
        df = df.dropna(subset=['Volatility'])
        
        if df.empty:
            return pd.DataFrame()
            
        mean_vol = df['Volatility'].mean()
        std_vol = df['Volatility'].std()
        cutoff = mean_vol + threshold * std_vol
        anomalies = df[df['Volatility'] > cutoff]
        return anomalies[['Volatility']].reset_index()
    except Exception as e:
        raise ValueError(f"Anomaly detection error: {str(e)}")

@app.route('/volatility', methods=['GET'])
def get_volatility():
    try:
        # Get and validate parameters
        symbol = request.args.get('symbol', '').strip()
        start = request.args.get('start', '').strip()
        end = request.args.get('end', '').strip()
        threshold = float(request.args.get('threshold', 2.0))
        
        if not all([symbol, start, end]):
            return jsonify({
                'error': 'Missing parameters',
                'required': {
                    'symbol': 'Stock symbol (e.g. AAPL)',
                    'start': 'Start date (YYYY-MM-DD)',
                    'end': 'End date (YYYY-MM-DD)'
                },
                'optional': {
                    'threshold': 'Standard deviation threshold (default: 2.0)'
                }
            }), 400
            
        # Process request
        df = fetch_data(symbol, start, end)
        anomalies = detect_anomalies(df, threshold)
        
        # Format response
        results = [{
            'date': row['Date'].strftime('%Y-%m-%d'),
            'volatility': round(row['Volatility'], 5),
            'symbol': symbol
        } for _, row in anomalies.iterrows()]
        
        return jsonify({
            'symbol': symbol,
            'period': f"{start} to {end}",
            'threshold': threshold,
            'anomaly_count': len(results),
            'anomalies': results if results else "No anomalies detected"
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid input',
            'message': str(e),
            'hint': 'Check symbol exists and dates are in YYYY-MM-DD format'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Processing error',
            'message': str(e),
            'hint': 'Please check your parameters and try again'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)