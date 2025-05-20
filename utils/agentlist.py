import csv
import os
import datetime
from utils.api_client import APIClient

class ClientManager:
    def __init__(self):
        self.api_client = APIClient()

    def list_all_clients(self):
        """列出全部 Vision One 上的 Client，並顯示 `agentGuid`、`endpointName`、`lastUsedIp`、`osName`、`edrSensor.connectivity`"""
        endpoint = "/v3.0/endpointSecurity/endpoints"
        params = {
            "orderBy": "agentGuid asc",  # 按照 agentGuid 遞增排序
            "top": 1000,  # 取得最多 1000 筆資料
            "select": "agentGuid,endpointName,lastUsedIp,osName,edrSensorConnectivity"  # ✅ 正確選取 edrSensor 欄位
        }

        result = self.api_client.send_request("GET", endpoint, params=params)

        if result is None:
            print("❌ API 回應為 None，請檢查 API Key 或權限")
            return []

        #print("🔍 API 回應內容: ", result)  # ✅ Debug: 確認 API 回應內容
        return result.get("items", [])

    def export_to_csv(self, agents):
        """將 Client 資料匯出至 CSV"""
        if not agents:
            print("❌ 沒有可匯出的 Client 資料")
            return

        # 產生 CSV 檔名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clients_{timestamp}.csv"

        # 定義 CSV 欄位名稱
        headers = ["Agent GUID", "Endpoint Name", "Last Used IP", "OS Name", "EDR Sensor Connectivity"]

        # 確保目錄存在
        output_dir = "client_export_data"
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

        # 寫入 CSV 檔案
        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # 寫入標題
            for agent in agents:
                edr_status = agent.get("edrSensor", {}).get("connectivity", "Disconnected")  # ✅ 正確取得值

                writer.writerow([
                    agent.get("agentGuid", "未知"),
                    agent.get("endpointName", "未知"),
                    agent.get("lastUsedIp", "未知"),
                    agent.get("osName", "未知"),
                    edr_status
                ])

        print(f"✅ Client 資料已成功匯出至 {file_path}")

if __name__ == "__main__":
    manager = ClientManager()
    agents = manager.list_all_clients()

    if agents:
        print("✅ 取得 Client 資訊:")
        for agent in agents:
            agent_guid = agent.get("agentGuid", "未知")
            endpoint_name = agent.get("endpointName", "未知")
            last_used_ip = agent.get("lastUsedIp", "未知")
            os_name = agent.get("osName", "未知")
            edr_sensor_connectivity = agent.get("edrSensor", {}).get("connectivity", "Disconnected")  # ✅ 正確取值

            print(f"- {endpoint_name} (Agent GUID: {agent_guid}, Last Used IP: {last_used_ip}, OS: {os_name}, Status: {edr_sensor_connectivity})")

        # 問使用者是否要匯出 CSV
        export_choice = input("\n是否要匯出資料到 CSV？(Y/N): ").strip().lower()
        if export_choice == "y":
            manager.export_to_csv(agents)
        else:
            print("🚀 匯出取消，回到主選單。")
    else:
        print("❌ 沒有找到任何 Client")
