# Shopee API 認證簽名生成文檔

## ⚠️ 重要修正說明

**本文件記錄了 Shopee API 的實際正確使用方法，與官方文檔存在差異：**

| 項目 | 官方文檔（錯誤） | 實際使用（正確） |
|------|----------------|----------------|
| HTTP 方法 | POST | **GET** ✅ |
| 參數傳遞方式 | 請求體（Request Body） | **URL 查詢參數（Query Parameters）** ✅ |
| 參數名稱 | 可能不同 | `timestamp`, `payloadString` ✅ |

---

## API 端點

### 生成 Shopee 認證簽名

**端點：** `/generate-shopee-auth`  
**HTTP 方法：** `GET` ⚠️ **必須使用 GET，不是 POST**  
**Content-Type：** 不需要（因為使用 GET 和查詢參數）

---

## 請求參數

### 查詢參數（Query Parameters）

所有參數必須通過 URL 查詢參數傳遞，**不要放在請求體中**。

| 參數名稱 | 類型 | 必填 | 說明 | 範例 |
|---------|------|------|------|------|
| `timestamp` | string | ✅ 是 | Unix 時間戳（秒），不是毫秒 | `1699123456` |
| `payloadString` | string | ✅ 是 | URL 編碼後的請求內容字串 | `%7B%22key%22%3A%22value%22%7D` |

### 參數說明

1. **timestamp**
   - 格式：Unix 時間戳（秒）
   - 獲取方式：`Math.floor(Date.now() / 1000)` (JavaScript) 或 `int(time.time())` (Python)
   - 必須是當前時間或接近當前時間

2. **payloadString**
   - 必須是 **URL 編碼（URL Encoding）** 後的字串
   - 原始內容通常是 JSON 字串
   - 編碼範例：
     - 原始：`{"key":"value"}`
     - 編碼後：`%7B%22key%22%3A%22value%22%7D`

---

## 請求範例

### 1. cURL

```bash
# 正確方式 ✅
curl -X GET \
  "https://your-app.zeabur.app/generate-shopee-auth?timestamp=1699123456&payloadString=%7B%22params%22%3A%22value%22%7D"

# 錯誤方式 ❌（不要這樣做）
curl -X POST \
  "https://your-app.zeabur.app/generate-shopee-auth" \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "1699123456", "payloadString": "..."}'
```

### 2. JavaScript (fetch)

```javascript
// ✅ 正確方式
const timestamp = Math.floor(Date.now() / 1000);
const payload = { params: "value" };
const payloadString = encodeURIComponent(JSON.stringify(payload));

const url = `https://your-app.zeabur.app/generate-shopee-auth?timestamp=${timestamp}&payloadString=${payloadString}`;

fetch(url)
  .then(response => response.json())
  .then(data => {
    console.log('Authorization Header:', data.shopeeAuthHeader);
    // 使用此標頭在後續的 Shopee API 請求中
  })
  .catch(error => {
    console.error('Error:', error);
  });
```

### 3. Python (requests)

```python
import requests
import time
import json
from urllib.parse import quote

# ✅ 正確方式
timestamp = str(int(time.time()))
payload = {"params": "value"}
payload_string = quote(json.dumps(payload))

url = "https://your-app.zeabur.app/generate-shopee-auth"
params = {
    "timestamp": timestamp,
    "payloadString": payload_string
}

response = requests.get(url, params=params)
data = response.json()

print("Authorization Header:", data["shopeeAuthHeader"])
print("Payload:", data["shopeePayload"])
print("Timestamp:", data["timestamp"])
```

### 4. Node.js (axios)

```javascript
const axios = require('axios');
const querystring = require('querystring');

// ✅ 正確方式
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
  const authHeader = response.data.shopeeAuthHeader;
  console.log('Authorization Header:', authHeader);
  
  // 在後續請求中使用此標頭
  return axios.post('https://partner.shopeemobile.com/api/v2/...', {
    // 你的請求數據
  }, {
    headers: {
      'Authorization': authHeader,
      'Content-Type': 'application/json'
    }
  });
})
.catch(error => {
  console.error('Error:', error.response?.data || error.message);
});
```

### 5. Python (完整範例)

```python
import requests
import time
import json
from urllib.parse import quote

# 配置
APP_ID = 'your-app-id'
SECRET_KEY = 'your-secret-key'
SIGNER_URL = 'https://your-app.zeabur.app/generate-shopee-auth'
SHOPEE_API_URL = 'https://partner.shopeemobile.com/api/v2/...'

