# -*- coding: utf-8 -*-
"""售后数据分析引擎 — 12 项单月分析 + 多月对比"""

import pandas as pd
import numpy as np
import re
import os
import json
from datetime import datetime
from collections import defaultdict


def parse_month_from_filename(filepath):
    """从文件名提取年月，支持多种格式：
    202509售后配件记录.xlsx → (2025, 9)
    2025年6月售后配件记录.xlsx → (2025, 6)
    2025-06售后记录.xlsx → (2025, 6)
    """
    basename = os.path.basename(filepath)
    # 尝试多种格式，按优先级依次匹配
    for pattern in (
        r"(\d{4})年(\d{1,2})月",   # "2025年6月"
        r"(\d{4})[-/](\d{1,2})",   # "2025-06" 或 "2025/6"
        r"(\d{4})(\d{2})",          # "202506" 紧凑格式
    ):
        m = re.search(pattern, basename)
        if m:
            return int(m.group(1)), int(m.group(2))
    return datetime.now().year, datetime.now().month


def normalize_date(val, year=None, month=None):
    """将反馈日期列的值标准化为完整日期字符串。

    Excel 中日期格式多样，特别处理以下格式：
    - datetime / Timestamp 对象 → 直接读取年月日
    - float/int 形如 9.1, 10.28（月.日）→ 提取月份和日，配合 year 生成完整日期
    - 字符串 "2025-09-01", "2025/09/01" 等完整格式
    - 字符串 "9-1", "9/1", "9月1日" 等月日格式（需要 year）
    """
    if pd.isna(val):
        return None
    try:
        # ① 已经是日期对象（Excel 自动解析）—— 包含完整年月日信息
        if isinstance(val, (datetime, pd.Timestamp)):
            return val.strftime("%Y-%m-%d")

        # ② 数字格式（如 9.1 表示9月1日，10.28 表示10月28日）
        if isinstance(val, (int, float, np.integer, np.floating)):
            fval = float(val)
            # 拆分整数部分（月）和小数部分（日）
            m_part = int(fval)              # 月份（如 9, 10）
            day_part = round((fval - m_part) * 100)  # 日（如 .01→1, .28→28）
            # 小数部分为0时，说明是如 "9.0" 或整数 "9"，无法确定日，用文件名兜底
            if day_part == 0:
                day_part = int(fval)  # 此时 fval 可能是纯日数（旧格式）
                if year and month:
                    # 当作纯日数处理（旧格式兼容）
                    return f"{year}-{month:02d}-{day_part:02d}"
                return None
            # 月.日格式：m_part 在 1-12，day_part 在 1-31
            if 1 <= m_part <= 12 and 1 <= day_part <= 31:
                y = year or datetime.now().year
                return f"{y}-{m_part:02d}-{day_part:02d}"
            # 超出范围时，当纯日数处理
            if year and month:
                return f"{year}-{month:02d}-{m_part:02d}"
            return None

        # ③ 字符串类型
        s = str(val).strip()
        if not s:
            return None
        # 先尝试完整日期格式
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        # 再尝试月日格式（需要 year 上下文）
        if year:
            for fmt in ("%m-%d", "%m/%d", "%m月%d日"):
                try:
                    dt = datetime.strptime(s, fmt)
                    dt = dt.replace(year=year)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        # 最后尝试纯数字字符串（月.日 格式的字符串版本，如 "10.28"）
        try:
            fval = float(s)
            return normalize_date(fval, year, month)
        except ValueError:
            pass
        return None
    except Exception:
        return None


def parse_first_time(val):
    """解析首次时间，返回 datetime 或 None"""
    if pd.isna(val):
        return None
    try:
        if isinstance(val, datetime):
            return val
        return pd.to_datetime(str(val), errors="coerce")
    except Exception:
        return None


def _find_col(df, candidates):
    """按候选名称列表查找列名，返回第一个匹配的"""
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in cols_lower:
            return cols_lower[key]
    # fallback: 模糊匹配
    for cand in candidates:
        key = cand.strip().lower()
        for ck, cv in cols_lower.items():
            if key in ck or ck in key:
                return cv
    return None


