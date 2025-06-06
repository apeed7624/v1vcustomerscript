import csv
import os
import datetime
from utils.api_client import APIClient

class RunCustomScriptManager:
    def __init__(self):
        self.api_client = APIClient()
        self.task_id_output_file = "run_script_result/task_ids.txt"  # ✅ Task ID 輸出 TXT

    def run_custom_script(self, agent_guid, file_name, parameters=None, description="Run custom script task"):
        """
        執行自訂腳本
        :param agent_guid: 目標 Agent GUID
        :param file_name: 要執行的腳本檔案名稱
        :param parameters: 腳本執行時的參數（可選）
        :param description: 任務描述（預設為 "Run custom script task"）
        """
        endpoint = "/v3.0/response/endpoints/runScript"
        payload = [{
            "agentGuid": agent_guid,
            "fileName": file_name,
            "parameter": parameters if parameters else "",
            "description": description
        }]

        result = self.api_client.send_request("POST", endpoint, data=payload)
        print("🔥 result 回傳:", result)

        if result is None:
            print(f"❌ 無法執行 Custom Script（Agent: {agent_guid}），請檢查 API 權限")
            return None

        # ✅ 處理 207 Multi-Status 回應
        if isinstance(result, list) and len(result) > 0 and "status" in result[0]:
            status_code = result[0]["status"]
            task_id = None  # 預設 Task ID

            # 如果是 202 Accepted，取得 Task URL
            if status_code == 202:
                task_url = None
                for header in result[0].get("headers", []):
                    if header["name"] == "Operation-Location":
                        task_url = header["value"]
                        task_id = task_url.split("/")[-1]  # ✅ 提取 Task ID
                        break

                if task_url:
                    print(f"✅ Custom Script 執行成功（Agent: {agent_guid}）")
                    print(f"🔍 任務查詢 URL: {task_url}")
                    return {"agent_guid": agent_guid, "task_id": task_id, "task_url": task_url, "status": "Success"}
                else:
                    print(f"⚠️ 任務已接受（Agent: {agent_guid}），但未提供 Task URL，請手動檢查 API")
                    return {"agent_guid": agent_guid, "task_id": "N/A", "task_url": "N/A", "status": "Accepted"}

        print(f"❌ API 回應格式異常（Agent: {agent_guid}），請檢查 API 設定")
        return {"agent_guid": agent_guid, "task_id": "N/A", "task_url": "N/A", "status": "Failed"}

    def run_from_file(self, file_path, file_name, parameters=None):
        """
        從 txt 檔案批次執行 Custom Script，並將結果匯出到 CSV
        :param file_path: 包含 Agent GUIDs 的 txt 檔案路徑
        :param file_name: 要執行的 Custom Script 檔案名稱
        :param parameters: 腳本執行時的參數（可選）
        """
        if not os.path.isfile(file_path):
            print(f"❌ 錯誤: 檔案 '{file_path}' 不存在，請確認路徑")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            agent_guids = [line.strip() for line in f if line.strip()]

        if not agent_guids:
            print("❌ 檔案內沒有有效的 Agent GUID")
            return

        results = []
        task_ids = []  # ✅ Task ID 收集

        for agent_guid in agent_guids:
            response = self.run_custom_script(agent_guid, file_name, parameters)
            if response:
                results.append(response)
                if response["task_id"] != "N/A":  # 只記錄有效 Task ID
                    task_ids.append(response["task_id"])

        # 匯出結果到 CSV & Task ID 到 TXT
        self.export_results(results)
        self.export_task_ids(task_ids)

    def export_results(self, results):
        """將執行結果匯出至 CSV"""
        if not results:
            print("❌ 沒有可匯出的結果")
            return

        # 產生 CSV 檔名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"run_script_result/result_{timestamp}.csv"

        # 確保目錄存在
        output_dir = "run_script_result"
        os.makedirs(output_dir, exist_ok=True)

        # 寫入 CSV
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Agent GUID", "Task ID", "Task URL", "Status"])  # ✅ 新增 Task ID 欄位
            for result in results:
                writer.writerow([result["agent_guid"], result["task_id"], result["task_url"], result["status"]])

        print(f"✅ 執行結果已成功匯出至 {filename}")

    def export_task_ids(self, task_ids):
        """✅ 將 Task ID 存入 `task_ids.txt`"""
        if not task_ids:
            print("❌ 沒有可匯出的 Task ID")
            return

        os.makedirs("run_script_result", exist_ok=True)  # 確保目錄存在

        with open(self.task_id_output_file, "w", encoding="utf-8") as file:
            for task_id in task_ids:
                file.write(f"{task_id}\n")

        print(f"✅ Task IDs 已成功匯出至 {self.task_id_output_file}")

if __name__ == "__main__":
    manager = RunCustomScriptManager()

    # 讀取 Agent GUIDs 的 txt 檔案
    agent_file = input("請輸入包含 Agent GUIDs 的 txt 檔案路徑: ").strip()
    file_name = input("請輸入要執行的 Custom Script 檔案名稱: ").strip()
    parameters = input("請輸入腳本參數（powershell or bash，留空則不填）: ").strip() or None

    # 迴圈執行所有 GUID，並匯出結果
    manager.run_from_file(agent_file, file_name, parameters)
