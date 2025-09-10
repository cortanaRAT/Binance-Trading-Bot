from flask import Flask, request, jsonify
from binance.client import Client

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

    side = side.upper()
    if side not in ["BUY", "SELL"]:
        return jsonify({"error": "Invalid side, must be BUY or SELL"}), 400

    price_data = client.futures_symbol_ticker(symbol=symbol)
    current_price = float(price_data['price'])

    qty = 0.02
    STOP = 10000
    TAKE = 20000

    if side == "BUY":
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

        reverse_side = "SELL" if side == "BUY" else "BUY"

        # TP
        tp_order = client.futures_create_order(
            symbol=symbol,
            side=reverse_side,
            type="LIMIT",
            price=round(tp_price, 2),
            quantity=qty,
            reduceOnly=True,
            timeInForce="GTC"
        )

        # SL
        sl_order = client.futures_create_order(
            symbol=symbol,
            side=reverse_side,
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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