def load_and_prepare(filepath):
    """加载 Excel 并完成数据预处理（U/V 列）"""
    year, month = parse_month_from_filename(filepath)
    df = pd.read_excel(filepath)

    # 验证最少列数
    if df.shape[1] < 10:
        raise ValueError(f"文件列数不足（{df.shape[1]}列），至少需要10列数据")

    # 通过列名匹配关键列，兼容不同月份文件列顺序的细微差异
    col_date = _find_col(df, ["反馈日期"])
    col_first = _find_col(df, ["首次时间"])
    col_model = _find_col(df, ["型号", "产品型号"])
    col_unit = _find_col(df, ["盖机/整机", "盖机整机"])
    col_parts = _find_col(df, ["配件", "更换部品"])
    col_warranty = _find_col(df, ["保内保外", "保内/保外"])
    col_customer = _find_col(df, ["客户"])
    col_parts_fee = _find_col(df, ["部品费", "部品费用"])
    col_shipping = _find_col(df, ["运费", "快递费", "运输费"])
    col_tech_fee = _find_col(df, ["师傅费用", "人工费", "维修费"])

    if not col_date:
        col_date = df.columns[0]  # fallback: 第一列
    if not col_first:
        col_first = df.columns[6] if df.shape[1] > 6 else df.columns[-1]

    # U 列：标准化日期 — 两步策略
    # 第一步：传入文件名年份（无月份），让 normalize_date 自己从 月.日 数字中提取月份
    df["标准化日期"] = df[col_date].apply(lambda v: normalize_date(v, year))
    # 第二步：对于仍解析失败的行（纯整数日数等），用文件名年月兜底
    fallback_mask = df["标准化日期"].isna()
    if fallback_mask.any():
        df.loc[fallback_mask, "标准化日期"] = df.loc[fallback_mask, col_date].apply(
            lambda v: normalize_date(v, year, month)
        )
    df["标准化日期_dt"] = pd.to_datetime(df["标准化日期"], errors="coerce")

    # G 列首次时间
    df["首次时间_dt"] = df[col_first].apply(parse_first_time)

    # V 列：使用月数 = (反馈日期 - 首次时间).days / 30
    def calc_usage_months(row):
        d1 = row["标准化日期_dt"]
        d2 = row["首次时间_dt"]
        if pd.isna(d1) or pd.isna(d2):
            return None
        days = (d1 - d2).days
        if days < 0:
            return None
        return round(days / 30, 1)

    df["使用月数"] = df.apply(calc_usage_months, axis=1)

    # 费用相关（为避免误匹日期列，先用 pd.to_numeric 验证该列是否含数值）
    for col, name in [(col_parts_fee, "部品费"), (col_shipping, "运费"), (col_tech_fee, "师傅费用")]:
        src = col if col else df.columns[13] if df.shape[1] > 13 else df.columns[-3]
        # 如果匹配到的列全是日期类型，回退到位置索引
        if col and pd.api.types.is_datetime64_any_dtype(df[col]):
            src = df.columns[13] if df.shape[1] > 13 else df.columns[-3]
        df[name] = pd.to_numeric(df[src], errors="coerce").fillna(0)
    df["总费用"] = df["部品费"] + df["运费"] + df["师傅费用"]

    # 重命名关键列方便使用
    df["型号"] = df[col_model if col_model else df.columns[3]].astype(str).str.strip()
    df["盖机整机"] = df[col_unit if col_unit else df.columns[4]].astype(str).str.strip()
    df["保内保外"] = df[col_warranty if col_warranty else df.columns[9]].astype(str).str.strip()
    df["配件"] = df[col_parts if col_parts else df.columns[8]].astype(str).str.strip()
    df["客户"] = df[col_customer if col_customer else df.columns[10]].astype(str).str.strip() if col_customer or df.shape[1] > 10 else df["-"]

    title = f"{year}年{month}月售后费用"
    return df, year, month, title


# ============ 12 项分析函数 ============

