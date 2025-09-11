import os
from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *

# ⚠️ مفاتيحك (انتبه لا تنشرها للعامة)
API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
SECRET_KEY = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

# testnet=True (للاختبار) أو False (للحقيقي)
USE_TESTNET = True

# عميل Binance
client = Client(API_KEY, SECRET_KEY, testnet=USE_TESTNET)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "🚀 Binance Webhook is running"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    if not data:
        return jsonify({"error": "Empty body"}), 400

    try:
        symbol = data.get("symbol")
        side = data.get("side", "BUY").upper()
        qty = float(data.get("qty", 0.01))
        position_side = data.get("positionSide", "BOTH")
        price = data.get("price", "market")
        reduce_only = data.get("reduceOnly", False)

        if not symbol:
            return jsonify({"error": "symbol is required"}), 400

        if str(price).lower() == "market":
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_MARKET,
                quantity=qty,
                positionSide=position_side,
                reduceOnly=reduce_only
            )
        else:
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                type=FUTURE_ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=qty,
                price=price,
                positionSide=position_side,
                reduceOnly=reduce_only
            )

        return jsonify({"status": "success", "order": order}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
