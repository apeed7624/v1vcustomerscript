import streamlit as st
import os
import platform
import subprocess
from utils.custom_script import CustomScriptManager
from utils.agentlist import ClientManager
from utils.run_custom_script import RunCustomScriptManager
from utils.collect_file import CollectFileManager
from utils.download_task import TaskDownloader
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Vision One 工具", layout="wide")
st.title("Trend Micro Vision One 工具")

with st.sidebar:
    option = option_menu(
        menu_title="功能選單",
        options=[
            "列出 Custom Scripts",
            "列出所有 Clients（包含 EDR Sensor 狀態）",
            "執行單一 Custom Script",
            "更新 Custom Script",
            "批次執行 Custom Script",
            "批次收集檔案",
            "下載並解壓縮檔案",
            "檢查 Task ID 狀態",
            "持續監控所有 Task 狀態（Web 介面）",
            "關於本工具"
        ],
        icons=[
            "file-earmark-code", "people", "play", "upload",
            "layers", "cloud-arrow-down", "archive", "search", "list-check", "info-circle"
        ],
        menu_icon="tools",
        default_index=0
    )

if option == "列出 Custom Scripts":
    with st.expander("1. 列出 Custom Scripts", expanded=True):
        if st.button("執行功能"):
            st.subheader("Custom Script 清單")
            manager = CustomScriptManager()
            scripts = manager.list_custom_scripts()
            if scripts:
                for script in scripts:
                    st.write(f"{script.get('fileName', '未命名')} (ID: {script.get('id', '未知 ID')})")
            else:
                st.warning("沒有找到 Custom Scripts")

elif option == "列出所有 Clients（包含 EDR Sensor 狀態）":
    with st.expander("2. 列出所有 Clients（包含 EDR Sensor 狀態）", expanded=True):
        st.subheader("Client 清單")
        manager = ClientManager()
        if "agents_data" not in st.session_state:
            st.session_state.agents_data = []

        if st.button("執行功能"):
            agents = manager.list_all_clients()
            st.session_state.agents_data = agents
            if agents:
                for agent in agents:
                    st.write(f"{agent.get('endpointName', '未知')} (Agent GUID: {agent.get('agentGuid', '')}, IP: {agent.get('lastUsedIp', '')}, OS: {agent.get('osName', '')}, Status: {agent.get('edrSensor', {}).get('connectivity', 'Disconnected')})")
            else:
                st.warning("❌ 沒有找到任何 Client")

        if st.button("匯出 CSV"):
            if st.session_state.agents_data:
                manager.export_to_csv(st.session_state.agents_data)
                st.success("已匯出 CSV（請查看本機路徑）")
            else:
                st.warning("尚未執行查詢或沒有資料可匯出")

elif option == "執行單一 Custom Script":
    with st.expander("3. 執行單一 Custom Script", expanded=True):
        st.subheader("執行 Custom Script")
        agent_guid = st.text_input("Agent GUID")
        file_name = st.text_input("Script 檔名")
        parameters = st.text_input("腳本參數（powershell or bash）", "")
        if st.button("執行"):
            if agent_guid and file_name:
                manager = RunCustomScriptManager()
                result = manager.run_custom_script(agent_guid, file_name, parameters or None)
                if result:
                    st.success(f"執行成功，Task URL: {result.get('task_url')}")
                else:
                    st.error("執行失敗")
                    st.write("🔥 傳入參數:", agent_guid, file_name, parameters)
            else:
                st.warning("請輸入 Agent GUID 和 Script 名稱")

elif option == "更新 Custom Script":
    with st.expander("4. 更新 Custom Script", expanded=True):
        st.subheader("上傳 / 更新 Custom Script")
        file_path = st.text_input("本機腳本檔案路徑")
        file_name = st.text_input("目標檔案名稱")
        file_type = st.selectbox("Script 類型", ["powershell", "bash"])
        description = st.text_area("描述")
        if st.button("上傳 Script"):
            if all([file_path, file_name, file_type]):
                manager = CustomScriptManager()
                res = manager.update_script(file_path, file_name, file_type, description)
                if res:
                    st.success("Script 上傳成功")
                else:
                    st.error("Script 上傳失敗")
            else:
                st.warning("請填寫所有欄位")