def analysis_1_warranty_cost(df, title):
    """保修期内/外 + 整机/盖机 费用汇总"""
    groups = df.groupby(["保内保外", "盖机整机"])
    rows = []
    for (warranty, unit_type), g in groups:
        rows.append({
            "保内保外": warranty,
            "盖机整机": unit_type,
            "件数": len(g),
            "部品费合计": round(g["部品费"].sum(), 2),
            "运费合计": round(g["运费"].sum(), 2),
            "师傅费用合计": round(g["师傅费用"].sum(), 2),
            "总费用合计": round(g["总费用"].sum(), 2),
        })
    # 添加总计行
    rows.append({
        "保内保外": "合计",
        "盖机整机": "",
        "件数": len(df),
        "部品费合计": round(df["部品费"].sum(), 2),
        "运费合计": round(df["运费"].sum(), 2),
        "师傅费用合计": round(df["师傅费用"].sum(), 2),
        "总费用合计": round(df["总费用"].sum(), 2),
    })
    return {"title": title, "data": rows}


def analysis_2_usage_by_model(df, title):
    """使用月数 + 盖机/整机 + 产品型号 次数/费用汇总"""
    groups = df.groupby(["型号", "盖机整机"])
    rows = []
    for (model, unit_type), g in groups:
        usage = g["使用月数"].dropna()
        rows.append({
            "型号": model,
            "盖机整机": unit_type,
            "次数": len(g),
            "平均使用月数": round(usage.mean(), 1) if len(usage) > 0 else "-",
            "最小使用月数": round(usage.min(), 1) if len(usage) > 0 else "-",
            "最大使用月数": round(usage.max(), 1) if len(usage) > 0 else "-",
            "部品费合计": round(g["部品费"].sum(), 2),
            "总费用合计": round(g["总费用"].sum(), 2),
        })
    rows.sort(key=lambda r: r["次数"], reverse=True)
    return {"title": title, "data": rows}


def get_top10_models(df, unit_type, warranty):
    """获取指定类型 + 保修状态的 TOP10 型号"""
    mask = (df["盖机整机"] == unit_type) & (df["保内保外"] == warranty)
    sub = df[mask]
    top = sub.groupby("型号").size().sort_values(ascending=False).head(10)
    return sub[sub["型号"].isin(top.index)], top


def analysis_3_or_6_top10(df, unit_type, warranty, title):
    """(3) 盖机保内 / (6) 整机保内 TOP10 型号"""
    sub, top = get_top10_models(df, unit_type, warranty)
    rows = []
    for model, count in top.items():
        g = sub[sub["型号"] == model]
        rows.append({
            "排名": len(rows) + 1,
            "型号": model,
            "发生次数": count,
            "部品费合计": round(g["部品费"].sum(), 2),
            "运费合计": round(g["运费"].sum(), 2),
            "师傅费用合计": round(g["师傅费用"].sum(), 2),
            "总费用合计": round(g["总费用"].sum(), 2),
        })
    return {"title": title, "data": rows}


def analysis_4_or_7_top10_parts(df, unit_type, warranty, title):
    """(4) 盖机保内 / (7) 整机保内 TOP10 型号中各型号 TOP10 更换部品"""
    parts_order = ["配件", "发生次数", "占比", "部品费合计", "总费用合计"]
    sub, top = get_top10_models(df, unit_type, warranty)
    result = []
    for model, _ in top.items():
        g = sub[sub["型号"] == model]
        total = len(g)
        parts_count = g.groupby("配件").size().sort_values(ascending=False).head(10)
        parts_list = []
        for part, cnt in parts_count.items():
            pg = g[g["配件"] == part]
            ratio = round(cnt / total * 100, 1) if total > 0 else 0
            ratio_str = f"{int(ratio)}%" if ratio == int(ratio) else f"{ratio}%"
            row = {
                "配件": part,
                "发生次数": cnt,
                "占比": ratio_str,
                "部品费合计": round(pg["部品费"].sum(), 2),
                "总费用合计": round(pg["总费用"].sum(), 2),
            }
            parts_list.append({k: row[k] for k in parts_order})
        result.append({"型号": model, "总次数": total, "TOP10部品": parts_list})
    return {"title": title, "data": result, "_orderedColumns": parts_order}


