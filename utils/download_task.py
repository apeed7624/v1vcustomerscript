import os
import json
import requests
import subprocess  # 使用 7z.exe 來解壓縮
import csv
import datetime
import zipfile  # 用於 zip 解壓縮
import platform
import shutil
from utils.api_client import APIClient


class TaskDownloader:
    def __init__(self):
        self.api_client = APIClient()
        self.url_template = "/v3.0/response/tasks/{task_id}"

        # 檔案儲存路徑
        self.download_dir = "downloaded_files"
        self.extract_base_dir = "extracted_files"
        self.assessment_dir = "assessment_file"  # 存放 assessment.zip 的解壓縮內容
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.extract_base_dir, exist_ok=True)
        os.makedirs(self.assessment_dir, exist_ok=True)

        # 7z 解壓縮工具
        if platform.system() == "Windows":
            self.seven_zip_cmd = [r"C:\Program Files\7-Zip\7z.exe"]
        else:
            self.seven_zip_cmd = ["7z"]

    def get_task_info(self, task_id):
        """
        查詢指定 Task ID 的資訊，取得下載連結與密碼
        """
        endpoint = self.url_template.format(task_id=task_id)
        result = self.api_client.send_request("GET", endpoint)

        if result is None:
            print(f"❌ 無法獲取 Task ID ({task_id}) 的資訊，請檢查 API 權限")
            return None

        if result.get("status") not in ["Completed", "succeeded"]:
            print(f"⚠️ Task ID {task_id} 尚未完成，跳過下載")
            return None

        download_url = result.get("resourceLocation")
        password = result.get("password", "無密碼")
        file_name = result.get("filePath", "未知檔案").split("\\")[-1]

        if not download_url:
            print(f"⚠️ Task ID {task_id} 無可用的下載連結，請手動檢查")
            return None

        return {
            "task_id": task_id,
            "download_url": download_url,
            "password": password,
            "file_name": file_name
        }

    def download_file(self, url, save_path):
        """
        下載檔案並確保完整性
        """
        try:
            response = requests.get(url, stream=True, timeout=60)
            if response.status_code != 200:
                print(f"❌ 無法下載 (狀態碼: {response.status_code})")
                return False

            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)

            if os.path.getsize(save_path) < 500:
                print(f"❌ 下載失敗: {save_path} 檔案過小")
                return False

            print(f"✅ 下載完成: {save_path}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 下載失敗: {e}")
            return False

    def extract_7z(self, archive_path, task_id, password):
        """
        使用 7z.exe 解壓縮 7z 檔案，並放到 Task ID 對應的資料夾
        """
        extract_to = os.path.join(self.extract_base_dir, task_id)
        os.makedirs(extract_to, exist_ok=True)

        try:
            if shutil.which(self.seven_zip_cmd[0]) is None and not os.path.exists(self.seven_zip_cmd[0]):
                print("❌ 找不到 7-Zip 解壓工具，請確認已安裝 7-Zip 或設定 PATH")
                return []

            command = self.seven_zip_cmd + ["x", archive_path, f"-p{password}", f"-o{extract_to}", "-y"]
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode == 0:
                extracted_files = os.listdir(extract_to)
                print(f"✅ 7z 解壓縮成功: {extract_to}")
                return extracted_files
            else:
                print(f"❌ 7z 解壓縮失敗: {result.stderr}")
                return []

        except Exception as e:
            print(f"❌ 7z 解壓縮錯誤: {e}")
            return []

    def extract_assessment_zip(self, task_id):
        """
        將 `assessment.zip` 解壓縮到 `assessment_file/`，並以前三個 `_` 分隔的資訊作為資料夾名稱
        """
        extract_source = os.path.join(self.extract_base_dir, task_id)
        extracted_folders = []

        for file in os.listdir(extract_source):
            if file.lower() == "assessment.zip":
                zip_path = os.path.join(extract_source, file)

                # 取得壓縮檔內的檔案名稱來當作資料夾名稱
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_files = zip_ref.namelist()
                    if not zip_files:
                        print(f"⚠️ assessment.zip 內無檔案，跳過解壓縮: {zip_path}")
                        continue

                    # 取得第一個檔案的名稱，並取前三個 `_` 分隔的資訊作為資料夾名稱
                    extracted_file_name = zip_files[0].split("/")[0]
                    folder_parts = extracted_file_name.split("_")[:3]
                    new_folder_name = "_".join(folder_parts)

                    final_extract_to = os.path.join(self.assessment_dir, new_folder_name)
                    os.makedirs(final_extract_to, exist_ok=True)

                    try:
                        zip_ref.extractall(final_extract_to)
                        extracted_folders.append(new_folder_name)
                        print(f"✅ assessment.zip 解壓縮成功: {file} -> {final_extract_to}")
                    except zipfile.BadZipFile:
                        print(f"❌ assessment.zip 解壓縮失敗: {file}")

        return extracted_folders

    def process_task(self, task_id):
        """
        執行下載與解壓縮流程
        """
        task_info = self.get_task_info(task_id)
        if not task_info:
            return {
                "task_id": task_id,
                "status": "Failed",
                "password": "無密碼",
                "extracted_files": "無"
            }

        # 下載檔案
        filename = f"{task_info['task_id']}.7z"
        zip_path = os.path.join(self.download_dir, filename)

        if not self.download_file(task_info["download_url"], zip_path):
            return {
                "task_id": task_id,
                "status": "Download Failed",
                "password": task_info["password"],
                "extracted_files": "無"
            }

        # 解壓縮 7z 檔案
        extracted_files = self.extract_7z(zip_path, task_info["task_id"], task_info["password"])
        if not extracted_files:
            return {
                "task_id": task_id,
                "status": "Extract Failed",
                "password": task_info["password"],
                "extracted_files": "無"
            }

        # 解壓縮 assessment.zip
        final_extracted_folders = self.extract_assessment_zip(task_info["task_id"])

        return {
            "task_id": task_id,
            "status": "Success",
            "password": task_info["password"],
            "extracted_files": ", ".join(final_extracted_folders) if final_extracted_folders else "無"
        }

    def process_from_file(self, task_file):
        """
        讀取 Task ID 清單，批次執行下載與解壓縮
        """
        if not os.path.isfile(task_file):
            print(f"❌ 錯誤: 檔案 '{task_file}' 不存在，請確認路徑")
            return

        with open(task_file, "r", encoding="utf-8") as f:
            task_ids = [line.strip() for line in f if line.strip()]

        if not task_ids:
            print("❌ 檔案內沒有有效的 Task ID")
            return

        results = []
        for task_id in task_ids:
            result = self.process_task(task_id)
            results.append(result)

        # 匯出結果到 CSV
        self.export_results(results)

    def export_results(self, results):
        """
        將執行結果匯出至 CSV
        """
        if not results:
            print("❌ 無可匯出的結果")
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"download_results_{timestamp}.csv"
        file_path = os.path.join("exported_results", filename)
        os.makedirs("exported_results", exist_ok=True)

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Task ID", "Status", "Password", "Extracted Files"])
            for result in results:
                writer.writerow([
                    result.get("task_id", "未知"),
                    result.get("status", "未知"),
                    result.get("password", "無密碼"),
                    result.get("extracted_files", "無")
                ])

        print(f"✅ 結果已成功匯出至 {file_path}")


if __name__ == "__main__":
    manager = TaskDownloader()
    task_file = input("請輸入 Task ID 清單的 txt 檔案: ").strip()
    manager.process_from_file(task_file)
