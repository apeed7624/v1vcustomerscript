import os
from utils.api_client import APIClient

class YaraScanManager:
    def __init__(self):
        self.api_client = APIClient()
        self.url_path = "/v3.0/response/endpoints/runYaraRules"

    def run_yara_scan(self, payload: dict):
        """
        執行 YARA 掃描任務（支援多個 endpoint）
        :param payload: dict，包含 agentGuids list 及其他掃描參數
        """
        import json

        if not payload or not isinstance(payload, dict):
            print("❌ 傳入的 payload 不是有效的字典格式。")
            return None

        agent_guids = payload.get("agentGuids", [])
        if not agent_guids or not isinstance(agent_guids, list):
            print("❌ payload 中缺少有效的 'agentGuids' 列表。")
            return None

        print("🚀 即將送出 YARA Scan Request：")
        print(payload)

        # 拆解成符合 API 要求的 list 格式，每個 agentGuid 對應一份 payload
        payload_copy = payload.copy()
        payload_copy.pop("agentGuids", None)
        request_body = []
        for guid in agent_guids:
            item = payload_copy.copy()
            item["agentGuid"] = guid
            request_body.append(item)

        print("🚀 即將送出的 Request Payload:")
        print(json.dumps(request_body, indent=2, ensure_ascii=False))

        headers = self.api_client.headers

        import pprint
        print("📤 Headers to send:")
        pprint.pprint(headers)

        print("📤 Payload to send (JSON body):")
        pprint.pprint(request_body)

        try:
            response = self.api_client.send_request(
                "POST",
                self.url_path,
                data=request_body
            )

            import pprint

            # 列印回應 Headers（標準化）
            response_headers = {}
            if hasattr(response, 'headers'):
                response_headers = dict(response.headers)
            elif isinstance(response, dict) and 'headers' in response:
                response_headers = response['headers']
            print("📥 回應 Headers:")
            if isinstance(response_headers, dict):
                for k, v in response_headers.items():
                    print(f"🔸 {k}: {v}")
            else:
                print("⚠️ 無法讀取 Headers")

            # 處理回傳結果內容
            if hasattr(response, 'json'):
                try:
                    result = response.json()
                except Exception:
                    result = response.text
            else:
                result = response if isinstance(response, (dict, list)) else None

            # response_headers 已於上方取得

            # 印出回傳的資料內容
            print("📦 API 回傳結果:", result)

        except Exception as e:
            print(f"❌ 發送 YARA API 時發生錯誤: {e}")
            return None

        if result is None:
            print("❌ 無法執行 YARA 掃描，請檢查 API 權限或參數設定")
            return None

        if isinstance(result, dict) and "error" in result:
            print(f"❌ API 回傳錯誤: {result['error']}")
            return None

        print("✅ YARA 任務發出成功")
        return {
            "data": result,
            "headers": response_headers
        }

if __name__ == "__main__":
    runner = YaraScanManager()
    print("請依序輸入以下資訊：")
    agent_guid = input("Agent GUID: ").strip()
    target_file_location = input("掃描檔案路徑（例如：C:\\Users\\test\\Downloads）: ").strip()
    yara_rule_filename = input("請輸入 YARA rule 檔案名稱（例如：xxx.yara）: ").strip()

    payload = {
        "agentGuids": [agent_guid],
        "target": "File",
        "targetFileLocation": target_file_location,
        "targetFileSize": "1M",
        "targetFileOption": "SCAN_ALL",
        "yaraRuleFileName": yara_rule_filename,
        "description": "Run YARA rule task"
    }

    runner.run_yara_scan(payload)