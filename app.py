from flask import Flask, request, jsonify
import hashlib
import time

app = Flask(__name__)

APP_ID = '16345040007'
SECRET_KEY = 'STB252ZA5HVC4MJJ5ZSYZBXY423WIYHU'

@app.route('/generate-shopee-auth', methods=['POST'])
def generate_auth():
    data = request.get_json()
    timestamp = data.get('timestamp')
    payload_string = data.get('payloadString')

    if not timestamp or not payload_string:
        return jsonify({"error": "Missing timestamp or payloadString in request"}), 400

    signature_factor = APP_ID + timestamp + payload_string + SECRET_KEY

    try:
        signature = hashlib.sha256(signature_factor.encode('utf-8')).hexdigest()
    except Exception as e:
        return jsonify({"error": f"SHA256 calculation failed: {str(e)}"}), 500

    auth_value = f"SHA256 Credential={APP_ID}, Timestamp={timestamp}, Signature={signature}"

    return jsonify({
        "shopeeAuthHeader": auth_value,
        "shopeePayload": payload_string,
        "timestamp": timestamp
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000) 
