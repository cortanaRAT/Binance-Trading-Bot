from flask import Flask, request, jsonify
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging
import os

# تهيئة Flask app
app = Flask(__name__)

# تهيئة logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# مفاتيح API لـ Binance Futures Testnet
API_KEY = "f9cdfdd0f2b13fb8bb89ef5b9edf93281b2fef3aa3e8ff16d48817b4f59c3543"
API_SECRET ="f7b69a165a2ba1ea72727cf96c908863eafa1bff3673dd6752cc193e20734f70"

# إعدادات التداول
QUANTITY = 0.02  # حجم الصفقة
TAKE_PROFIT_POINTS = 20000  # نقاط Take Profit
STOP_LOSS_POINTS = 10000  # نقاط Stop Loss

# تهيئة عميل Binance
client = Client(API_KEY, API_SECRET, testnet=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    معالجة Webhook من TradingView لفتح صفقات على Binance Futures Testnet
    """
    try:
        # التحقق من وجود بيانات JSON في الطلب
        if not request.is_json:
            return jsonify({"error": "Missing JSON in request"}), 400
        
        data = request.get_json()
        
        # التحقق من وجود الحقول المطلوبة
        if 'symbol' not in data or 'side' not in data:
            return jsonify({"error": "Missing required fields: symbol or side"}), 400
        
        symbol = data['symbol'].upper()  # تأكد من أن الرمز بحروف كبيرة
        side = data['side'].upper()      # تأكد من أن الجانب بحروف كبيرة
        
        # التحقق من أن الجانب صالح (BUY أو SELL)
        if side not in ['BUY', 'SELL']:
            return jsonify({"error": "Invalid side. Must be 'BUY' or 'SELL'"}), 400
        
        # الحصول على سعر السوق الحالي
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        
        # تحديد نوع الأمر بناءً على الجانب
        side_effect = 'OPEN'  # هذا يخبر Binance أننا نفتح صفقة جديدة
        
        # فتح الصفقة الرئيسية (MARKET Order)
        if side == 'BUY':
            order = client.futures_create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=QUANTITY,
                sideEffectType=side_effect
            )
        else:  # SELL
            order = client.futures_create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=QUANTITY,
                sideEffectType=side_effect
            )
        
        logger.info(f"تم فتح الصفقة الرئيسية: {order}")
        
        # حساب أسعار Take Profit و Stop Loss
        if side == 'BUY':
            take_profit_price = round(current_price + TAKE_PROFIT_POINTS, 2)
            stop_loss_price = round(current_price - STOP_LOSS_POINTS, 2)
        else:  # SELL
            take_profit_price = round(current_price - TAKE_PROFIT_POINTS, 2)
            stop_loss_price = round(current_price + STOP_LOSS_POINTS, 2)
        
        # وضع أمر Take Profit (LIMIT Order)
        tp_order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL if side == 'BUY' else Client.SIDE_BUY,
            type=Client.ORDER_TYPE_LIMIT,
            timeInForce=Client.TIME_IN_FORCE_GTC,
            quantity=QUANTITY,
            price=take_profit_price,
            reduceOnly=True
        )
        
        logger.info(f"تم وضع أمر Take Profit: {tp_order}")
        
        # وضع أمر Stop Loss (STOP_MARKET Order)
        sl_order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL if side == 'BUY' else Client.SIDE_BUY,
            type=Client.ORDER_TYPE_STOP_MARKET,
            quantity=QUANTITY,
            stopPrice=stop_loss_price,
            reduceOnly=True
        )
        
        logger.info(f"تم وضع أمر Stop Loss: {sl_order}")
        
        # إرجاع رد ناجح
        return jsonify({
            "status": "success",
            "message": "تم فتح الصفقة ووضع أوامر TP/SL بنجاح",
            "main_order": order,
            "tp_order": tp_order,
            "sl_order": sl_order
        }), 200
        
    except BinanceAPIException as e:
        logger.error(f"خطأ في Binance API: {e}")
        return jsonify({"error": f"Binance API Error: {e}"}), 500
        
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        return jsonify({"error": f"Unexpected error: {e}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    نقطة نهاية للتحقق من صحة الخادم
    """
    try:
        # التحقق من اتصال API
        client.futures_ping()
        return jsonify({"status": "healthy", "message": "الخادم يعمل بشكل طبيعي"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # تشغيل التطبيق (في production استخدم خادمًا مثل Gunicorn)
    app.run(host='0.0.0.0', port=5000, debug=False)