# 步驟 1: 準備參數
timestamp = str(int(time.time()))
payload = {
    "partner_id": APP_ID,
    "shop_id": "your-shop-id",
    # 其他參數...
}
payload_string = quote(json.dumps(payload))

# 步驟 2: 獲取認證標頭
response = requests.get(SIGNER_URL, params={
    "timestamp": timestamp,
    "payloadString": payload_string
})

if response.status_code == 200:
    data = response.json()
    auth_header = data["shopeeAuthHeader"]
    
    # 步驟 3: 使用認證標頭調用 Shopee API
    shopee_response = requests.post(
        SHOPEE_API_URL,
        json=payload,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
    )
    
    print("Shopee API Response:", shopee_response.json())
else:
    print("Error:", response.json())
```

---

## 響應格式

### 成功響應 (200 OK)

```json
{
  "shopeeAuthHeader": "SHA256 Credential=16345040007,Timestamp=1699123456,Signature=abc123def456...",
  "shopeePayload": "%7B%22params%22%3A%22value%22%7D",
  "timestamp": "1699123456"
}
```

#### 響應欄位說明

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `shopeeAuthHeader` | string | 完整的認證標頭值，可直接用於 Shopee API 請求的 `Authorization` 標頭 |
| `shopeePayload` | string | URL 編碼後的 payload 字串（與請求中的 payloadString 相同） |
| `timestamp` | string | 使用的時間戳（與請求中的 timestamp 相同） |

### 錯誤響應

#### 缺少參數 (400 Bad Request)

```json
{
  "error": "Missing timestamp or payloadString in query parameters"
}
```

**原因：** 請求中缺少 `timestamp` 或 `payloadString` 參數。

**解決方法：** 確保兩個參數都通過 URL 查詢參數傳遞。

#### 簽名計算失敗 (500 Internal Server Error)

```json
{
  "error": "SHA256 calculation failed: [錯誤詳情]"
}
```

**原因：** 在計算 SHA256 簽名時發生錯誤（通常是編碼問題）。

**解決方法：** 確保 `payloadString` 正確進行了 URL 編碼。

---

## 簽名生成邏輯

### 簽名計算公式

```
signature_factor = APP_ID + timestamp + payloadString + SECRET_KEY
signature = SHA256(signature_factor)
```

### 認證標頭格式

```
Authorization: SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={signature}
```

### 詳細步驟

1. **準備簽名字串**
   ```
   signature_factor = APP_ID + timestamp + payloadString + SECRET_KEY
   ```
   例如：
   ```
   signature_factor = "16345040007" + "1699123456" + "%7B%22key%22%3A%22value%22%7D" + "STB252ZA5HVC4MJJ5ZSYZBXY423WIYHU"
   ```

2. **計算 SHA256 雜湊**
   ```python
   import hashlib
   signature = hashlib.sha256(signature_factor.encode('utf-8')).hexdigest()
   ```

3. **組裝認證標頭**
   ```
   Authorization: SHA256 Credential=16345040007,Timestamp=1699123456,Signature={signature}
   ```

---

## 完整使用流程

### 步驟 1: 準備參數

```javascript
// 獲取當前時間戳（秒）
const timestamp = Math.floor(Date.now() / 1000);

// 準備請求 payload
const payload = {
    partner_id: "your-partner-id",
    shop_id: "your-shop-id",
    // 其他 Shopee API 需要的參數...
};

// URL 編碼 payload
const payloadString = encodeURIComponent(JSON.stringify(payload));
```

### 步驟 2: 獲取認證標頭

```javascript
const signerUrl = `https://your-app.zeabur.app/generate-shopee-auth?timestamp=${timestamp}&payloadString=${payloadString}`;

const response = await fetch(signerUrl);
const data = await response.json();

const authHeader = data.shopeeAuthHeader;
```

### 步驟 3: 調用 Shopee API

```javascript
const shopeeApiUrl = "https://partner.shopeemobile.com/api/v2/product/get_item_list";

