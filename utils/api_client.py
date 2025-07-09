import requests
from utils.config import API_KEY, BASE_URL

class APIClient:
    def __init__(self):
        """初始化 API 連線"""
        self.base_url = BASE_URL
        self.headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

    def send_request(self, method, endpoint, params=None, data=None, files=None, extra_headers=None):
        """
        統一發送 API 請求
        :param method: "GET", "POST", "PUT", "DELETE"
        :param endpoint: API 端點 (例如 "/v3.0/response/customScripts")
        :param params: 查詢參數 (GET 用, 例如 {'filter': 'YOUR_FILTER'})
        :param data: `POST/PUT` 傳送的 JSON 資料
        :param files: `POST/PUT` 需要上傳的檔案 (multipart/form-data)
        :param extra_headers: 額外的 HTTP 標頭字典
        :return: JSON 回應，若 API 無回應則回傳 None
        """
        url = f"{self.base_url}{endpoint}"

        try:
            import json
            print("📤 發送 API 請求:")
            print(f"🔹 Method: {method}")
            print(f"🔹 URL: {url}")
            headers = self.headers.copy()
            if extra_headers:
                headers.update(extra_headers)
            print(f"🔹 Headers: {headers}")
            print("📤 送出 Request Headers:")
            for k, v in headers.items():
                print(f"🔹 {k}: {v}")
            if params:
                print(f"🔹 Params: {params}")
            if files:
                print("🚀 即將送出的 Request Payload (form-data):")
                print(data)
                response = requests.request(method, url, headers=headers, params=params, data=data, files=files)
            else:
                headers["Content-Type"] = "application/json"
                print("🚀 即將送出的 Request Payload:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                response = requests.request(method, url, headers=headers, params=params, json=data)

            print("📥 回應 Headers:")
            for k, v in response.headers.items():
                print(f"🔸 {k}: {v}")
            if response.status_code in [200, 201, 202]:
                return response.json() if response.text else True  # 若無回應內容，視為成功

            elif response.status_code == 207:  # ✅ 處理 207 Multi-Status
                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError:
                    print("⚠️ 207 Multi-Status 回應無法解析 JSON")
                    return None

            elif response.status_code == 204:  # 204 No Content
                print("✅ API 執行成功 (204 No Content)")
                return None

            else:
                print(f"❌ API 錯誤 ({response.status_code}): {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ API 請求失敗: {e}")
            return None