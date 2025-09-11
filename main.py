import os
from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

# المفاتيح من متغيرات البيئة (Railway Variables)
API_KEY ="f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
SECRET_KEY = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

# mode = testnet or real
USE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() == "true"

client = Client(API_KEY, SECRET_KEY, testnet=USE_TESTNET)

@app.route("/", methods=["GET"])
def home():
    return "Flask Binance Client — POST JSON to /send_order"

@app.route("/send_order", methods=["POST"])
def send_order():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Expected JSON body"}), 400

    symbol = data.get("symbol")
    side = data.get("side", "BUY")
    position_side = data.get("positionSide", "BOTH")
    qty = data.get("qty", "0.01")
    price = data.get("price", "market")
    reduce_only = data.get("reduceOnly", False)

    try:
        if str(price).lower() == "market":
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_MARKET,
                positionSide=position_side,
                quantity=qty,
                reduceOnly=reduce_only
            )
        else:
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side.upper() == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                positionSide=position_side,
                quantity=qty,
                price=price,
                reduceOnly=reduce_only
            )

        return jsonify(order)

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
