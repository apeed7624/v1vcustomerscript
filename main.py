import os
import subprocess
import utils.api_client
import utils.config
from utils.custom_script import CustomScriptManager
from utils.agentlist import ClientManager
from utils.run_custom_script import RunCustomScriptManager
from utils.collect_file import CollectFileManager
from utils.download_task import TaskDownloader


def main():
    while True:  # 使用迴圈確保執行完畢後回到主選單
        print("\nTrend Micro Vision One Customer Script Tool")
        print("1. 列出 Custom Scripts")
        print("2. 列出所有 Clients（包含 EDR Sensor 狀態）")
        print("3. 執行單一 Custom Script")
        print("4. 更新 Custom Script")
        print("5. 批次執行 Custom Script (從 txt 檔案讀取)")
        print("6. 批次收集檔案 (Collect File)")
        print("7. 下載並解壓縮檔案")
        print("8. **檢查 Task ID 狀態**")
        print("9. 退出程式")


        choice = input("請選擇功能: ").strip()

        if choice == "1":
            manager = CustomScriptManager()
            scripts = manager.list_custom_scripts()
            if scripts:
                print(" 取得 Custom Scripts：")
                for script in scripts:
                    file_name = script.get('fileName', '未命名')
                    script_id = script.get('id', '未知 ID')
                    print(f"- {file_name} (ID: {script_id})")
            else:
                print(" 沒有找到 Custom Scripts")

        elif choice == "2":
            manager = ClientManager()
            agents = manager.list_all_clients()
            if agents:
                print("✅ 取得 Client 資訊：")
                for agent in agents:
                    agent_guid = agent.get("agentGuid", "未知")
                    endpoint_name = agent.get("endpointName", "未知")
                    last_used_ip = agent.get("lastUsedIp", "未知")
                    os_name = agent.get("osName", "未知")
                    edr_sensor_connectivity = agent.get("edrSensor", {}).get("connectivity", "Disconnected")

                    print(f"- {endpoint_name} (Agent GUID: {agent_guid}, Last Used IP: {last_used_ip}, OS: {os_name}, Status: {edr_sensor_connectivity})")

                # 詢問使用者是否要匯出 CSV
                export_choice = input("\n是否要匯出資料到 CSV？(Y/N): ").strip().lower()
                if export_choice == "y":
                    manager.export_to_csv(agents)
                else:
                    print(" 匯出取消，回到主選單。")
            else:
                print(" 沒有找到任何 Client")

        elif choice == "3":
            manager = RunCustomScriptManager()
            agent_guid = input("請輸入要執行腳本的 Agent GUID: ").strip()
            file_name = input("請輸入要執行的 Custom Script 檔案名稱: ").strip()
            parameters = input("請輸入腳本參數（powershell or bash，留空則不填）: ").strip() or None

            response = manager.run_custom_script(agent_guid, file_name, parameters)

            if response:
                print(" 成功執行 Custom Script!")
            else:
                print(" 執行失敗")

        elif choice == "4":
            manager = CustomScriptManager()
            file_path = input("請輸入要上傳的腳本檔案路徑: ").strip()
            file_name = input("請輸入要儲存的腳本檔案名稱: ").strip()
            file_type = input("請輸入腳本類型 (powershell, bash, etc.): ").strip()
            description = input("請輸入腳本描述: ").strip()

            response = manager.update_script(file_path, file_name, file_type, description)

            if response:
                print(" 更新成功！")
            else:
                print("更新失敗")

        elif choice == "5":
            manager = RunCustomScriptManager()
            agent_file = input("請輸入包含 Agent GUIDs 的 txt 檔案路徑: ").strip()
            file_name = input("請輸入要執行的 Custom Script 檔案名稱: ").strip()
            parameters = input("請輸入腳本參數（powershell or bash，留空則不填）: ").strip() or None

            # 讀取 txt 檔案並執行 Custom Script
            manager.run_from_file(agent_file, file_name, parameters)

        elif choice == "6":
            manager = CollectFileManager()
            agent_file = input("請輸入包含 Agent GUIDs 的 txt 檔案路徑: ").strip()
            file_path = input("請輸入要收集的檔案路徑: ").strip()

            # 讀取 txt 檔案並批次執行收集檔案
            manager.collect_from_file(agent_file, file_path)

        elif choice == "7":
            manager = TaskDownloader()
            task_file = input("請輸入包含 Task ID 的 txt 檔案路徑: ").strip()

            # 讀取 txt 檔案並下載並解壓縮
            manager.process_from_file(task_file)

        elif choice == "8":

            task_file = input("請輸入包含 Task ID 的 txt 檔案路徑: ").strip()

            # ✅ 確保 task_file 存在

            if not os.path.isfile(task_file):
                print(f" 檔案 '{task_file}' 不存在，請確認路徑")

                continue

            # ✅ 啟動新視窗，運行 `check_task_status.py`

            script_path = os.path.join(os.getcwd(), "check_task_status.py")

            subprocess.Popen(["python", script_path, task_file], creationflags=subprocess.CREATE_NEW_CONSOLE)

            print(" 新視窗已開啟，正在監控 Task 狀態，請勿關閉該視窗！")

        elif choice == "9":
            print(" 再見！已退出程式。")
            break  # 離開迴圈，結束程式





        else:
            print("無效的選擇，請重新輸入！")

if __name__ == "__main__":
    main()
