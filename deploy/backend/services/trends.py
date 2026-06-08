# -*- coding: utf-8 -*-
"""
services/trends.py — 多月推移数据构建服务

职责：接收已从数据库读出的各月 analysis_data，
计算型号推移、部品推移、专项投诉推移、座盖使用月数推移等趋势数据。

与数据库无关，便于单独测试。
"""

import re


# ── 内部工具函数 ──────────────────────────────────────────

def _get_top10_models(analysis_data: dict, key: str) -> list:
    """从单月 analysis_data 提取 TOP10 型号及其发生次数。"""
    data = (analysis_data or {}).get(key, {}).get("data", [])
    return [(row.get("型号", ""), row.get("发生次数", 0))
            for row in data if row.get("型号")]


def _get_special_count(analysis_data: dict, key: str) -> int:
    """从单月 analysis_data 提取单项专项指标的发生次数。"""
    data = (analysis_data or {}).get(key, {}).get("data", [])
    return data[0].get("发生次数", 0) if data else 0


def _extract_month_num(bucket_label: str) -> int:
    """从 'N个月' 中提取数字 N 用于排序，未知排最后。"""
    m = re.search(r"(\d+)", str(bucket_label))
    return int(m.group(1)) if m else 9999


def _build_model_trend(months_data: list, analysis_key: str, top_n: int = 8) -> dict:
    """通用：构建 TOP-N 型号的多月推移数据。

    Args:
        months_data: 各月数据列表（含 analysis_data 字段）
        analysis_key: 分析结果 key，如 "analysis_3"（盖机TOP10）
        top_n: 取前 N 个型号

    Returns:
        包含 models/labels/datasets/table 的推移字典
    """
    labels = [m["month_label"] for m in months_data]

    # 跨月聚合，取总次数最多的 top_n 型号
    model_totals: dict = {}
    for m in months_data:
        for model, cnt in _get_top10_models(m.get("analysis_data"), analysis_key):
            model_totals[model] = model_totals.get(model, 0) + cnt
    top_models = sorted(model_totals.items(), key=lambda x: -x[1])[:top_n]

    trend = {
        "models": [m for m, _ in top_models],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["型号"] + labels, "rows": []},
    }
    for model, _ in top_models:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = next(
                (row.get("发生次数", 0)
                 for row in (ad or {}).get(analysis_key, {}).get("data", [])
                 if row.get("型号") == model),
                0,
            )
            counts.append(found)
        trend["datasets"].append({"model": model, "data": counts})
        trend["table"]["rows"].append({"label": model, "data": counts})

    return trend


def _build_parts_trend(months_data: list, sorted_key: str, raw_key: str, top_n: int = 8) -> tuple:
    """通用：构建 TOP-N 部品的多月推移数据（汇总 + 明细）。

    Args:
        months_data:  各月数据列表
        sorted_key:   已排序部品数据 key，如 "analysis_5"（盖机部品排序）
        raw_key:      未排序部品数据 key，如 "analysis_4"（盖机部品明细，用于型号明细表）
        top_n:        取前 N 个部品

    Returns:
        (parts_trend, parts_detail) 两个字典
    """
    labels = [m["month_label"] for m in months_data]

    # 跨月聚合，取总次数最多的 top_n 部品
    parts_totals: dict = {}
    for m in months_data:
        ad = m.get("analysis_data", {})
        for model_data in (ad or {}).get(sorted_key, {}).get("data", []):
            for part in model_data.get("TOP10部品", []):
                pname = part.get("配件", "")
                cnt = part.get("发生次数", 0)
                parts_totals[pname] = parts_totals.get(pname, 0) + cnt
    top_parts = sorted(parts_totals.items(), key=lambda x: -x[1])[:top_n]

    parts_trend = {
        "parts": [p for p, _ in top_parts],
        "labels": labels,
        "datasets": [],
        "table": {"columns": ["部品"] + labels, "rows": []},
    }
    for pname, _ in top_parts:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = sum(
                part.get("发生次数", 0)
                for model_data in (ad or {}).get(sorted_key, {}).get("data", [])
                for part in model_data.get("TOP10部品", [])
                if part.get("配件") == pname
            )
            counts.append(found)
        parts_trend["datasets"].append({"part": pname, "data": counts})
        parts_trend["table"]["rows"].append({"label": pname, "data": counts})

    # 明细：以最新月份的型号列表为基准，按月追踪每个型号的每个部品
    parts_detail = {"labels": labels, "models": []}
    latest_ad = months_data[-1].get("analysis_data", {}) if months_data else {}
    for model_data in (latest_ad or {}).get(raw_key, {}).get("data", []):
        model_name = model_data.get("型号", "")
        parts_info = []
        for part in model_data.get("TOP10部品", []):
            pname = part.get("配件", "")
            pcounts = []
            for m in months_data:
                ad = m.get("analysis_data", {})
                found = next(
                    (
                        pt.get("发生次数", 0)
                        for md2 in (ad or {}).get(raw_key, {}).get("data", [])
                        if md2.get("型号") == model_name
                        for pt in md2.get("TOP10部品", [])
                        if pt.get("配件") == pname
                    ),
                    0,
                )
                pcounts.append(found)
            parts_info.append({"name": pname, "data": pcounts})
        if parts_info:
            parts_detail["models"].append({"model": model_name, "parts": parts_info})

    return parts_trend, parts_detail


