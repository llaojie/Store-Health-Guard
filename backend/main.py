"""FastAPI 主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import stores, health, alerts, diagnosis
from config.database import DATABASE_URL, ENGINE_KWARGS
from sqlalchemy import create_engine
from models.store import Base

app = FastAPI(
    title="Store Health Guard - 门店健康度预警系统",
    description="基于餐饮行业核心指标体系的门店健康度监测、预警与诊断系统",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化
engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)
Base.metadata.create_all(bind=engine)

# 注册路由
app.include_router(stores.router, prefix="/api/stores", tags=["门店管理"])
app.include_router(health.router, prefix="/api/health", tags=["健康度监测"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["预警管理"])
app.include_router(diagnosis.router, prefix="/api/diagnosis", tags=["诊断工具"])


@app.get("/api")
def root():
    return {
        "name": "Store Health Guard",
        "version": "1.0.0",
        "description": "门店健康度预警系统 API",
        "docs": "/api/docs"
    }


@app.get("/api/biz-types")
def get_biz_types():
    """获取支持的业态列表"""
    from services.health_engine import load_biz_config
    config = load_biz_config()
    result = []
    for key, val in config.get("biz_types", {}).items():
        result.append({"code": key, "name": val.get("name", key)})
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
