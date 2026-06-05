#!/bin/bash
# ============================================================
# 售后数据分析系统 — 一键启动脚本 (Linux / Ubuntu)
# After-Sales Data Analysis System — One-click Start Script
# ============================================================

set -e

echo "=============================="
echo "  Water X Technologies"
echo "  售后数据分析系统  Setup"
echo "=============================="

# ---- 1. 检查 Python ----
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.10+"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "✓ Python $(python3 --version) detected"

# ---- 2. 创建虚拟环境（可选）----
if [ ! -d "venv" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# ---- 3. 安装依赖 ----
echo "→ Installing Python dependencies..."
pip install -r backend/requirements.txt --quiet

# ---- 4. 环境变量（可在此修改密码）----
# SHOUHOU_PASSWORD: 登录密码，默认 waterx2026
# SHOUHOU_SECRET:   Session 密钥，默认 shouhou-analyzer-secret-2026
# PORT:             服务端口，默认 5859
# CORS_ORIGINS:     允许的来源，默认自动允许所有（部署时建议指定域名）
export SHOUHOU_PASSWORD="${SHOUHOU_PASSWORD:-waterx2026}"
export SHOUHOU_SECRET="${SHOUHOU_SECRET:-shouhou-analyzer-secret-2026}"
export PORT="${PORT:-5859}"

# 自动检测本机 IP 并设置 CORS_ORIGINS（允许通过 IP 直接访问）
# 如果有域名，请手动设置：export CORS_ORIGINS="https://yourdomain.com"
if [ -z "${CORS_ORIGINS}" ]; then
    # 获取本机对外 IP（优先使用 eth0 / 云服务器网卡）
    MY_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "")
    if [ -n "$MY_IP" ]; then
        export CORS_ORIGINS="http://localhost:${PORT},http://127.0.0.1:${PORT},http://${MY_IP}:${PORT},http://${MY_IP}"
    else
        export CORS_ORIGINS="http://localhost:${PORT},http://127.0.0.1:${PORT}"
    fi
fi

echo ""
echo "=============================="
echo "  Starting server..."
echo "  URL:      http://0.0.0.0:${PORT}"
echo "  Password: ${SHOUHOU_PASSWORD}"
echo "  CORS:     ${CORS_ORIGINS}"
echo "  Language: Auto-detect (中文 / English / 日本語)"
echo "=============================="
echo ""

# ---- 5. 启动 Flask（绑定 0.0.0.0 允许外网访问）----
# 注意：端口通过环境变量 PORT 传递，不使用命令行参数
cd backend
python3 app.py