def analysis_5_or_8_sorted_parts(df, unit_type, warranty, title):
    """(5) 盖机保内 / (8) 整机保内 TOP10 型号 → 各部品按次数排序"""
    parts_order = ["排名", "配件", "发生次数", "占比", "部品费合计", "总费用合计"]
    sub, top = get_top10_models(df, unit_type, warranty)
    result = []
    for model, _ in top.items():
        g = sub[sub["型号"] == model]
        total = len(g)
        parts_count = g.groupby("配件").size().sort_values(ascending=False).head(10)
        parts_list = []
        rank = 0
        for part, cnt in parts_count.items():
            rank += 1
            pg = g[g["配件"] == part]
            ratio = round(cnt / total * 100, 1) if total > 0 else 0
            ratio_str = f"{int(ratio)}%" if ratio == int(ratio) else f"{ratio}%"
            row = {
                "排名": rank,
                "配件": part,
                "发生次数": cnt,
                "占比": ratio_str,
                "部品费合计": round(pg["部品费"].sum(), 2),
                "总费用合计": round(pg["总费用"].sum(), 2),
            }
            parts_list.append({k: row[k] for k in parts_order})
        result.append({"型号": model, "总次数": total, "TOP10部品": parts_list})
    return {"title": title, "data": result, "_orderedColumns": parts_order}


def analysis_9_cover_seat(df, title):
    """盖机 + 保内 + 配件含"座盖"但不含"座盖软胶垫" """
    mask = (
        (df["盖机整机"] == "盖机") &
        (df["保内保外"] == "保内") &
        (df["配件"].str.contains("座盖", na=False)) &
        (~df["配件"].str.contains("座盖软胶垫", na=False))
    )
    sub = df[mask]
    return {
        "title": title,
        "data": [{"发生次数": len(sub), "部品费合计": round(sub["部品费"].sum(), 2),
                  "运费合计": round(sub["运费"].sum(), 2), "总费用合计": round(sub["总费用"].sum(), 2)}]
    }


def analysis_10_cover_seat_pad(df, title):
    """盖机 + 保内 + 配件含"座盖软胶垫" """
    mask = (
        (df["盖机整机"] == "盖机") &
        (df["保内保外"] == "保内") &
        (df["配件"].str.contains("座盖软胶垫", na=False))
    )
    sub = df[mask]
    return {
        "title": title,
        "data": [{"发生次数": len(sub), "部品费合计": round(sub["部品费"].sum(), 2),
                  "运费合计": round(sub["运费"].sum(), 2), "总费用合计": round(sub["总费用"].sum(), 2)}]
    }


def analysis_11_led_light(df, title):
    """盖机 + 配件含"柔光灯" """
    mask = (
        (df["盖机整机"] == "盖机") &
        (df["配件"].str.contains("柔光灯", na=False))
    )
    sub = df[mask]
    return {
        "title": title,
        "data": [{"发生次数": len(sub), "部品费合计": round(sub["部品费"].sum(), 2),
                  "运费合计": round(sub["运费"].sum(), 2), "总费用合计": round(sub["总费用"].sum(), 2)}]
    }


def _extract_month_num(bucket_label):
    """从 'N个月' 中提取数字 N 用于排序，未知排最后"""
    m = re.search(r'(\d+)', str(bucket_label))
    return int(m.group(1)) if m else 9999


def analysis_12_seat_usage_months(df, title):
    """盖机 + 配件含"座盖"不含"座盖软胶垫" + 按使用月数统计次数"""
    mask = (
        (df["盖机整机"] == "盖机") &
        (df["配件"].str.contains("座盖", na=False)) &
        (~df["配件"].str.contains("座盖软胶垫", na=False))
    )
    sub = df[mask].copy()
    sub["月数区间"] = sub["使用月数"].apply(
        lambda x: f"{int(x)}个月" if pd.notna(x) and x >= 0 else "未知"
    )
    counts = sub.groupby("月数区间").size()
    # 按数值排序：1, 2, 3, ..., 12, 未知
    sorted_items = sorted(counts.items(), key=lambda kv: _extract_month_num(kv[0]))
    rows = []
    for k, v in sorted_items:
        rows.append({"使用月数区间": k, "发生次数": v})
    return {"title": title, "data": rows}


