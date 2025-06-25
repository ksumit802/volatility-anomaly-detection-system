# Volatility Anomaly Detector

This project detects abnormal spikes in volatility for publicly traded equities using Python, Pandas, and NumPy. It provides a Flask API to retrieve detected anomalies for a given stock and date range.

## 🔧 Features
- Pulls historical data using `yfinance`
- Calculates rolling 10-day volatility
- Flags anomalies exceeding 2 standard deviations above the mean
- Exposes an HTTP API to fetch anomalies

## 🚀 Usage
Run locally:
```bash
pip install -r requirements.txt
python app.py
```

Query the API:
```bash
curl "http://127.0.0.1:5000/volatility?symbol=AAPL&start=2024-01-01&end=2024-06-01"
```

📌 *Note: This API runs locally by default (127.0.0.1:5000). Public deployment is planned for future versions.*

## 🐳 Run with Docker
```bash
docker build -t volatility-anomaly-detection-system .
docker run -p 5000:5000 volatility-anomaly-detection-system .
```

## Planned Next Steps
- Integrate LangChain + ChromaDB for semantic search over anomaly history
- Plan to add GitHub Actions CI/CD workflow for automation
- Visualize anomalies using Streamlit or Dash
- Adding basic ML model (Random Forest) with synthetic labels