from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = os.getenv("f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543")
API_SECRET = os.getenv("f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70")

client = Client(API_KEY, API_SECRET, testnet=True)

@app.route("/")
def home():
    return "Binance Webhook is running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400

    try:
        symbol = data["symbol"]
        side = data["side"]
        qty = data["qty"]

        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty
        )
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