def build_trends(months_data: list) -> dict:
    """从各月 analysis_data 构建多维度推移数据。

    入参是 get_all_months_with_analysis() 的返回值（含 analysis_data 字段）。
    出参结构与原 _build_trends() 完全一致，保持 API 兼容。
    """
    labels = [m["month_label"] for m in months_data]

    # 1. 盖机保内 TOP10 型号推移
    cover_top10 = _build_model_trend(months_data, "analysis_3")

    # 2. 整机保内 TOP10 型号推移
    whole_top10 = _build_model_trend(months_data, "analysis_6")

    # 3. 盖机部品推移（汇总 + 明细）
    cover_parts, cover_parts_detail = _build_parts_trend(
        months_data, sorted_key="analysis_5", raw_key="analysis_4"
    )

    # 4. 整机部品推移（汇总 + 明细）
    whole_parts, whole_parts_detail = _build_parts_trend(
        months_data, sorted_key="analysis_8", raw_key="analysis_7"
    )

    # 5. 专项投诉推移（座盖 / 座盖软胶垫 / 柔光灯）
    special_datasets = [
        {
            "label": "保内座盖投诉",
            "data": [_get_special_count(m.get("analysis_data"), "analysis_9")
                     for m in months_data],
        },
        {
            "label": "保内座盖软胶垫投诉",
            "data": [_get_special_count(m.get("analysis_data"), "analysis_10")
                     for m in months_data],
        },
        {
            "label": "柔光灯投诉",
            "data": [_get_special_count(m.get("analysis_data"), "analysis_11")
                     for m in months_data],
        },
    ]
    special_trend = {
        "labels": labels,
        "datasets": special_datasets,
        "table": {
            "columns": ["指标"] + labels,
            "rows": [{"label": ds["label"], "data": ds["data"]}
                     for ds in special_datasets],
        },
    }

    # 6. 座盖故障使用月数推移
    usage_buckets_set: set = set()
    for m in months_data:
        ad = m.get("analysis_data", {})
        for row in (ad or {}).get("analysis_12", {}).get("data", []):
            bucket = row.get("使用月数区间", "")
            if bucket:
                usage_buckets_set.add(bucket)
    usage_buckets_order = sorted(usage_buckets_set, key=_extract_month_num)

    seat_usage_trend = {
        "labels": labels,
        "buckets": usage_buckets_order,
        "datasets": [],
        "table": {"columns": ["使用月数"] + labels, "rows": []},
    }
    for bucket in usage_buckets_order:
        counts = []
        for m in months_data:
            ad = m.get("analysis_data", {})
            found = next(
                (row.get("发生次数", 0)
                 for row in (ad or {}).get("analysis_12", {}).get("data", [])
                 if row.get("使用月数区间") == bucket),
                0,
            )
            counts.append(found)
        seat_usage_trend["datasets"].append({"bucket": bucket, "data": counts})
        seat_usage_trend["table"]["rows"].append({"label": bucket, "data": counts})

    return {
        "cover_top10": cover_top10,
        "whole_top10": whole_top10,
        "cover_parts": cover_parts,
        "whole_parts": whole_parts,
        "cover_parts_detail": cover_parts_detail,
        "whole_parts_detail": whole_parts_detail,
        "special": special_trend,
        "seat_usage": seat_usage_trend,
    }
