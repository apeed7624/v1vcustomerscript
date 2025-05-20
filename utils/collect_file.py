import csv
import os
import json
import datetime
from utils.api_client import APIClient

class CollectFileManager:
    def __init__(self):
        self.api_client = APIClient()
        self.url_path = "/v3.0/response/endpoints/collectFile"
        self.task_output_dir = "collectFile_exported_results"  # 儲存 Task ID 的資料夾
        os.makedirs(self.task_output_dir, exist_ok=True)

    def collect_file(self, agent_guid, file_path, description="Collect file task"):
        """
        發送請求收集檔案
        :param agent_guid: 目標 Agent GUID
        :param file_path: 需要收集的檔案路徑
        :param description: 任務描述（預設為 "Collect file task"）
        """
        payload = [{
            "description": description,
            "agentGuid": agent_guid,
            "filePath": file_path
        }]

        result = self.api_client.send_request("POST", self.url_path, data=payload)

        if result is None:
            print(f"❌ 無法收集檔案（Agent: {agent_guid}），請檢查 API 權限")
            return {"agent_guid": agent_guid, "file_path": file_path, "status": "Failed", "task_id": "N/A"}

        # ✅ 處理 207 Multi-Status 回應
        if isinstance(result, list) and len(result) > 0 and "status" in result[0]:
            status_code = result[0]["status"]

            # 如果是 202 Accepted，取得 Task ID
            if status_code == 202:
                task_id = None
                for header in result[0].get("headers", []):
                    if header["name"] == "Operation-Location":
                        task_id = header["value"].split("/")[-1]  # 從 URL 取出 Task ID
                        break

                if task_id:
                    print(f"✅ 檔案收集成功（Agent: {agent_guid}），Task ID: {task_id}")
                    return {
                        "agent_guid": agent_guid,
                        "file_path": file_path,
                        "task_id": task_id,
                        "status": "Success"
                    }
                else:
                    print(f"⚠️ 任務已接受（Agent: {agent_guid}），但未提供 Task ID，請手動檢查 API")
                    return {
                        "agent_guid": agent_guid,
                        "file_path": file_path,
                        "task_id": "N/A",
                        "status": "Accepted"
                    }

        print(f"❌ API 回應格式異常（Agent: {agent_guid}），請檢查 API 設定")
        return {"agent_guid": agent_guid, "file_path": file_path, "task_id": "N/A", "status": "Failed"}

    def collect_from_file(self, agent_file, file_path):
        """
        讀取 Agent GUID 清單，批次執行檔案收集
        :param agent_file: 包含 Agent GUIDs 的 txt 檔案路徑
        :param file_path: 需要收集的檔案路徑
        """
        if not os.path.isfile(agent_file):
            print(f"❌ 錯誤: 檔案 '{agent_file}' 不存在，請確認路徑")
            return

        with open(agent_file, "r", encoding="utf-8") as f:
            agent_guids = [line.strip() for line in f if line.strip()]

        if not agent_guids:
            print("❌ 檔案內沒有有效的 Agent GUID")
            return

        results = []
        for agent_guid in agent_guids:
            response = self.collect_file(agent_guid, file_path)
            if response:
                results.append(response)

        # 匯出結果到 CSV
        self.export_results(results)

        # 匯出 Task ID 到 txt
        self.export_task_ids(results)

    def export_results(self, results):
        """將執行結果匯出至 CSV"""
        if not results:
            print("❌ 沒有可匯出的結果")
            return

        # 產生 CSV 檔名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"collect_file_results_{timestamp}.csv"
        file_path = os.path.join(self.task_output_dir, filename)

        # 寫入 CSV
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Agent GUID", "File Path", "Task ID", "Status"])
            for result in results:
                writer.writerow([
                    result["agent_guid"],
                    result["file_path"],
                    result["task_id"],
                    result["status"]
                ])

        print(f"✅ 檔案收集結果已成功匯出至 {file_path}")

    def export_task_ids(self, results):
        """將 Task ID 匯出到 txt 檔案"""
        task_ids = [result["task_id"] for result in results if result["task_id"] != "N/A"]

        if not task_ids:
            print("❌ 沒有可匯出的 Task ID")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"task_ids_{timestamp}.txt"
        file_path = os.path.join(self.task_output_dir, filename)

        with open(file_path, mode="w", encoding="utf-8") as file:
            file.write("\n".join(task_ids))

        print(f"✅ Task ID 已成功匯出至 {file_path}")

if __name__ == "__main__":
    manager = CollectFileManager()

    agent_file = input("請輸入包含 Agent GUIDs 的 txt 檔案路徑: ").strip()
    file_path = input("請輸入要收集的檔案路徑: ").strip()

    # 迴圈執行所有 GUID，並匯出結果
    manager.collect_from_file(agent_file, file_path)
