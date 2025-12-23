import json
import os
import stat

CONFIG_FILE = "tenants.json"

class ConfigManager:
    def __init__(self):
        self.config_file = CONFIG_FILE
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        """確保設定檔存在，若不存在則嘗試從舊 config.py 遷移"""
        if not os.path.exists(self.config_file):
            initial_data = {
                "active_tenant": "Default",
                "tenants": {}
            }
            
            # 嘗試從舊 config.py 遷移
            try:
                import utils.config as old_config
                if hasattr(old_config, "API_KEY") and hasattr(old_config, "BASE_URL"):
                    initial_data["tenants"]["Default"] = {
                        "api_key": old_config.API_KEY,
                        "base_url": old_config.BASE_URL,
                        "note": "Migrated from config.py"
                    }
                    print("✅ 已從 config.py 遷移設定至 tenants.json")
            except ImportError:
                # 若沒有舊 config.py，則建立空的 Default
                initial_data["tenants"]["Default"] = {
                    "api_key": "",
                    "base_url": "https://api.sg.xdr.trendmicro.com",
                    "note": "Default Tenant"
                }
            
            self._save_config(initial_data)

    def _load_config(self):
        """讀取設定檔"""
        if not os.path.exists(self.config_file):
            return {"active_tenant": "Default", "tenants": {}}
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"active_tenant": "Default", "tenants": {}}

    def _save_config(self, data):
        """儲存設定檔並設定權限"""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        # 設定檔案權限為僅擁有者可讀寫 (600) - Unix-like systems
        try:
            os.chmod(self.config_file, stat.S_IRUSR | stat.S_IWUSR)
        except Exception:
            pass # Windows 可能不支援或行為不同，忽略錯誤

    def get_active_config(self):
        """取得當前 Active Tenant 的設定"""
        data = self._load_config()
        active_name = data.get("active_tenant")
        tenant = data.get("tenants", {}).get(active_name)
        
        if not tenant:
            return None, None # API_KEY, BASE_URL
            
        return tenant.get("api_key"), tenant.get("base_url")

    def get_all_tenants(self):
        """取得所有 Tenant 列表"""
        data = self._load_config()
        return data.get("tenants", {})

    def get_active_tenant_name(self):
        """取得當前 Active Tenant 名稱"""
        data = self._load_config()
        return data.get("active_tenant")

    def add_tenant(self, name, api_key, base_url, note=""):
        """新增或更新 Tenant"""
        data = self._load_config()
        data["tenants"][name] = {
            "api_key": api_key,
            "base_url": base_url,
            "note": note
        }
        # 如果是第一個新增的，設為 Active
        if len(data["tenants"]) == 1:
            data["active_tenant"] = name
            
        self._save_config(data)
        return True

    def delete_tenant(self, name):
        """刪除 Tenant"""
        data = self._load_config()
        if name in data["tenants"]:
            del data["tenants"][name]
            
            # 如果刪除的是 Active，且還有其他 Tenant，隨機選一個當 Active
            if data["active_tenant"] == name:
                if data["tenants"]:
                    data["active_tenant"] = next(iter(data["tenants"]))
                else:
                    data["active_tenant"] = None
            
            self._save_config(data)
            return True
        return False

    def set_active_tenant(self, name):
        """切換 Active Tenant"""
        data = self._load_config()
        if name in data["tenants"]:
            data["active_tenant"] = name
            self._save_config(data)
            return True
        return False