const shopeeResponse = await fetch(shopeeApiUrl, {
    method: "POST",
    headers: {
        "Authorization": authHeader,
        "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
});

const result = await shopeeResponse.json();
console.log("Shopee API Result:", result);
```

---

## 常見錯誤與解決方法

### 錯誤 1: 使用 POST 方法

**錯誤訊息：** `405 Method Not Allowed` 或類似錯誤

**原因：** 使用了 POST 方法而不是 GET

**解決方法：** 
```javascript
// ❌ 錯誤
fetch(url, { method: 'POST', body: JSON.stringify(params) })

// ✅ 正確
fetch(`${url}?timestamp=${timestamp}&payloadString=${payloadString}`)
```

### 錯誤 2: 參數放在請求體中

**錯誤訊息：** `Missing timestamp or payloadString in query parameters`

**原因：** 將參數放在請求體（body）中而不是查詢參數

**解決方法：**
```javascript
// ❌ 錯誤
fetch(url, {
    method: 'GET',
    body: JSON.stringify({ timestamp, payloadString })
})

// ✅ 正確
fetch(`${url}?timestamp=${timestamp}&payloadString=${payloadString}`)
```

### 錯誤 3: payloadString 未進行 URL 編碼

**錯誤訊息：** `SHA256 calculation failed` 或簽名驗證失敗

**原因：** payloadString 沒有正確進行 URL 編碼

**解決方法：**
```javascript
// ❌ 錯誤
const payloadString = JSON.stringify(payload);

// ✅ 正確
const payloadString = encodeURIComponent(JSON.stringify(payload));
```

### 錯誤 4: timestamp 使用毫秒

**錯誤訊息：** 簽名驗證失敗

**原因：** timestamp 使用了毫秒而不是秒

**解決方法：**
```javascript
// ❌ 錯誤
const timestamp = Date.now(); // 毫秒

// ✅ 正確
const timestamp = Math.floor(Date.now() / 1000); // 秒
```

### 錯誤 5: 參數名稱錯誤

**錯誤訊息：** `Missing timestamp or payloadString in query parameters`

**原因：** 使用了錯誤的參數名稱（例如 `payload` 而不是 `payloadString`）

**解決方法：** 確保參數名稱完全正確：
- ✅ `timestamp`
- ✅ `payloadString`
- ❌ `payload`
- ❌ `time`
- ❌ `data`

---

## 測試範例

### 測試請求

```bash
# 使用實際的時間戳和 payload
TIMESTAMP=$(date +%s)
PAYLOAD='{"partner_id":"16345040007","shop_id":"12345"}'
PAYLOAD_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PAYLOAD'))")

curl -X GET \
  "https://your-app.zeabur.app/generate-shopee-auth?timestamp=$TIMESTAMP&payloadString=$PAYLOAD_ENCODED"
```

### 預期響應

```json
{
  "shopeeAuthHeader": "SHA256 Credential=16345040007,Timestamp=1699123456,Signature=...",
  "shopeePayload": "%7B%22partner_id%22%3A%2216345040007%22%2C%22shop_id%22%3A%2212345%22%7D",
  "timestamp": "1699123456"
}
```

---

## 重要提醒

1. ⚠️ **必須使用 GET 方法**，不要使用 POST
2. ⚠️ **參數必須通過 URL 查詢參數傳遞**，不要放在請求體中
3. ⚠️ **payloadString 必須是 URL 編碼後的字串**
4. ⚠️ **timestamp 必須是 Unix 時間戳（秒）**，不是毫秒
5. ⚠️ **參數名稱必須完全正確**：`timestamp` 和 `payloadString`（注意大小寫）
6. ⚠️ **認證標頭格式固定**：`SHA256 Credential={APP_ID},Timestamp={timestamp},Signature={signature}`
7. ⚠️ **簽名計算順序固定**：`APP_ID + timestamp + payloadString + SECRET_KEY`

---

## 與官方文檔的差異總結

| 項目 | 官方文檔 | 實際正確方式 | 備註 |
|------|---------|------------|------|
| HTTP 方法 | POST | **GET** | 必須使用 GET |
| 參數位置 | Request Body | **Query Parameters** | 必須在 URL 中 |
| Content-Type | application/json | **不需要** | GET 請求不需要 |
| timestamp 格式 | 可能未明確 | **Unix 時間戳（秒）** | 必須是秒，不是毫秒 |
| payloadString 編碼 | 可能未明確 | **URL 編碼** | 必須進行 URL 編碼 |

---

## 參考資源

- Shopee Partner API 官方文檔（注意：本文檔已修正其中的錯誤）
- SHA256 雜湊算法說明
- URL 編碼標準（RFC 3986）

---

**最後更新：** 根據實際使用經驗修正  
**版本：** 1.0（修正版）
