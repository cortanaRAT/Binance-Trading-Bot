from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import hmac, hashlib, time, os, json

# إعداد مفاتيح API الخاصة بك من Binance
API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
API_SECRET = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

client = Client(API_KEY, API_SECRET)

# إنشاء سيرفر Flask
app = Flask(__name__)

# استقبال Webhook من TradingView
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("📩 Webhook Received:", data)

        symbol = data.get("symbol", "BTCUSDT")
        side = data.get("side", "").lower()   # buy أو sell
        qty = float(data.get("qty", 0.001))
        tp = float(data.get("tp", 0))  # Take Profit
        sl = float(data.get("sl", 0))  # Stop Loss

        if side not in ["buy", "sell"]:
            return jsonify({"error": "Invalid side"}), 400

        # تنفيذ أمر السوق (Market Order)
        order_side = SIDE_BUY if side == "buy" else SIDE_SELL
        order = client.create_order(
            symbol=symbol,
            side=order_side,
            type=ORDER_TYPE_MARKET,
            quantity=qty
        )

        print("✅ Market Order Executed:", order)

        # إضافة أمر OCO (Take Profit + Stop Loss) إذا تم توفيره
        if tp > 0 and sl > 0:
            if side == "buy":
                client.create_oco_order(
                    symbol=symbol,
                    side=SIDE_SELL,
                    quantity=qty,
                    price=str(tp),
                    stopPrice=str(sl),
                    stopLimitPrice=str(sl * 0.999),  # قليل أقل للـ Limit
                    stopLimitTimeInForce=TIME_IN_FORCE_GTC
                )
            else:  # في حالة البيع أولاً
                client.create_oco_order(
                    symbol=symbol,
                    side=SIDE_BUY,
                    quantity=qty,
                    price=str(tp),
                    stopPrice=str(sl),
                    stopLimitPrice=str(sl * 1.001),
                    stopLimitTimeInForce=TIME_IN_FORCE_GTC
                )

            print("📌 OCO Order (TP + SL) Added")

        return jsonify({"status": "success", "order": order}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
