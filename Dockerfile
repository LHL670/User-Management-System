# ==========================================
# [Stage 1] 前端建置階段 (Build Frontend)
# ==========================================
# 使用 Node.js 22 (Alpine Linux) 來解決 Vite 版本的相容性問題
FROM node:22-alpine AS frontend-builder

# 設定前端建置工作目錄
WORKDIR /build

# 1. 複製 package.json 與 package-lock.json (利用 Docker Cache 加速安裝)
COPY frontend/package*.json ./

# 2. 安裝專案依賴
RUN npm install

# [關鍵修正] 強制安裝 lucide-react
# 這能防止因為本地 package.json 尚未更新導致 Rollup 無法解析圖標庫的錯誤
RUN npm install lucide-react

# 3. 複製所有前端原始碼
COPY frontend/ ./

# 4. 執行編譯 (產出物會位於 /build/dist)
RUN npm run build


# ==========================================
# [Stage 2] 後端執行階段 (Production Runtime)
# ==========================================
# 使用輕量級 Python 3.9 映像檔
FROM python:3.9-slim

# 設定後端工作目錄
WORKDIR /app

# 1. 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 複製後端程式碼與測試
COPY ./app ./app
COPY ./tests ./tests

# 3. [整合關鍵] 從 Stage 1 複製編譯好的前端檔案
# 將 /build/dist 複製到後端預期的 /app/frontend/dist 位置
COPY --from=frontend-builder /build/dist ./frontend/dist

# 4. 設定環境變數
ENV PYTHONPATH=/app

# 5. 啟動 FastAPI 服務 (Host 0.0.0.0 讓外部可存取)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]