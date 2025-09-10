from flask import Flask, request, jsonify
from binance.client import Client
import os

app = Flask(__name__)

# استدعاء الـ API Key و Secret من Environment Variables
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Client مع testnet=True
client = Client(API_KEY, API_SECRET, testnet=True)

@app.route("/")
def home():
    return "Binance Webhook is running 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data received"}), 400

    # التأكد من أن البيانات موجودة
    symbol = data.get("symbol")
    side = data.get("side")
    qty = data.get("qty")

    if not all([symbol, side, qty]):
        return jsonify({"error": "Missing symbol, side, or qty"}), 400

    try:
        # إنشاء أوردر ماركت في Testnet
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=float(qty)
        )
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# مهم: تشغيل Flask على 0.0.0.0 و port من البيئة
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
