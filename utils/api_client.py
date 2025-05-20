import requests
from utils.config import API_KEY, BASE_URL

class APIClient:
    def __init__(self):
        """初始化 API 連線"""
        self.base_url = BASE_URL
        self.headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

    def send_request(self, method, endpoint, params=None, data=None, files=None):
        """
        統一發送 API 請求
        :param method: "GET", "POST", "PUT", "DELETE"
        :param endpoint: API 端點 (例如 "/v3.0/response/customScripts")
        :param params: 查詢參數 (GET 用, 例如 {'filter': 'YOUR_FILTER'})
        :param data: `POST/PUT` 傳送的 JSON 資料
        :param files: `POST/PUT` 需要上傳的檔案 (multipart/form-data)
        :return: JSON 回應，若 API 無回應則回傳 None
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if files:
                response = requests.request(method, url, headers=self.headers, params=params, data=data, files=files)
            else:
                self.headers["Content-Type"] = "application/json"
                response = requests.request(method, url, headers=self.headers, params=params, json=data)

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