def analysis_13_product_usage_summary(df, title):
    """所有产品使用月数整理：按保内/保外、整机/盖机、型号分类统计
    包含 1~24 个月逐月统计（四舍五入归桶）+ 3/4/5年汇总 + 合计校验
    """
    # 定义列顺序：基础列 → 逐月列 → 年份列 → 合计校验列
    base_cols = ["保内保外", "盖机整机", "型号", "件数", "平均使用月数", "最小使用月数", "最大使用月数"]
    month_cols = [f"{m}个月" for m in range(1, 25)]
    year_cols = ["3年(25~36月)", "4年(37~48月)", "大于4年"]
    verify_col = "月数合计"
    ordered_columns = base_cols + month_cols + year_cols + [verify_col]

    groups = df.groupby(["保内保外", "盖机整机", "型号"])
    rows = []
    for (warranty, unit, model), g in groups:
        usage = g["使用月数"].dropna()
        # 四舍五入取整归桶（<1月的统一归入1个月）
        usage_rounded = usage.round().clip(lower=1).astype(int)
        row = {
            "保内保外": warranty,
            "盖机整机": unit,
            "型号": model,
            "件数": len(g),
            "平均使用月数": round(usage.mean(), 1) if len(usage) > 0 else "-",
            "最小使用月数": round(usage.min(), 1) if len(usage) > 0 else "-",
            "最大使用月数": round(usage.max(), 1) if len(usage) > 0 else "-",
        }
        # 1~24 个月逐月统计（四舍五入归桶）
        month_total = 0
        for m in range(1, 25):
            cnt = int((usage_rounded == m).sum())
            row[f"{m}个月"] = cnt
            month_total += cnt
        # 第3年(25~36)、第4年(37~48)、第5年(49+)
        cnt_3y = int(((usage_rounded >= 25) & (usage_rounded <= 36)).sum())
        cnt_4y = int(((usage_rounded >= 37) & (usage_rounded <= 48)).sum())
        cnt_5y = int((usage_rounded > 48).sum())
        row["3年(25~36月)"] = cnt_3y
        row["4年(37~48月)"] = cnt_4y
        row["大于4年"] = cnt_5y
        month_total += cnt_3y + cnt_4y + cnt_5y
        row["月数合计"] = month_total
        # 重整 key 顺序：确保前端 Object.keys() 列序正确
        ordered_row = {col: row[col] for col in ordered_columns}
        rows.append(ordered_row)
    # 排序：保内优先 → 盖机优先 → 件数降序
    rows.sort(key=lambda r: (
        0 if r["保内保外"] == "保内" else 1,
        0 if r["盖机整机"] == "盖机" else 1,
        -r["件数"]
    ))
    return {"title": title, "data": rows, "_orderedColumns": ordered_columns}


def _build_summary(df, year, month):
    """从 DataFrame 构建汇总指标字典"""
    prefix = f"{year}年{month}月"
    return {
        "month_label": prefix,
        "year": year,
        "month": month,
        "total_records": int(len(df)),
        "total_cost": float(round(df["总费用"].sum(), 2)),
        "in_warranty_count": int(len(df[df["保内保外"] == "保内"])),
        "out_warranty_count": int(len(df[df["保内保外"] == "保外"])),
        "cover_count": int(len(df[df["盖机整机"] == "盖机"])),
        "whole_count": int(len(df[df["盖机整机"] == "整机"])),
    }


def _df_to_json(df):
    """将处理后的 DataFrame 转为 JSON 字符串（包含全部原始列+计算列，方便核对）"""
    sub = df.copy()
    # 转换时间列为字符串，避免 JSON 序列化报错
    for col in sub.columns:
        if pd.api.types.is_datetime64_any_dtype(sub[col]):
            sub[col] = sub[col].astype(str)
        # 内部辅助列加前缀 _ 标识
        if col in ("标准化日期_dt", "首次时间_dt"):
            # 保留但改名，避免与主列混淆
            pass
    # NaN → None
    sub = sub.where(sub.notna(), None)
    records = sub.to_dict(orient="records")
    return json.dumps(records, ensure_ascii=False, default=str)


