# EasyDocker 使用說明

本教學將引導您完成 Docker 的安裝，並使用 EasyDocker.exe 快速將 Python 程式封裝成 Docker 映像檔。

---

## 一、安裝 Docker Desktop

### 1. 系統需求
- **Windows**：Windows 10 或 11 (64位元)，需啟用 WSL 2
- **Mac**：macOS 11 (Big Sur) 或更新版本

> WSL 2 是 Windows 的 Linux 子系統，Docker Desktop 安裝時會引導設定。

### 2. 下載 Docker Desktop
- 官方下載網址：[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

### 3. 安裝與啟動
- 執行安裝檔，依指示完成安裝
- Windows 請勾選 "Use WSL 2 instead of Hyper-V"
- 安裝完成後重啟電腦，啟動 Docker Desktop

### 4. 驗證安裝
打開終端機或命令提示字元，輸入：

```sh
docker --version
```

若顯示版本資訊，代表安裝成功！

---

## 二、使用 EasyDocker.exe 封裝 Python 程式

### 1. 準備專案
- 建立資料夾（如 my-python-project）
- 放入您的 Python 主程式（如 main.py）及 EasyDocker.exe

```
my-python-project/
├── EasyDocker.exe
└── main.py
```

#### 範例 main.py
```python
import requests
import time

def get_title():
    try:
        r = requests.get('https://www.python.org')
        title = r.text.split('<title>')[1].split('</title>')[0]
        print(f"成功抓取標題: {title}")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == '__main__':
    print("Python 容器啟動！")
    get_title()
    print("程式將在 10 秒後結束...")
    time.sleep(10)
    print("程式結束。")
```

### 2. 執行封裝工具
- 直接雙擊 EasyDocker.exe 啟動
- 依照互動式指示操作

### 3. 操作流程
- 語言選擇：直接 Enter 使用中文
- 主程式檔案：自動偵測 main.py，Enter 確認
- 映像名稱：可自訂或 Enter 使用預設
- 是否產生 run_docker.bat：建議 Enter
- 是否自訂 Dockerfile：如需安裝特殊系統套件請選 y
- 是否輸出 log 檔：建議 Enter

### 4. 自動產生檔案
- requirements.txt：自動偵測 import 並產生
- Dockerfile：自動產生
- run_docker.bat：自動產生（Windows）
- build.log：自動產生

產生後的資料夾結構：
```
my-python-project/
├── EasyDocker.exe
├── main.py
├── Dockerfile
├── requirements.txt
├── run_docker.bat
└── build.log
```

---

## ⚠️ 重要提醒：系統層級依賴

EasyDocker 只會自動偵測 Python 套件（寫入 requirements.txt）。

若您的程式需要安裝系統層級函式庫（如 ODBC、影像處理、資料庫驅動等），請在「是否自訂 Dockerfile」選 y，並貼上自訂內容。

### 範例：安裝 Microsoft ODBC Driver for SQL Server

```dockerfile
FROM python:3.11-slim
# --- 安裝 ODBC Driver ---
RUN apt-get update && apt-get install -y curl gnupg
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
# --- 其餘步驟 ---
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
CMD ["python", "main.py"]
```

---

## 三、運行 Docker 容器

### 方法一：雙擊 run_docker.bat
- 會自動啟動容器並執行主程式

### 方法二：命令列

```sh
docker run --rm my-first-app
```

- my-first-app 請換成您設定的映像名稱

---

## 執行結果範例

```
Python 容器啟動！
成功抓取標題: Welcome to Python.org
程式將在 10 秒後結束...
程式結束。
```

---

恭喜！您已成功將 Python 程式封裝成 Docker 容器並順利運行。
