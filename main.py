from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
API_SECRET ="f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

client = Client(API_KEY, API_SECRET, testnet=True)

@app.route("/")
def home():
    return "Binance Hedge Webhook is running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data"}), 400

    try:
        symbol = data["symbol"]           # مثل: "BTCUSDT"
        side = data["side"].upper()       # "BUY" or "SELL"
        qty = float(data["qty"])          # الكمية
        tp_points = float(data.get("tp_points", 0))  # عدد النقاط للتيك بروفت
        sl_points = float(data.get("sl_points", 0))  # عدد النقاط للستوب لوز

        # نحدد positionSide بناءً على الـ side
        positionSide = "LONG" if side == "BUY" else "SHORT"

        # نجيب سعر السوق الحالي
        price_data = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(price_data["price"])

        # نحسب أسعار TP/SL
        tp_price, sl_price = tp_points, sl_points


        # 1️⃣ أمر الدخول
        entry = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty,
            positionSide=positionSide
        )

        tp_order, sl_order = None, None

        # 2️⃣ أمر Take Profit
        if tp_price:
            tp_order = client.futures_create_order(
                symbol=symbol,
                side="SELL" if positionSide == "LONG" else "BUY",
                type="TAKE_PROFIT_MARKET",
                stopPrice=round(tp_price, 2),
                closePosition=True,
                positionSide=positionSide
            )

        # 3️⃣ أمر Stop Loss
        if sl_price:
            sl_order = client.futures_create_order(
                symbol=symbol,
                side="SELL" if positionSide == "LONG" else "BUY",
                type="STOP_MARKET",
                stopPrice=round(sl_price, 2),
                closePosition=True,
                positionSide=positionSide
            )

        return jsonify({
            "entry": entry,
            "take_profit": tp_order,
            "stop_loss": sl_order,
            "current_price": current_price,
            "tp_price": tp_price,
            "sl_price": sl_price
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