elif option == "批次執行 Custom Script":
    with st.expander("5. 批次執行 Custom Script", expanded=True):
        st.subheader("批次執行 Custom Script")
        file = st.file_uploader("上傳包含 Agent GUID 的 txt 檔案", type="txt")
        script_name = st.text_input("Script 檔案名稱")
        params = st.text_input("腳本參數（powershell or bash）", "")
        if st.button("執行批次"):
            if file and script_name:
                path = f"/tmp/agents.txt"
                with open(path, "wb") as f:
                    f.write(file.read())
                manager = RunCustomScriptManager()
                results, csv_path, taskid_path = manager.run_from_file(path, script_name, params or None)
                for res in results:
                    st.success(f"Custom Script 執行成功（Agent: {res.get('agent_guid')}）")
                    st.write(f"任務查詢 URL: {res.get('task_url')}")

                if csv_path:
                    st.success(f"執行結果已成功匯出至 {csv_path}")
                if taskid_path:
                    st.success(f"Task IDs 已成功匯出至 {taskid_path}")
            else:
                st.warning("請上傳 txt 並輸入 Script 名稱")

elif option == "批次收集檔案":
    with st.expander("6. 批次收集檔案", expanded=True):
        st.subheader("Collect File")
        file = st.file_uploader("上傳 Agent GUIDs 的 txt", type="txt")
        collect_path = st.text_input("目標檔案路徑（例如 C:\\\\test.txt）")
        if st.button("收集檔案"):
            if file and collect_path:
                path = "/tmp/agents_collect.txt"
                with open(path, "wb") as f:
                    f.write(file.read())
                manager = CollectFileManager()
                manager.collect_from_file(path, collect_path)
                st.success("收集完成")
            else:
                st.warning("請上傳 txt 並輸入路徑")

    with st.expander("單一收集（手動輸入 Agent GUID）", expanded=False):
        st.subheader("單一 Agent 檔案收集")
        single_guid = st.text_input("Agent GUID（單一）")
        single_path = st.text_input("檔案路徑（單一）", value="C:\\Users\\Public\\Desktop\\test.zip")
        if st.button("執行單一收集"):
            if single_guid and single_path:
                manager = CollectFileManager()
                result = manager.collect_file(single_guid, single_path)
                if result:
                    task_id = result.get("task_id", "N/A")
                    status = result.get("status", "Unknown")
                    if status in ["Success", "Accepted"]:
                        st.success(f"✅ 任務狀態：{status}，Task ID: {task_id}")
                    else:
                        st.error(f"❌ 收集失敗（狀態: {status}）")
                else:
                    st.error("❌ 無法取得任務結果，請檢查輸入或 API 設定")
            else:
                st.warning("請填入 GUID 和路徑")

elif option == "下載並解壓縮檔案":
    with st.expander("7. 下載並解壓縮檔案", expanded=True):
        st.subheader("下載並解壓縮")
        file = st.file_uploader("上傳包含 Task ID 的txt檔案", type="txt")
        if st.button("開始下載"):
            if file:
                path = "/tmp/taskids.txt"
                with open(path, "wb") as f:
                    f.write(file.read())
                manager = TaskDownloader()
                manager.process_from_file(path)
                st.success("任務處理完成")
            else:
                st.warning("請上傳 txt 檔")

    with st.expander("單一下載（輸入 Task ID）", expanded=False):
        st.subheader("單一任務下載")
        single_task_id = st.text_input("Task ID（單一）")
        save_dir = st.text_input("儲存目錄（例如 C:\\Downloads\\）", value="C:\\Downloads\\")
        save_name = st.text_input("自訂壓縮檔名稱（例如 result.7z）", value="result.7z")
        if st.button("執行單一下載"):
            if single_task_id:
                import shutil
                manager = TaskDownloader()
                result = manager.process_task(single_task_id)
                if result:
                    status = result.get("status")
                    if status == "Success":
                        st.success(f"✅ 下載與解壓縮完成（Task ID: {single_task_id}）")
                        original_zip_path = os.path.join("downloaded_files", f"{single_task_id}.7z")
                        target_path = os.path.join(save_dir, save_name)

                        try:
                            shutil.move(original_zip_path, target_path)
                            st.success(f"✅ 檔案已搬移至: {target_path}")
                        except Exception as e:
                            st.warning(f"⚠️ 檔案搬移失敗：{e}")
                    elif status == "NotReady":
                        st.warning(f"⚠️ Task ID {single_task_id} 尚未完成，跳過下載")
                    else:
                        st.error(f"❌ 任務處理失敗（Task ID: {single_task_id}），狀態: {status}")
                else:
                    st.error("❌ 無法取得任務資訊，請確認 Task ID 是否正確")
            else:
                st.warning("請輸入 Task ID")

