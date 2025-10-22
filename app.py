# app.py 修正內容
from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

# ===========================================
# 🚨 請使用您的 App ID 和 Secret Key
APP_ID = '16345040007'
SECRET_KEY = 'STB252ZA5HVC4MJJ5ZSYZBXY423WIYHU'
# ===========================================

# 🚨 路由從 POST 改為 GET
@app.route('/generate-shopee-auth', methods=['GET'])
def generate_auth():
    # 🚨 從 URL 查詢參數中讀取數據
    timestamp = request.args.get('timestamp')
    payload_string = request.args.get('payloadString') # payloadString 是 URL 編碼後的字串
    
    if not timestamp or not payload_string:
        return jsonify({"error": "Missing timestamp or payloadString in query parameters"}), 400

    # 數據接收成功，後續邏輯不變
    signature_factor = APP_ID + timestamp + payload_string + SECRET_KEY

    try:
        signature = hashlib.sha256(signature_factor.encode('utf-8')).hexdigest()
    except Exception as e:
        return jsonify({"error": f"SHA256 calculation failed: {str(e)}"}), 500
    
    auth_value = f"SHA256Credential={APP_ID},Timestamp={timestamp},Signature={signature}"


    # 由於我們只關注 Header，將其和 payloadString 一起返回
    return jsonify({
        "shopeeAuthHeader": auth_value,
        "shopeePayload": payload_string,
        "timestamp": timestamp
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
