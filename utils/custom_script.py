import os
from utils.api_client import APIClient

class CustomScriptManager:
    def __init__(self):
        self.api_client = APIClient()

    def list_custom_scripts(self):
        """列出所有 Custom Scripts"""
        endpoint = "/v3.0/response/customScripts"
        result = self.api_client.send_request("GET", endpoint)

        if result is None:
            print("❌ API 回應為 None，請檢查 API Key 或權限")
            return []

        return result.get("items", [])

    def update_script(self, file_path, file_name, file_type, description):
        """
        更新 Custom Script
        :param file_path: 本地端的檔案路徑
        :param file_name: 上傳後的腳本檔名
        :param file_type: 腳本類型 (例如: "powershell", "bash")
        :param description: 腳本描述
        """
        # 確保檔案存在
        if not os.path.isfile(file_path):
            print(f"❌ 錯誤: 檔案 '{file_path}' 不存在，請確認路徑")
            return None

        # 確保程式有權限讀取檔案
        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_name, f, "text/plain")
                }
                data = {
                    "fileType": file_type,
                    "description": description
                }
                endpoint = "/v3.0/response/customScripts"
                result = self.api_client.send_request("POST", endpoint, data=data, files=files)

        except PermissionError:
            print(f"❌ 錯誤: 無法讀取檔案 '{file_path}'，請檢查權限")
            return None

        if result is None:
            print("✅ 更新 Custom Script 成功！(204 No Content)")
            return True  # 返回 True 表示成功

        print("✅ 成功更新 Custom Script")
        return result

if __name__ == "__main__":
    manager = CustomScriptManager()

    # 讓使用者輸入參數
    file_path = input("請輸入要上傳的腳本檔案路徑: ").strip()
    file_name = input("請輸入要儲存的腳本檔案名稱: ").strip()
    file_type = input("請輸入腳本類型 (powershell, bash, etc.): ").strip()
    description = input("請輸入腳本描述: ").strip()

    response = manager.update_script(file_path, file_name, file_type, description)

    if response:
        print("✅ 更新成功！")
    else:
        print("❌ 更新失敗")
