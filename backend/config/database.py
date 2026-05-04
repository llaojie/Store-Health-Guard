"""数据库配置 - 支持 SQLite(开发) / PostgreSQL(生产)"""
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./store_health.db"
)

# PostgreSQL 示例:
# DATABASE_URL = "postgresql://user:password@localhost:5432/store_health"

ENGINE_KWARGS = {}
if DATABASE_URL.startswith("sqlite"):
    ENGINE_KWARGS = {"connect_args": {"check_same_thread": False}}
