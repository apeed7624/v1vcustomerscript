import os
from utils.api_client import APIClient

class YaraRuleManager:
    def __init__(self):
        self.api_client = APIClient()

    def list_yara_rules(self, filter_str=None, top=100):
        endpoint = "/v3.0/response/yaraRuleFiles"
        params = {
            "top": top
        }
        if filter_str:
            params["filter"] = filter_str

        response = self.api_client.send_request("GET", endpoint, params=params)
        print("📦 API 回應:", response)

        if not response:
            print("❌ 無法取得 YARA 規則清單，請檢查 API 權限或網路連線")
            return []

        rules = response.get("items", [])
        return [
            {
                "ID": rule.get("id", "N/A"),
                "檔案名稱": rule.get("name", "未知"),
                "描述": rule.get("description", "無描述"),
                "上傳者": rule.get("updatedBy", "未知"),
                "更新時間": rule.get("updatedDateTime", "未知")
            }
            for rule in rules
        ]
