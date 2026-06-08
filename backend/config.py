# -*- coding: utf-8 -*-
"""统一配置 — 所有部署相关参数从这里读取。

优先级：环境变量 > 此处默认值。
部署时只需设置对应的环境变量，无需修改源码。
"""

import os
import sys

# ── 运行环境 ──────────────────────────────────────────────
IS_FROZEN = getattr(sys, "frozen", False)


def root_dir() -> str:
    """返回可执行文件（或源码）所在目录，打包前后保持一致。"""
    if IS_FROZEN:
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# ── 服务配置 ──────────────────────────────────────────────
PORT: int = int(os.environ.get("PORT", 5859))

# ── 鉴权配置 ──────────────────────────────────────────────
# 生产环境：通过 SHOUHOU_PASSWORD 环境变量设置密码
ACCESS_PASSWORD: str = os.environ.get("SHOUHOU_PASSWORD", "waterx2026")
SECRET_KEY: str = os.environ.get("SHOUHOU_SECRET", "shouhou-analyzer-secret-2026")

# ── 路径配置 ──────────────────────────────────────────────
_ROOT = root_dir()

UPLOAD_FOLDER: str = os.environ.get(
    "UPLOAD_FOLDER",
    os.path.join(_ROOT, "uploads")
)

# 数据库路径：打包模式下放在 exe 所在目录的 backend/ 子目录
if IS_FROZEN:
    _db_dir = os.path.join(_ROOT, "backend")
    os.makedirs(_db_dir, exist_ok=True)
    DB_PATH: str = os.environ.get("DB_PATH", os.path.join(_db_dir, "after_sales.db"))
else:
    DB_PATH: str = os.environ.get(
        "DB_PATH",
        os.path.join(_ROOT, "after_sales.db")
    )

# 前端静态文件目录
_static_default = os.path.join(_ROOT, "frontend")
if not os.path.isdir(_static_default):
    # 源码目录：frontend 与 backend 同级
    _alt = os.path.join(os.path.dirname(_ROOT), "frontend")
    if os.path.isdir(_alt):
        _static_default = os.path.abspath(_alt)

STATIC_DIR: str = os.environ.get("STATIC_DIR", _static_default)

# ── CORS 配置 ──────────────────────────────────────────────
# 设为 "*" 允许所有来源（调试用），逗号分隔指定多个来源，留空使用默认本地列表
CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "")

DEFAULT_CORS_ORIGINS: list = [
    "http://localhost:5859", "http://127.0.0.1:5859",
    "http://localhost:80",   "http://127.0.0.1:80",
    "http://localhost",      "http://127.0.0.1",
]
