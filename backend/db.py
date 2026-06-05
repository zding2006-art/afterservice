# -*- coding: utf-8 -*-
"""SQLite 数据库 — 存储历月分析数据，支持多月对比"""

import sqlite3
import json
import os
import numpy as np

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


def _build_trends(months_data):
    """从各月的 analysis_data 中构建多维度推移数据"""
    labels = [m["month_label"] for m in months_data]
    n = len(labels)

    # --- 通用工具：从单月分析提取指标 ---
    def _get_top10_models(ad, key):
        """提取 TOP10 型号及其发生次数"""
        data = (ad or {}).get(key, {}).get("data", [])
        return [(row.get("型号", ""), row.get("发生次数", 0)) for row in data if row.get("型号")]

    def _get_special_count(ad, key):
        """提取单项指标的发生次数"""
        data = (ad or {}).get(key, {}).get("data", [])
        if data:
            return data[0].get("发生次数", 0)
        return 0

    # --- 1. 盖机保内 TOP10 型号推移 ---
    cover_models_all = {}
    for m in months_data:
        for model, cnt in _get_top10_models(m.get("analysis_data"), "analysis_3"):
            cover_models_all[model] = cover_models_all.get(model, 0) + cnt
    top_cover_models = sorted(cover_models_all.items(), key=lambda x: -x[1])[:8]
    cover_top10_trend = {
        "models": [m for m, _ in top_cover_models],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["型号"] + labels, "rows": []}
    }
    for model, _ in top_cover_models:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = 0
            for row in (ad or {}).get("analysis_3", {}).get("data", []) if ad else []:
                if row.get("型号") == model:
                    found = row.get("发生次数", 0)
                    break
            counts.append(found)
        cover_top10_trend["datasets"].append({"model": model, "data": counts})
        cover_top10_trend["table"]["rows"].append({"label": model, "data": counts})

    # --- 2. 整机保内 TOP10 型号推移 ---
    whole_models_all = {}
    for m in months_data:
        for model, cnt in _get_top10_models(m.get("analysis_data"), "analysis_6"):
            whole_models_all[model] = whole_models_all.get(model, 0) + cnt
    top_whole_models = sorted(whole_models_all.items(), key=lambda x: -x[1])[:8]
    whole_top10_trend = {
        "models": [m for m, _ in top_whole_models],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["型号"] + labels, "rows": []}
    }
    for model, _ in top_whole_models:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = 0
            for row in (ad or {}).get("analysis_6", {}).get("data", []) if ad else []:
                if row.get("型号") == model:
                    found = row.get("发生次数", 0)
                    break
            counts.append(found)
        whole_top10_trend["datasets"].append({"model": model, "data": counts})
        whole_top10_trend["table"]["rows"].append({"label": model, "data": counts})

    # --- 3. 保内盖机 TOP10 各 TOP10 部品推移（取全域频次最高的部品） ---
    cover_parts_all = {}
    for m in months_data:
        ad = m.get("analysis_data", {})
        for model_data in (ad or {}).get("analysis_5", {}).get("data", []) if ad else []:
            for part in model_data.get("TOP10部品", []):
                pname = part.get("配件", "")
                cnt = part.get("发生次数", 0)
                cover_parts_all[pname] = cover_parts_all.get(pname, 0) + cnt
    top_cover_parts = sorted(cover_parts_all.items(), key=lambda x: -x[1])[:8]
    cover_parts_trend = {
        "parts": [p for p, _ in top_cover_parts],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["部品"] + labels, "rows": []}
    }
    for pname, _ in top_cover_parts:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = 0
            for model_data in (ad or {}).get("analysis_5", {}).get("data", []) if ad else []:
                for part in model_data.get("TOP10部品", []):
                    if part.get("配件") == pname:
                        found += part.get("发生次数", 0)
            counts.append(found)
        cover_parts_trend["datasets"].append({"part": pname, "data": counts})
        cover_parts_trend["table"]["rows"].append({"label": pname, "data": counts})

    # 盖机部品详情表：各型号对应的 TOP10 部品（取最新月份为参考）
    cover_parts_detail = {"labels": labels, "models": []}
    latest_ad = months_data[-1].get("analysis_data", {}) if months_data else {}
    for model_data in (latest_ad or {}).get("analysis_4", {}).get("data", []) if latest_ad else []:
        model_name = model_data.get("型号", "")
        parts_info = []
        for part in model_data.get("TOP10部品", []):
            pname = part.get("配件", "")
            # 按月份收集该配件在该型号下的次数
            pcounts = []
            for m in months_data:
                ad = m.get("analysis_data", {})
                found = 0
                for md2 in (ad or {}).get("analysis_4", {}).get("data", []) if ad else []:
                    if md2.get("型号") == model_name:
                        for pt in md2.get("TOP10部品", []):
                            if pt.get("配件") == pname:
                                found = pt.get("发生次数", 0)
                                break
                        break
                pcounts.append(found)
            parts_info.append({"name": pname, "data": pcounts})
        if parts_info:
            cover_parts_detail["models"].append({"model": model_name, "parts": parts_info})

    # --- 4. 保内整机 TOP10 各 TOP10 部品推移 ---
    whole_parts_all = {}
    for m in months_data:
        ad = m.get("analysis_data", {})
        for model_data in (ad or {}).get("analysis_8", {}).get("data", []) if ad else []:
            for part in model_data.get("TOP10部品", []):
                pname = part.get("配件", "")
                cnt = part.get("发生次数", 0)
                whole_parts_all[pname] = whole_parts_all.get(pname, 0) + cnt
    top_whole_parts = sorted(whole_parts_all.items(), key=lambda x: -x[1])[:8]
    whole_parts_trend = {
        "parts": [p for p, _ in top_whole_parts],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["部品"] + labels, "rows": []}
    }
    for pname, _ in top_whole_parts:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = 0
            for model_data in (ad or {}).get("analysis_8", {}).get("data", []) if ad else []:
                for part in model_data.get("TOP10部品", []):
                    if part.get("配件") == pname:
                        found += part.get("发生次数", 0)
            counts.append(found)
        whole_parts_trend["datasets"].append({"part": pname, "data": counts})
        whole_parts_trend["table"]["rows"].append({"label": pname, "data": counts})

    # 整机部品详情表
    whole_parts_detail = {"labels": labels, "models": []}
    latest_ad2 = months_data[-1].get("analysis_data", {}) if months_data else {}
    for model_data in (latest_ad2 or {}).get("analysis_7", {}).get("data", []) if latest_ad2 else []:
        model_name = model_data.get("型号", "")
        parts_info = []
        for part in model_data.get("TOP10部品", []):
            pname = part.get("配件", "")
            pcounts = []
            for m in months_data:
                ad = m.get("analysis_data", {})
                found = 0
                for md2 in (ad or {}).get("analysis_7", {}).get("data", []) if ad else []:
                    if md2.get("型号") == model_name:
                        for pt in md2.get("TOP10部品", []):
                            if pt.get("配件") == pname:
                                found = pt.get("发生次数", 0)
                                break
                        break
                pcounts.append(found)
            parts_info.append({"name": pname, "data": pcounts})
        if parts_info:
            whole_parts_detail["models"].append({"model": model_name, "parts": parts_info})

    # --- 5. 专项指标推移（座盖 / 座盖软胶垫 / 柔光灯） ---
    special_datasets = [
        {"label": "保内座盖投诉", "data": [_get_special_count(m.get("analysis_data"), "analysis_9") for m in months_data]},
        {"label": "保内座盖软胶垫投诉", "data": [_get_special_count(m.get("analysis_data"), "analysis_10") for m in months_data]},
        {"label": "柔光灯投诉", "data": [_get_special_count(m.get("analysis_data"), "analysis_11") for m in months_data]},
    ]
    special_trend = {
        "labels": labels,
        "datasets": special_datasets,
        "table": {"columns": ["指标"] + labels, "rows": [
            {"label": ds["label"], "data": ds["data"]} for ds in special_datasets
        ]}
    }

    # --- 6. 座盖故障使用月数推移 ---
    def _extract_month_num(bucket_label):
        """从 'N个月' 中提取数字 N 用于排序，未知排最后"""
        import re
        m = re.search(r'(\d+)', str(bucket_label))
        return int(m.group(1)) if m else 9999

    usage_buckets_set = set()
    for m in months_data:
        ad = m.get("analysis_data", {})
        for row in (ad or {}).get("analysis_12", {}).get("data", []) if ad else []:
            bucket = row.get("使用月数区间", "")
            if bucket:
                usage_buckets_set.add(bucket)
    usage_buckets_order = sorted(usage_buckets_set, key=_extract_month_num)
    seat_usage_trend = {
        "labels": labels, "buckets": usage_buckets_order, "datasets": [],
        "table": {"columns": ["使用月数"] + labels, "rows": []}
    }
    for bucket in usage_buckets_order:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = 0
            for row in (ad or {}).get("analysis_12", {}).get("data", []) if ad else []:
                if row.get("使用月数区间") == bucket:
                    found = row.get("发生次数", 0)
                    break
            counts.append(found)
        seat_usage_trend["datasets"].append({"bucket": bucket, "data": counts})
        seat_usage_trend["table"]["rows"].append({"label": bucket, "data": counts})

    return {
        "cover_top10": cover_top10_trend,
        "whole_top10": whole_top10_trend,
        "cover_parts": cover_parts_trend,
        "whole_parts": whole_parts_trend,
        "cover_parts_detail": cover_parts_detail,
        "whole_parts_detail": whole_parts_detail,
        "special": special_trend,
        "seat_usage": seat_usage_trend,
    }


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
        comparison["trends"] = _build_trends(months_data)
    else:
        comparison["trends"] = None

    return comparison


def delete_month(month_id):
    conn = get_db()
    conn.execute("DELETE FROM monthly_summary WHERE id = ?", (month_id,))
    conn.commit()
    conn.close()
