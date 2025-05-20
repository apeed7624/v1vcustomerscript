import os
import time
import sys
from utils.api_client import APIClient


class TaskStatusChecker:
    def __init__(self):
        self.api_client = APIClient()
        self.url_template = "/v3.0/response/tasks/{task_id}"
        self.check_interval = 30  # ✅ 每 30 秒檢查一次 (可調整)

    def get_task_status(self, task_id):
        """查詢 Task ID 狀態"""
        endpoint = self.url_template.format(task_id=task_id)
        result = self.api_client.send_request("GET", endpoint)

        if result is None:
            print(f"❌ 無法獲取 Task ID ({task_id}) 的資訊，請檢查 API 權限")
            return "Unknown"

        return result.get("status", "Unknown")

    def check_all_tasks(self, task_file):
        """讀取 Task ID 清單，持續檢查所有 Task 狀態直到全部完成"""
        if not os.path.isfile(task_file):
            print(f"❌ 錯誤: 檔案 '{task_file}' 不存在，請確認路徑")
            return

        with open(task_file, "r", encoding="utf-8") as f:
            task_ids = [line.strip() for line in f if line.strip()]

        if not task_ids:
            print("❌ 檔案內沒有有效的 Task ID")
            return

        print(f"🔍 共有 {len(task_ids)} 個 Task，開始監控狀態...")

        while True:
            pending_tasks = []
            for task_id in task_ids:
                status = self.get_task_status(task_id)
                print(f"🔄 Task {task_id} 狀態: {status}")

                if status.lower() not in ["completed", "succeeded", "failed"]:
                    pending_tasks.append(task_id)

            if not pending_tasks:
                print("✅ 所有 Task 已完成！")
                break

            print(f"⏳ 仍有 {len(pending_tasks)} 個 Task 未完成，30 秒後重新檢查...")
            time.sleep(self.check_interval)  # ✅ 等待 30 秒再檢查

        # ✅ 在所有 Task 完成後，停留在視窗
        input("\n🎯 所有 Task 已完成！按 Enter 退出...")  # ❌ 這行讓視窗保持開啟


if __name__ == "__main__":
    if len(sys.argv) > 1:
        task_file = sys.argv[1]  # ✅ 從參數讀取 Task ID 檔案
    else:
        task_file = input("請輸入包含 Task ID 的 txt 檔案路徑: ").strip()

    manager = TaskStatusChecker()
    manager.check_all_tasks(task_file)
