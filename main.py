from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import json

# ========== Binance API ==========
BINANCE_API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
BINANCE_API_SECRET = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# ========== Flask ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 Webhook Server is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = json.loads(request.data)
        print("📩 Received Signal:", data)

        symbol = data['symbol']       # مثال: "BTCUSDT"
        side = data['side'].upper()   # "BUY" or "SELL"
        quantity = float(data['quantity'])
        entry_type = data.get('entry_type', "MARKET").upper()
        tp = float(data.get('take_profit', 0))
        sl = float(data.get('stop_loss', 0))

        # 1. فتح الصفقة الرئيسية
        order = client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=ORDER_TYPE_MARKET if entry_type == "MARKET" else ORDER_TYPE_LIMIT,
            quantity=quantity
        )

        print("✅ Main Order Executed:", order)

        # 2. إضافة Take Profit و Stop Loss
        if tp > 0 or sl > 0:
            opposite_side = SIDE_SELL if side == "BUY" else SIDE_BUY

            oco_order = client.create_oco_order(
                symbol=symbol,
                side=opposite_side,
                quantity=quantity,
                price=str(tp),                # Take Profit
                stopPrice=str(sl),            # Stop Loss
                stopLimitPrice=str(sl),       # نفس سعر الستوب
                stopLimitTimeInForce=TIME_IN_FORCE_GTC
            )

            print("🎯 OCO Order Created (TP/SL):", oco_order)
            return jsonify({"status": "success", "main_order": order, "oco_order": oco_order})

        return jsonify({"status": "success", "main_order": order})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
