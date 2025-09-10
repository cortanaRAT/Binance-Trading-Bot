from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
API_SECRET = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

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

    if not all([symbol, side]):
        return jsonify({"error": "Missing symbol or side"}), 400

    # السعر الحالي من Binance
    price_data = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(price_data['price'])

    # اللوت ثابت
    qty = 0.02

    # تحديد TP و SL بالنقاط
    STOP = 10000
    TAKE = 20000

    if side.upper() == "BUY":
        tp_price = current_price + TAKE
        sl_price = current_price - STOP
    else:  # SELL
        tp_price = current_price - TAKE
        sl_price = current_price + STOP

    try:
        # فتح الصفقة الرئيسية
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty
        )

        # أوامر TP و SL
        tp_order = client.futures_create_order(
            symbol=symbol,
            side="SELL" if side.upper()=="BUY" else "BUY",
            type="LIMIT",
            price=round(tp_price, 2),
            quantity=qty,
            reduceOnly=True
        )

        sl_order = client.futures_create_order(
            symbol=symbol,
            side="SELL" if side.upper()=="BUY" else "BUY",
            type="STOP_MARKET",
            stopPrice=round(sl_price, 2),
            quantity=qty,
            reduceOnly=True
        )

        return jsonify({
            "order": order,
            "take_profit": tp_order,
            "stop_loss": sl_order
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
