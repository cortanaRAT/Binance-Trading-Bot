from binance.client import Client
from flask import Flask, request, jsonify

app = Flask(__name__)

api_key = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
api_secret = "f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"
client = Client(api_key, api_secret, testnet=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    try:
        order = client.futures_create_order(
            symbol=data['symbol'],
            side=data['side'],
            type=data['type'],
            quantity=data['quantity']
        )
        return jsonify(order)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5000)
