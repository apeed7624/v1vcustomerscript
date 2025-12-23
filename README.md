Trend Micro Vison one API Tool

本專案為整合式 Web 工具，提供下列功能：

- **多 Tenant 管理**：支援多個 Vision One 環境切換與管理
- 任務下發與監控（含單一 / 批次）
- 自動下載與解壓縮 Task 結果
- 任務狀態即時查詢（API）
- 支援自訂儲存路徑與任務描述

---

## 執行環境需求

- Python 3.9+
- 建議使用虛擬環境（venv）

---

## 安裝套件

```bash
pip install -r requirements.txt
```

## 執行方式

1. **(Optional) 設定檔準備**:
   - 專案內附有 `tenants_template.json`。
   - 首次執行時，程式會自動建立 `tenants.json`。
   - 若您已有舊版 `config.py`，程式會自動將其遷移至新設定檔。

2. **啟動程式**:
   ```bash
   streamlit run main.py
   ```

3. **設定 API Key**:
   - 啟動後，請至側邊欄的 **「⚙️ 設定與 Tenant 切換」** 頁面。
   - 新增或編輯您的 Tenant 資訊 (API Key, Base URL)。

## 專案結構

```text
.
├── main.py                  # 主介面入口
├── requirements.txt         # 所需 Python 套件
├── changelog.md             # 版本記錄
├── tenants.json             # (自動產生) 儲存多 Tenant 設定，已加入 .gitignore
├── tenants_template.json    # 設定檔範本
├── utils/                   # 功能模組
│   ├── api_client.py
│   ├── config_manager.py    # 設定檔管理模組
│   ├── download_task.py
│   ├── collect_file.py
│   ├── all_tasks_status.py
│   └── ...
├── downloaded_files/        # 下載的原始壓縮檔
├── extracted_files/         # 7z 解壓縮內容
├── assessment_file/         # assessment.zip 的解壓結果
├── exported_results/        # 任務結果報表（CSV）
```
