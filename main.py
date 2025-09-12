from flask import Flask, request, jsonify
import json, time, os

app = Flask(__name__)

# ملف نخزن به الصفقات
trades_file = "paper_trades.json"

# تحميل الصفقات القديمة لو موجودة
if os.path.exists(trades_file):
    with open(trades_file, "r") as f:
        trades = json.load(f)
else:
    trades = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # قراءة البيانات من تنبيه TradingView
    symbol = data.get("symbol")
    side = data.get("side")
    qty = float(data.get("qty"))
    tp = float(data.get("tp"))
    sl = float(data.get("sl"))
    entry = data.get("entry")  # اذا ماكو entry راح نعتبرها None

    trade = {
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "tp": tp,
        "sl": sl,
        "entry": entry,
        "status": "OPEN",
        "time_open": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    trades.append(trade)

    # تحديث الملف
    with open(trades_file, "w") as f:
        json.dump(trades, f, indent=2)

    return jsonify({"status": "trade logged", "trade": trade})


# API لمتابعة كل الصفقات
@app.route('/trades', methods=['GET'])
def get_trades():
    return jsonify(trades)


if __name__ == '__main__':
    app.run(port=5000)
