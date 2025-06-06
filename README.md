Trend Micro Vison one API Tool

本專案為整合式 Web 工具，提供下列功能：

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

## 執行方式

1.rename config_template.py to config.py

2.add api key to config.py

3.streamlit run main.py



.
├── main.py                  # 主介面入口
├── requirements.txt         # 所需 Python 套件
├── changelog.md             # 版本記錄
├── utils/                   # 功能模組
│   ├── api_client.py
│   ├── download_task.py
│   ├── collect_file.py
│   ├── all_tasks_status.py
│   └── ...
├── downloaded_files/        # 下載的原始壓縮檔
├── extracted_files/         # 7z 解壓縮內容
├── assessment_file/         # assessment.zip 的解壓結果
├── exported_results/        # 任務結果報表（CSV）
