from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

# 🔑 API keys الخاصة بك
API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
SECRET_KEY = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

client = Client(API_KEY, SECRET_KEY, testnet=true)

# ✅ فحص إذا الحساب Hedge Mode أو One-Way
def get_position_mode():
    try:
        res = client.futures_get_position_mode()
        if res.get("dualSidePosition"):  
            return "HEDGE"
        else:
            return "ONEWAY"
    except Exception as e:
        print("❌ Error fetching position mode:", e)
        return "ONEWAY"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON data"}), 400

    symbol = data.get("symbol", "BTCUSDT")
    side = data.get("side", "BUY").upper()
    qty = float(data.get("qty", 0.01))
    price = data.get("price", "market")
    reduce_only = bool(data.get("reduceOnly", False))

    try:
        position_mode = get_position_mode()

        # 🟢 إعداد أمر Market
        if str(price).lower() == "market":
            order_args = {
                "symbol": symbol,
                "side": SIDE_BUY if side == "BUY" else SIDE_SELL,
                "type": FUTURE_ORDER_TYPE_MARKET,
                "quantity": qty,
                "reduceOnly": reduce_only
            }

        # 🟢 إعداد أمر Limit
        else:
            order_args = {
                "symbol": symbol,
                "side": SIDE_BUY if side == "BUY" else SIDE_SELL,
                "type": FUTURE_ORDER_TYPE_LIMIT,
                "timeInForce": TIME_IN_FORCE_GTC,
                "quantity": qty,
                "price": price,
                "reduceOnly": reduce_only
            }

        # 🟢 لو الحساب Hedge Mode نحدد positionSide
        if position_mode == "HEDGE":
            order_args["positionSide"] = "LONG" if side == "BUY" else "SHORT"

        # تنفيذ الأمر
        order = client.futures_create_order(**order_args)

        return jsonify({"status": "success", "order": order}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
