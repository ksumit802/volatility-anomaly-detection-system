from flask import Flask, request, jsonify
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

app = Flask(__name__)


def fetch_data(symbol, start, end):
    df = yf.download(symbol, start=start, end=end)
    df['Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Return'].rolling(window=10).std()
    df.dropna(inplace=True)
    return df


def detect_anomalies(df, threshold=2.0):
    mean_vol = df['Volatility'].mean()
    std_vol = df['Volatility'].std()
    cutoff = mean_vol + threshold * std_vol
    anomalies = df[df['Volatility'] > cutoff]
    return anomalies[['Volatility']].reset_index()


@app.route('/volatility', methods=['GET'])
def get_volatility():
    symbol = request.args.get('symbol')
    start = request.args.get('start')
    end = request.args.get('end')

    if not all([symbol, start, end]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        df = fetch_data(symbol, start, end)
        anomalies = detect_anomalies(df)
        results = [
            {
                'date': row['Date'].strftime('%Y-%m-%d'),
                'volatility': round(row['Volatility'], 5)
            }
            for _, row in anomalies.iterrows()
        ]
        return jsonify({'symbol': symbol, 'anomalies': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
