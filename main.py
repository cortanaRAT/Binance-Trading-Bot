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
        tp = float(data.get("tp", 0))     # سعر التيك بروفت
        sl = float(data.get("sl", 0))     # سعر الستوب لوز

        # نحدد positionSide بناءً على الـ side
        positionSide = "LONG" if side == "BUY" else "SHORT"

        # نجيب سعر السوق الحالي
        price_data = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(price_data["price"])

        # تحقق من صحة TP/SL
        if positionSide == "LONG":
            if tp and tp <= current_price:
                return jsonify({"error": f"TP ({tp}) لازم يكون أعلى من سعر السوق {current_price}"}), 400
            if sl and sl >= current_price:
                return jsonify({"error": f"SL ({sl}) لازم يكون أقل من سعر السوق {current_price}"}), 400
        else:  # SHORT
            if tp and tp >= current_price:
                return jsonify({"error": f"TP ({tp}) لازم يكون أقل من سعر السوق {current_price}"}), 400
            if sl and sl <= current_price:
                return jsonify({"error": f"SL ({sl}) لازم يكون أعلى من سعر السوق {current_price}"}), 400

        # 1️⃣ أمر الدخول
        entry = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=qty,
            positionSide=positionSide
        )

        tp_order, sl_order = None, None

        # 2️⃣ أمر Take Profit (اختياري)
        if tp > 0:
            tp_order = client.futures_create_order(
                symbol=symbol,
                side="SELL" if positionSide == "LONG" else "BUY",
                type="TAKE_PROFIT_MARKET",
                stopPrice=tp,
                closePosition=True,
                positionSide=positionSide
            )

        # 3️⃣ أمر Stop Loss (اختياري)
        if sl > 0:
            sl_order = client.futures_create_order(
                symbol=symbol,
                side="SELL" if positionSide == "LONG" else "BUY",
                type="STOP_MARKET",
                stopPrice=sl,
                closePosition=True,
                positionSide=positionSide
            )

        return jsonify({
            "entry": entry,
            "take_profit": tp_order,
            "stop_loss": sl_order
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
