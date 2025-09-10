from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET, testnet=True)

@app.route("/")
def home():
    return "Binance Webhook is running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")

    if not all([symbol, side, qty]):
        return jsonify({"error": "Missing symbol, side, or qty"}), 400

    try:
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=float(qty)
        )
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
