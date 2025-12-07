import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .routers.routers import router as user_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mock User API",
    description="Hands-on Practice for RESTful API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 預設位置 (明確寫出以便理解)
    redoc_url="/redoc" 
)

# 1. 註冊 API Routers (API 優先匹配)
app.include_router(user_router, tags=["Users"])

# 2. CORS 設定
# 雖然整合後是同源 (Same Origin)，但在開發模式下 React (Port 5173) 仍需要 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. 靜態檔案服務 (整合 React Dashboard)
# ==========================================

# 設定前端編譯後的路徑 (對應 Dockerfile 中的 COPY 路徑)
FRONTEND_DIST_DIR = "frontend/dist"

# 檢查目錄是否存在 (避免本地開發時若無編譯檔案而報錯)
if os.path.exists(FRONTEND_DIST_DIR):
    # A. 掛載靜態資源 (JS, CSS, Images)
    # Vite 編譯後通常會有 assets 資料夾，掛載到 /assets 路徑
    app.mount("/assets", StaticFiles(directory=f"{FRONTEND_DIST_DIR}/assets"), name="assets")

    # B. 根路由回傳 index.html (SPA Entry Point)
    @app.get("/")
    async def read_root():
        return FileResponse(f"{FRONTEND_DIST_DIR}/index.html")

    # (可選) 若使用 React Router，可在此添加 catch-all route 導向 index.html