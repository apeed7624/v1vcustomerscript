from utils.api_client import APIClient

def fetch_all_tasks():
    """呼叫 /v3.0/response/tasks 並回傳 task 狀態列表"""
    api = APIClient()
    result = api.send_request("GET", "/v3.0/response/tasks")
    if not result or "items" not in result:
        return []
    return result["items"]