# ==================== 分析标题多语言映射 ====================
_ANALYSIS_TITLES = {
    "zh-CN": [
        "售后费用", "各产品投诉的使用月数和售后情况",
        "盖机TOP10", "保内盖机TOP10", "保内盖机TOP10各TOP10部品",
        "整机TOP10", "保内整机TOP10", "保内整机TOP10各TOP10部品",
        "保内座盖投诉数量", "保内座盖软胶垫投诉数量", "柔光灯投诉数量",
        "座盖故障数量和使用月数", "所有产品使用月数汇总",
    ],
    "en": [
        "After-Sales Costs", "Usage Months & After-Sales by Product",
        "Cover Unit TOP10", "In-Warranty Cover Unit TOP10", "In-Warranty Cover Unit TOP10 Parts",
        "Complete Unit TOP10", "In-Warranty Complete Unit TOP10", "In-Warranty Complete Unit TOP10 Parts",
        "In-Warranty Seat Cover Complaints", "In-Warranty Seat Cover Pad Complaints", "Soft Light Complaints",
        "Seat Cover Failures & Usage Months", "All Products Usage Months Summary",
    ],
    "ja": [
        "アフターサービス費用", "製品別使用月数・アフターサービス状況",
        "カバーユニットTOP10", "保証内カバーユニットTOP10", "保証内カバーユニットTOP10部品",
        "一体型ユニットTOP10", "保証内一体型ユニットTOP10", "保証内一体型ユニットTOP10部品",
        "保証内シートカバークレーム", "保証内シートカバーパッドクレーム", "ソフトライトクレーム",
        "シートカバー故障数・使用月数", "全製品使用月数サマリー",
    ],
}


def _fmt_month_prefix(year, month, lang="zh-CN"):
    """按语言格式化月份前缀"""
    if lang == "en":
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        return f"{months[month-1]} {year}"
    # zh-CN / ja 都保持 "2025年9月" 格式
    return f"{year}年{month}月"


def _run_12_analyses(df, year, month, lang="zh-CN"):
    """对给定的 DataFrame 执行全部 12 项分析"""
    prefix = _fmt_month_prefix(year, month, lang)
    titles = _ANALYSIS_TITLES.get(lang, _ANALYSIS_TITLES["zh-CN"])
    sep = " " if lang == "en" else ""
    results = {}
    results["analysis_1"] = analysis_1_warranty_cost(df, f"{prefix}{sep}{titles[0]}")
    results["analysis_2"] = analysis_2_usage_by_model(df, f"{prefix}{sep}{titles[1]}")
    results["analysis_3"] = analysis_3_or_6_top10(df, "盖机", "保内", f"{prefix}{sep}{titles[2]}")
    results["analysis_4"] = analysis_4_or_7_top10_parts(df, "盖机", "保内", f"{prefix}{sep}{titles[3]}")
    results["analysis_5"] = analysis_5_or_8_sorted_parts(df, "盖机", "保内", f"{prefix}{sep}{titles[4]}")
    results["analysis_6"] = analysis_3_or_6_top10(df, "整机", "保内", f"{prefix}{sep}{titles[5]}")
    results["analysis_7"] = analysis_4_or_7_top10_parts(df, "整机", "保内", f"{prefix}{sep}{titles[6]}")
    results["analysis_8"] = analysis_5_or_8_sorted_parts(df, "整机", "保内", f"{prefix}{sep}{titles[7]}")
    results["analysis_9"] = analysis_9_cover_seat(df, f"{prefix}{sep}{titles[8]}")
    results["analysis_10"] = analysis_10_cover_seat_pad(df, f"{prefix}{sep}{titles[9]}")
    results["analysis_11"] = analysis_11_led_light(df, f"{prefix}{sep}{titles[10]}")
    results["analysis_12"] = analysis_12_seat_usage_months(df, f"{prefix}{sep}{titles[11]}")
    results["analysis_13"] = analysis_13_product_usage_summary(df, f"{prefix}{sep}{titles[12]}")
    return results


def detect_data_months(df):
    """从标准化日期列中检测数据覆盖了多少个不同月份。
    返回按时间排序的 [(year, month), ...] 列表。
    如果所有行日期无效，回退到文件名解析的月份。
    """
    if "标准化日期_dt" not in df.columns or df["标准化日期_dt"].isna().all():
        return []

    # 提取有效的年-月组合
    valid_dates = df["标准化日期_dt"].dropna()
    if len(valid_dates) == 0:
        return []

    month_series = valid_dates.dt.to_period("M")
    unique_months = sorted(month_series.unique())
    return [(p.year, p.month) for p in unique_months]