elif option == "檢查 Task ID 狀態":
    with st.expander("8. 檢查 Task ID 狀態", expanded=True):
        st.subheader("檢查任務狀態（新視窗背景執行）")
        file = st.file_uploader("上傳 Task ID txt", type="txt")
        if file:
            path = "/tmp/task_check.txt"
            with open(path, "wb") as f:
                f.write(file.read())

            system = platform.system().lower()
            script_module = "utils.check_task_status"
            if system == "windows":
                script_path = os.path.join(os.getcwd(), "utils", "check_task_status.py")
                subprocess.Popen(["python", script_path, path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif system == "darwin":
                cwd = os.getcwd()
                path = os.path.abspath(path)
                cmd = f'tell application "Terminal" to do script "cd \\"{cwd}\\"; python3 -m {script_module} \\"{path}\\""'
                subprocess.Popen(["osascript", "-e", cmd])
            else:
                subprocess.Popen(["python3", "-m", script_module, path])
            st.info("任務監控中，請查看新視窗")

elif option == "持續監控所有 Task 狀態（Web 介面）":
    from utils.api_client import APIClient
    from utils.all_tasks_status import fetch_all_tasks
    import time
    from streamlit_autorefresh import st_autorefresh
    import pandas as pd
    from streamlit.components.v1 import html

    st.subheader("🔁 每 90 秒自動更新任務狀態")
    refresh_interval = 90 * 1000  # 毫秒
    st_autorefresh(interval=refresh_interval, key="task_autorefresh")

    st.subheader("🌐 顯示目前所有任務（API 方式）")

    if st.button("🔄 重新整理任務狀態"):
        st.rerun()

    all_tasks = fetch_all_tasks()
    if all_tasks:
        table_data = []
        for task in all_tasks:
            task_id = task.get("id", "N/A")
            status_raw = task.get("status", "Unknown").lower()
            if status_raw == "succeeded":
                status = f"<span style='color: green'>{status_raw}</span>"
            elif status_raw == "failed":
                status = f"<span style='color: red'>{status_raw}</span>"
            elif status_raw == "running":
                status = f"<span style='color: orange'>{status_raw}</span>"
            else:
                status = status_raw
            endpoint = task.get("endpointName", "N/A")
            file_path = task.get("filePath") or task.get("fileName") or "N/A"
            error_msg = task.get("error", {}).get("message", "")
            description = task.get("description", "N/A")
            table_data.append({
                "Task ID": task_id,
                "狀態": status,
                "端點": endpoint,
                "檔案路徑/名稱": file_path,
                "錯誤訊息": error_msg,
                "描述": description,
            })

        df = pd.DataFrame(table_data)
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("❌ 無法取得任務列表或目前尚無任務")

elif option == "關於本工具":
    with st.expander("🔧 關於本工具", expanded=True):
        st.markdown("""
        **Trend Micro Vision One 工具整合面板**  
        版本：v1.1.0  
        作者：Josh Huang  
        本工具整合常用腳本管理、批次執行、任務狀態監控與檔案下載功能。  
        若有任何問題或建議，請聯絡內部資訊安全團隊。
        """)
