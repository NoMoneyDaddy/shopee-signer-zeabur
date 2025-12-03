# Shopee API 簽名生成服務

這是一個用於生成 Shopee API 認證簽名的 Flask 服務，用於 Zeabur 部署。

## ⚠️ 重要修正說明

**實際使用方式與官方文檔不同：**
- ✅ **正確方式**：使用 `GET` 方法，參數通過 URL 查詢參數傳遞
- ❌ **錯誤方式**：使用 `POST` 方法，參數通過請求體傳遞

## API 端點

### 生成 Shopee 認證簽名

**端點：** `/generate-shopee-auth`  
**方法：** `GET` (⚠️ 注意：不是 POST)  
**認證：** 無需認證

### 請求參數

所有參數必須通過 URL 查詢參數（Query Parameters）傳遞：

| 參數名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `timestamp` | string | 是 | Unix 時間戳（秒） |
| `payloadString` | string | 是 | URL 編碼後的請求內容字串 |

### 請求範例

#### cURL

```bash
curl -X GET \
  "https://your-app.zeabur.app/generate-shopee-auth?timestamp=1699123456&payloadString=eyJwYXJhbXMiOiJ2YWx1ZSJ9"
```

#### JavaScript (fetch)

```javascript
const timestamp = Math.floor(Date.now() / 1000);
const payloadString = encodeURIComponent(JSON.stringify({ params: "value" }));

const url = `https://your-app.zeabur.app/generate-shopee-auth?timestamp=${timestamp}&payloadString=${payloadString}`;

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log('Authorization Header:', data.shopeeAuthHeader);
    console.log('Payload:', data.shopeePayload);
  });
```

#### Python (requests)

```python
import requests
import time
import json
from urllib.parse import quote

timestamp = str(int(time.time()))
payload = {"params": "value"}
payload_string = quote(json.dumps(payload))

url = f"https://your-app.zeabur.app/generate-shopee-auth"
params = {
    "timestamp": timestamp,
    "payloadString": payload_string
}

response = requests.get(url, params=params)
data = response.json()

print("Authorization Header:", data["shopeeAuthHeader"])
print("Payload:", data["shopeePayload"])
```

#### Node.js (axios)

```javascript
const axios = require('axios');
const querystring = require('querystring');

const timestamp = Math.floor(Date.now() / 1000);
const payload = { params: "value" };
const payloadString = querystring.escape(JSON.stringify(payload));

axios.get('https://your-app.zeabur.app/generate-shopee-auth', {
  params: {
    timestamp: timestamp,
    payloadString: payloadString
  }
})
.then(response => {
  console.log('Authorization Header:', response.data.shopeeAuthHeader);
  console.log('Payload:', response.data.shopeePayload);
});
```

### 響應格式

#### 成功響應 (200 OK)

```json
{
  "shopeeAuthHeader": "SHA256 Credential=16345040007,Timestamp=1699123456,Signature=abc123...",
  "shopeePayload": "eyJwYXJhbXMiOiJ2YWx1ZSJ9",
  "timestamp": "1699123456"
}
```

#### 錯誤響應

**缺少參數 (400 Bad Request)**
```json
{
  "error": "Missing timestamp or payloadString in query parameters"
}
```

**簽名計算失敗 (500 Internal Server Error)**
```json
{
  "error": "SHA256 calculation failed: [錯誤詳情]"
}
```

## 簽名生成邏輯

簽名計算公式：

```
signature_factor = APP_ID + timestamp + payloadString + SECRET_KEY
signature = SHA256(signature_factor)
```

最終的認證標頭格式：

```
Authorization: SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={signature}
```

## 使用流程

1. **準備參數**
   - 獲取當前 Unix 時間戳（秒）
   - 準備請求的 payload（通常是 JSON 字串）
   - 對 payload 進行 URL 編碼

2. **發送請求**
   - 使用 `GET` 方法
   - 將 `timestamp` 和 `payloadString` 作為查詢參數傳遞

3. **獲取認證標頭**
   - 從響應中提取 `shopeeAuthHeader`
   - 在後續的 Shopee API 請求中使用此標頭

4. **調用 Shopee API**
   ```bash
   curl -X POST https://partner.shopeemobile.com/api/v2/... \
     -H "Authorization: SHA256 Credential=16345040007,Timestamp=1699123456,Signature=abc123..." \
     -H "Content-Type: application/json" \
     -d '{"params": "value"}'
   ```

## 注意事項

1. ⚠️ **必須使用 GET 方法**，不要使用 POST
2. ⚠️ **參數必須通過 URL 查詢參數傳遞**，不要放在請求體中
3. ⚠️ **payloadString 必須是 URL 編碼後的字串**
4. ⚠️ **timestamp 必須是 Unix 時間戳（秒）**，不是毫秒
5. 確保 `APP_ID` 和 `SECRET_KEY` 在 `app.py` 中正確配置

## 部署

本服務使用 Flask 和 Gunicorn，可部署到 Zeabur 或其他支援 Python 的平台。

### 本地測試

```bash
python app.py
```

服務將在 `http://localhost:8000` 啟動。

### 環境變數

建議將敏感資訊（APP_ID、SECRET_KEY）改為環境變數：

```python
import os
APP_ID = os.getenv('SHOPEE_APP_ID', 'your-default-app-id')
SECRET_KEY = os.getenv('SHOPEE_SECRET_KEY', 'your-default-secret-key')
```

## 常見問題

**Q: 為什麼使用 GET 而不是 POST？**  
A: 這是實際使用中發現的正確方式。官方文檔可能有誤，實際 API 需要通過 GET 方法和查詢參數傳遞。

**Q: payloadString 需要如何編碼？**  
A: 必須進行 URL 編碼（URL encoding）。例如，`{"key":"value"}` 應該編碼為 `%7B%22key%22%3A%22value%22%7D`。

**Q: timestamp 格式是什麼？**  
A: Unix 時間戳，單位為秒（不是毫秒）。例如：`1699123456`。