def split_by_month(df, year_col=None, month_col=None):
    """按数据中的实际年月拆分 DataFrame。
    优先使用标准化日期列提取的年月；fallback 用传入的 year/month。
    Returns: { (year, month): df_subset, ... }
    """
    if "标准化日期_dt" not in df.columns or df["标准化日期_dt"].isna().all():
        # fallback: 全部归入一个月份
        y = year_col or datetime.now().year
        m = month_col or datetime.now().month
        return {(y, m): df}

    df_copy = df.copy()
    valid = df_copy["标准化日期_dt"].notna()
    df_copy["_ym"] = df_copy["标准化日期_dt"].dt.to_period("M")

    groups = {}
    for period, g in df_copy.groupby("_ym", dropna=False):
        if pd.isna(period):
            continue
        ym = (period.year, period.month)
        groups[ym] = g.drop(columns=["_ym"])

    return groups


def run_all_analysis(filepath, lang="zh-CN"):
    """运行全部 12 项分析。自动检测多月份数据并拆分。
    Args:
        filepath: Excel 文件路径
        lang: 语言代码 (zh-CN / en / ja)，影响分析标题
    Returns:
        (df, combined_results, combined_summary, is_multi_month, month_details)
        month_details: None 或 [{"year": y, "month": m, "month_label": "...",
                                   "record_count": n, "summary": {...}, "results": {...}}, ...]
    """
    df, filename_year, filename_month, base_title = load_and_prepare(filepath)

    # 检测数据中的实际月份
    detected_months = detect_data_months(df)

    def _month_label(y, m):
        return _fmt_month_prefix(y, m, lang)

    # 如果检测到 ≤1 个有效月份，按原逻辑单月处理
    if len(detected_months) <= 1:
        # 优先使用数据中检测到的实际月份；无有效日期时回退到文件名月份
        filename_mismatch = False
        if len(detected_months) == 1:
            data_year, data_month = detected_months[0]
            # 检测文件名月份与数据月份是否一致
            if (data_year, data_month) != (filename_year, filename_month):
                filename_mismatch = True
            year, month = data_year, data_month
        else:
            year, month = filename_year, filename_month
        results = _run_12_analyses(df, year, month, lang)
        summary = _build_summary(df, year, month)
        summary["month_label"] = _month_label(year, month)
        # 将不一致信息附加到 summary 中传递给 app.py
        summary["filename_mismatch"] = filename_mismatch
        summary["filename_year"] = filename_year
        summary["filename_month"] = filename_month
        return df, results, summary, False, None
    year, month = filename_year, filename_month

    # -- 多月份处理 --
    month_groups = split_by_month(df, year, month)
    month_details = []

    for (y, m), df_sub in sorted(month_groups.items(), key=lambda x: x[0]):
        sub_results = _run_12_analyses(df_sub, y, m, lang)
        sub_summary = _build_summary(df_sub, y, m)
        sub_summary["month_label"] = _month_label(y, m)
        # 序列化处理后数据（选关键列，控制 JSON 体积）
        raw_records = _df_to_json(df_sub)
        month_details.append({
            "year": y,
            "month": m,
            "month_label": _month_label(y, m),
            "record_count": int(len(df_sub)),
            "summary": sub_summary,
            "results": sub_results,
            "raw_data_json": raw_records,
        })

    # 汇总全量（用整份数据跑一套，方便看总览）
    results = _run_12_analyses(df, year, month, lang)
    summary = _build_summary(df, year, month)
    # 覆盖 month_label 使其更清晰
    first_label = _month_label(detected_months[0][0], detected_months[0][1])
    last_label = _month_label(detected_months[-1][0], detected_months[-1][1])
    if lang == "en":
        summary["month_label"] = f"{first_label} ~ {last_label}"
    else:
        summary["month_label"] = f"{first_label} ~ {last_label}"
    summary["is_multi_month"] = True
    summary["month_count"] = len(month_details)

    return df, results, summary, True, month_details
