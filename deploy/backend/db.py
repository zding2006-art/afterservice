# -*- coding: utf-8 -*-
"""SQLite 数据库 — 存储历月分析数据，支持多月对比

职责：数据库读写（CRUD）。
多月推移计算已移至 services/trends.py。
"""

import sqlite3
import json
import os
import numpy as np

from services.trends import build_trends

DB_PATH = os.path.join(os.path.dirname(__file__), "after_sales.db")


def _to_native(obj):
    """递归转换 numpy 类型为 Python 原生类型"""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    return obj


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS monthly_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        month_label TEXT NOT NULL,
        total_records INTEGER,
        total_cost REAL,
        in_warranty_count INTEGER,
        out_warranty_count INTEGER,
        cover_count INTEGER,
        whole_count INTEGER,
        analysis_data TEXT,
        raw_data_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(year, month)
    );
    """)
    # 兼容旧表：如果 raw_data_json 列不存在则添加
    try:
        conn.execute("ALTER TABLE monthly_summary ADD COLUMN raw_data_json TEXT")
    except:
        pass
    conn.commit()
    conn.close()


def save_monthly(year, month, month_label, summary, results, raw_data_json=None):
    """保存当月分析结果"""
    conn = get_db()
    conn.execute("""
    INSERT OR REPLACE INTO monthly_summary
        (year, month, month_label, total_records, total_cost,
         in_warranty_count, out_warranty_count, cover_count, whole_count, analysis_data, raw_data_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        year, month, month_label,
        summary["total_records"], summary["total_cost"],
        summary["in_warranty_count"], summary["out_warranty_count"],
        summary["cover_count"], summary["whole_count"],
        json.dumps(_to_native(results), ensure_ascii=False),
        raw_data_json
    ))
    conn.commit()
    conn.close()


def get_all_months():
    """获取所有已存储月份的基本信息"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, year, month, month_label, total_records, total_cost, "
        "in_warranty_count, out_warranty_count, cover_count, whole_count, created_at "
        "FROM monthly_summary ORDER BY year, month"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_month_detail(month_id):
    """获取某月完整分析数据"""
    conn = get_db()
    row = conn.execute("SELECT * FROM monthly_summary WHERE id = ?", (month_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["analysis_data"] = json.loads(d["analysis_data"])
    return d


def get_all_months_with_analysis():
    """获取所有月份完整数据（含 analysis_data JSON）"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, year, month, month_label, total_records, total_cost, "
        "in_warranty_count, out_warranty_count, cover_count, whole_count, analysis_data, created_at "
        "FROM monthly_summary ORDER BY year, month"
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["analysis_data"] = json.loads(d["analysis_data"])
        except (json.JSONDecodeError, TypeError):
            d["analysis_data"] = {}
        result.append(d)
    return result


def get_comparison_data():
    """获取多月对比数据（含推移趋势）"""
    months_data = get_all_months_with_analysis()
    months = [{k: v for k, v in m.items() if k != "analysis_data"} for m in months_data]
    comparison = {
        "labels": [],
        "total_records": [],
        "total_cost": [],
        "in_warranty_ratio": [],
        "cover_ratio": [],
        "details": months
    }
    for m in months_data:
        comparison["labels"].append(m["month_label"])
        comparison["total_records"].append(m["total_records"])
        comparison["total_cost"].append(round(m["total_cost"], 2))
        comparison["in_warranty_ratio"].append(
            round(m["in_warranty_count"] / m["total_records"] * 100, 1) if m["total_records"] else 0
        )
        comparison["cover_ratio"].append(
            round(m["cover_count"] / m["total_records"] * 100, 1) if m["total_records"] else 0
        )

    # 推移数据（至少2个月才生成）
    if len(months_data) >= 2:
        comparison["trends"] = build_trends(months_data)
    else:
        comparison["trends"] = None

    return comparison


def delete_month(month_id):
    conn = get_db()
    conn.execute("DELETE FROM monthly_summary WHERE id = ?", (month_id,))
    conn.commit()
    conn.close()
