# -*- coding: utf-8 -*-
"""
services/export_html.py — HTML 多月对比报告生成服务

职责：接收 get_comparison_data() 的输出，渲染并返回 HTML 报告文件路径。
与 Flask 和数据库无关，可单独测试。
"""

import json
import os
import tempfile
from datetime import datetime

from insights import generate_insights


# ── 工具 ──────────────────────────────────────────────────

def _tbl_html(tbl: dict) -> str:
    """将 {columns, rows} 格式的表格数据渲染为 HTML <table>。"""
    if not tbl:
        return ""
    cols = "".join(f"<th>{c}</th>" for c in tbl.get("columns", []))
    rows = "".join(
        f"<tr><td style='font-weight:600;text-align:left;'>{r['label']}</td>"
        + "".join(f"<td>{v or 0}</td>" for v in r["data"])
        + "</tr>"
        for r in tbl.get("rows", [])
    )
    return f"<table><thead><tr>{cols}</tr></thead><tbody>{rows}</tbody></table>"


def _chart_js(chart_id: str, chart_type: str, labels_js: str,
              datasets: list, label_key: str, data_key: str,
              colors: list) -> str:
    """生成 Chart.js 初始化代码（折线图 / 柱状图通用）。"""
    ds_list = []
    for i, ds in enumerate(datasets):
        color = colors[i % len(colors)]
        ds_list.append({
            "label": ds[label_key],
            "data": ds[data_key],
            "borderColor": color,
            "backgroundColor": "transparent" if chart_type == "line" else color,
            "tension": 0.3,
            "pointRadius": 3,
        })
    ds_json = json.dumps(ds_list)
    return (
        f"new Chart(document.getElementById('{chart_id}'), {{"
        f"type: '{chart_type}',"
        f"data: {{ labels: {labels_js}, datasets: {ds_json} }},"
        f"options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom',"
        f"  labels: {{ usePointStyle: true, padding: 20, font: {{ size: 11 }} }} }} }} }}"
        f"}});\n"
    )


def _build_trends_html(data: dict, labels_js: str) -> tuple:
    """构建推移图表的 HTML 片段和 JS 初始化代码。

    Returns:
        (trends_html, trends_js) 两个字符串
    """
    if not data.get("trends"):
        return "", ""

    t = data["trends"]
    colors = [
        "#2E75B6", "#e53e3e", "#38a169", "#d69e2e",
        "#805ad5", "#dd6b20", "#319795", "#d53f8c",
    ]

    trends_html = ""
    trends_js = ""

    def _add_line_card(chart_id: str, title: str, datasets: list,
                       label_key: str, data_key: str, tbl: dict) -> None:
        nonlocal trends_html, trends_js
        trends_js += _chart_js(chart_id, "line", labels_js, datasets,
                                label_key, data_key, colors)
        tbl_html = _tbl_html(tbl)
        trends_html += (
            f'<div class="card">'
            f'<div class="card-title">{title}</div>'
            f'<div style="height:320px;"><canvas id="{chart_id}"></canvas></div>'
            f'<div style="overflow-x:auto;margin-top:16px;">{tbl_html}</div>'
            f"</div>\n"
        )

    def _add_parts_detail(detail: dict, section_title: str) -> None:
        nonlocal trends_html
        if not detail or not detail.get("models"):
            return
        trends_html += (
            '<div style="margin-top:20px;padding-top:16px;border-top:2px solid #e2e8f0;">'
            f'<div style="font-weight:700;color:#1F4E79;font-size:15px;margin-bottom:12px;">'
            f"{section_title}</div>"
        )
        for mi in detail["models"]:
            trends_html += (
                f'<h4 style="color:#2E75B6;margin:12px 0 6px;">型号：{mi["model"]}</h4>'
                f'<table><thead><tr><th>部品</th>'
                + "".join(f"<th>{l}</th>" for l in detail["labels"])
                + "</tr></thead><tbody>"
            )
            for p in mi["parts"]:
                trends_html += (
                    f"<tr><td style='font-weight:500;'>{p['name']}</td>"
                    + "".join(f"<td>{v or 0}</td>" for v in p["data"])
                    + "</tr>"
                )
            trends_html += "</tbody></table>"
        trends_html += "</div>"

    # 盖机 TOP10
    _add_line_card("chartCoverTop10", "🔧 保内盖机 TOP10 型号推移",
                   t["cover_top10"]["datasets"], "model", "data",
                   t["cover_top10"].get("table"))

    # 整机 TOP10
    _add_line_card("chartWholeTop10", "📦 保内整机 TOP10 型号推移",
                   t["whole_top10"]["datasets"], "model", "data",
                   t["whole_top10"].get("table"))

    # 盖机部品汇总
    trends_js += _chart_js("chartCoverParts", "line", labels_js,
                            t["cover_parts"]["datasets"], "part", "data", colors)
    tbl_html = _tbl_html(t["cover_parts"].get("table"))
    trends_html += (
        '<div class="card">'
        '<div class="card-title">🔩 保内盖机 TOP10 部品推移（汇总）</div>'
        '<div style="height:320px;"><canvas id="chartCoverParts"></canvas></div>'
        f'<div style="overflow-x:auto;margin-top:16px;">{tbl_html}</div>'
    )
    _add_parts_detail(t.get("cover_parts_detail"), "📊 各型号 TOP10 部品明细")
    trends_html += "</div>\n"

    # 整机部品汇总
    trends_js += _chart_js("chartWholeParts", "line", labels_js,
                            t["whole_parts"]["datasets"], "part", "data", colors)
    tbl_html = _tbl_html(t["whole_parts"].get("table"))
    trends_html += (
        '<div class="card">'
        '<div class="card-title">⚙️ 保内整机 TOP10 部品推移（汇总）</div>'
        '<div style="height:320px;"><canvas id="chartWholeParts"></canvas></div>'
        f'<div style="overflow-x:auto;margin-top:16px;">{tbl_html}</div>'
    )
    _add_parts_detail(t.get("whole_parts_detail"), "📊 各型号 TOP10 部品明细")
    trends_html += "</div>\n"

    # 专项投诉推移
    special_colors = ["#e53e3e", "#d69e2e", "#805ad5"]
    sp_ds_list = [
        {
            "label": ds["label"], "data": ds["data"],
            "borderColor": special_colors[i],
            "backgroundColor": "transparent",
            "tension": 0.3, "pointRadius": 4, "borderWidth": 2,
        }
        for i, ds in enumerate(t["special"]["datasets"])
    ]
    trends_js += (
        f"new Chart(document.getElementById('chartSpecial'), {{"
        f"type: 'line',"
        f"data: {{ labels: {labels_js}, datasets: {json.dumps(sp_ds_list)} }},"
        f"options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom',"
        f"  labels: {{ usePointStyle: true, padding: 20, font: {{ size: 11 }} }} }} }} }}"
        f"}});\n"
    )
    tbl_html = _tbl_html(t["special"].get("table"))
    trends_html += (
        '<div class="card">'
        '<div class="card-title">🎯 专项投诉推移</div>'
        '<div style="height:280px;"><canvas id="chartSpecial"></canvas></div>'
        f'<div style="overflow-x:auto;margin-top:16px;">{tbl_html}</div>'
        "</div>\n"
    )

    # 座盖故障使用月数推移（柱状图）
    seat_ds_list = [
        {"label": ds["bucket"], "data": ds["data"],
         "backgroundColor": colors[i % len(colors)]}
        for i, ds in enumerate(t["seat_usage"]["datasets"])
    ]
    trends_js += (
        f"new Chart(document.getElementById('chartSeatUsage'), {{"
        f"type: 'bar',"
        f"data: {{ labels: {labels_js}, datasets: {json.dumps(seat_ds_list)} }},"
        f"options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom',"
        f"  labels: {{ usePointStyle: true, padding: 20, font: {{ size: 11 }} }} }} }} }}"
        f"}});\n"
    )
    tbl_html = _tbl_html(t["seat_usage"].get("table"))
    trends_html += (
        '<div class="card">'
        '<div class="card-title">🪑 座盖故障使用月数推移</div>'
        '<div style="height:320px;"><canvas id="chartSeatUsage"></canvas></div>'
        f'<div style="overflow-x:auto;margin-top:16px;">{tbl_html}</div>'
        "</div>\n"
    )

    return trends_html, trends_js


def _build_insights_html(data: dict, now: str) -> str:
    """构建 AI 智能分析结论的 HTML 片段。"""
    try:
        insights = generate_insights(data)
        insights["generated_at"] = now
    except Exception:
        return ""

    details = data.get("details", [])
    sei  = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    sc   = {"high": "#e53e3e", "medium": "#d69e2e", "low": "#38a169"}
    sbg  = {"high": "#fff5f5", "medium": "#fffff0", "low": "#f0fff4"}
    html = ""

    # 摘要
    if insights.get("summary"):
        html = (
            f'<div class="card" id="ai-summary"'
            f' style="background:linear-gradient(135deg,#1a365d,#2a4365);color:#fff;">'
            f'<div class="card-title" style="color:#bee3f8;border-left-color:#63b3ed;">🤖 AI 智能分析结论</div>'
            f'<div style="font-size:15px;line-height:1.8;opacity:0.95;">{insights["summary"]}</div>'
            f'<div style="font-size:11px;opacity:0.6;margin-top:12px;">'
            f'生成时间：{now} · 基于 {len(details)} 个月数据</div></div>'
        )

    # 关键发现
    if insights.get("key_findings"):
        items = "".join(
            f'<div class="insight-item" style="border-left:3px solid {sc.get(f.get("severity",""),"#718096")};'
            f'background:{sbg.get(f.get("severity",""),"#f7fafc")};padding:12px 16px;margin-bottom:8px;border-radius:4px;">'
            f'<div style="font-weight:700;font-size:14px;margin-bottom:4px;">'
            f'{sei.get(f.get("severity",""),"")}&nbsp;{f["title"]}</div>'
            f'<div style="font-size:13px;color:#4a5568;white-space:pre-line;">{f["detail"]}</div></div>'
            for f in insights["key_findings"]
        )
        html += (f'<div class="card" id="ai-findings">'
                 f'<div class="card-title">🔍 关键发现 ({len(insights["key_findings"])} 项)</div>'
                 f"{items}</div>")

    # 风险预警
    if insights.get("risk_alerts"):
        albg = {"warning": "#fffaf0", "info": "#ebf8ff"}
        albd = {"warning": "#fbd38d", "info": "#bee3f8"}
        slevel = {"warning": "⚠️ 预警", "info": "ℹ️ 关注"}
        items = "".join(
            f'<div style="padding:10px 14px;margin-bottom:6px;'
            f'background:{albg.get(a.get("level",""),"#f7fafc")};'
            f'border-radius:6px;border:1px solid {albd.get(a.get("level",""),"#e2e8f0")};">'
            f'<div style="font-weight:600;font-size:13px;">'
            f'{slevel.get(a.get("level",""),"")}&nbsp;{a["title"]}</div>'
            f'<div style="font-size:12px;color:#718096;margin-top:4px;">{a["detail"]}</div></div>'
            for a in insights["risk_alerts"]
        )
        html += (f'<div class="card" id="ai-alerts">'
                 f'<div class="card-title">🚨 风险预警 ({len(insights["risk_alerts"])} 项)</div>'
                 f"{items}</div>")

    # 改进建议
    if insights.get("recommendations"):
        items = "".join(
            f'<div style="padding:12px 16px;margin-bottom:8px;background:#f0fff4;'
            f'border-radius:6px;border:1px solid #c6f6d5;">'
            f'<div style="font-weight:700;font-size:14px;color:#276749;">✅&nbsp;{r["title"]}</div>'
            f'<div style="font-size:13px;color:#4a5568;margin-top:4px;white-space:pre-line;">{r["detail"]}</div>'
            f'<div style="font-size:11px;color:#a0aec0;margin-top:6px;">📂&nbsp;{r.get("category","")}</div></div>'
            for r in insights["recommendations"]
        )
        html += (f'<div class="card" id="ai-recommendations">'
                 f'<div class="card-title">💡 改进建议 ({len(insights["recommendations"])} 项)</div>'
                 f"{items}</div>")

    # 建议分析角度
    if insights.get("analysis_angles"):
        items = "".join(
            f'<div style="padding:10px 14px;margin-bottom:6px;background:#faf5ff;'
            f'border-radius:6px;border:1px solid #e9d8fd;">'
            f'<div style="font-weight:600;font-size:13px;color:#6b46c1;">📐&nbsp;{a["title"]}</div>'
            f'<div style="font-size:12px;color:#4a5568;margin-top:4px;">{a["description"]}</div>'
            f'<div style="font-size:11px;color:#a0aec0;margin-top:4px;">🔧&nbsp;方法：{a.get("method","")}</div></div>'
            for a in insights["analysis_angles"]
        )
        html += (f'<div class="card" id="ai-angles">'
                 f'<div class="card-title">🔬 建议分析角度 ({len(insights["analysis_angles"])} 项)</div>'
                 f"{items}</div>")

    return html


# ── HTML 模板 ──────────────────────────────────────────────

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>售后数据分析 — 多月对比报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "Microsoft YaHei", "PingFang SC", sans-serif;
       background: #f0f4f8; color: #2d3748; padding: 24px; }}
.header {{ text-align: center; padding: 32px;
           background: linear-gradient(135deg, #1F4E79, #2E75B6);
           color: #fff; border-radius: 12px; margin-bottom: 24px; }}
.header h1 {{ font-size: 24px; margin-bottom: 8px; }}
.header p  {{ opacity: 0.85; font-size: 14px; }}
.card {{ background: #fff; border-radius: 12px; padding: 24px;
         margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.card-title {{ font-size: 18px; font-weight: 700; color: #1F4E79;
               margin-bottom: 16px; padding-bottom: 8px;
               border-bottom: 2px solid #e2e8f0; }}
.charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px;
               margin-bottom: 16px; }}
.charts-row canvas {{ max-height: 300px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ background: #1F4E79; color: #fff; padding: 10px 12px;
      text-align: center; font-weight: 600; }}
td {{ padding: 10px 12px; text-align: center; border-bottom: 1px solid #e2e8f0; }}
tr:nth-child(even) td {{ background: #f7fafc; }}
tr:hover td {{ background: #ebf4ff; }}
.footer {{ text-align: center; color: #a0aec0; font-size: 12px; margin-top: 24px; }}
@media print {{ body {{ background: #fff; padding: 0; }}
                .card {{ box-shadow: none; break-inside: avoid; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>📊 售后数据分析 — 多月对比报告</h1>
  <p>生成时间：{now} | 数据范围：{range_start} ~ {range_end}（共 {month_count} 个月）</p>
</div>

<div class="card">
  <div class="card-title">📈 趋势图表</div>
  <div class="charts-row">
    <div><h4 style="text-align:center;margin-bottom:8px;color:#4a5568;">总记录数趋势</h4>
         <canvas id="chartRecords"></canvas></div>
    <div><h4 style="text-align:center;margin-bottom:8px;color:#4a5568;">总费用趋势 (¥)</h4>
         <canvas id="chartCost"></canvas></div>
  </div>
  <div class="charts-row">
    <div><h4 style="text-align:center;margin-bottom:8px;color:#4a5568;">保内占比趋势 (%)</h4>
         <canvas id="chartWarranty"></canvas></div>
    <div><h4 style="text-align:center;margin-bottom:8px;color:#4a5568;">盖机 / 整机对比</h4>
         <canvas id="chartUnitType"></canvas></div>
  </div>
</div>

<div class="card">
  <div class="card-title">📋 历月数据汇总</div>
  <table>
    <thead><tr>
      <th>月份</th><th>总记录数</th><th>总费用</th><th>保内件数</th><th>保外件数</th>
      <th>盖机件数</th><th>整机件数</th><th>保内占比</th><th>盖机占比</th>
    </tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
</div>

{insights_html}

{trends_html}

<div class="footer">
  <p>株式会社 Water X Technologies · 售后数据分析系统 · 自动生成</p>
</div>

<script>
const labels = {labels_js};
new Chart(document.getElementById('chartRecords'), {{
  type: 'bar',
  data: {{ labels, datasets: [{{ label: '总记录数', data: {records_js},
           backgroundColor: '#2E75B6' }}] }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});
new Chart(document.getElementById('chartCost'), {{
  type: 'line',
  data: {{ labels, datasets: [{{ label: '总费用(元)', data: {cost_js},
           borderColor: '#e53e3e', backgroundColor: 'rgba(229,62,62,0.1)',
           tension: 0.3, fill: true }}] }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});
new Chart(document.getElementById('chartWarranty'), {{
  type: 'line',
  data: {{ labels, datasets: [{{ label: '保内占比(%)', data: {warranty_js},
           borderColor: '#38a169', backgroundColor: 'rgba(56,161,105,0.1)',
           tension: 0.3, fill: true }}] }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});
new Chart(document.getElementById('chartUnitType'), {{
  type: 'bar',
  data: {{ labels, datasets: [
    {{ label: '盖机', data: {cover_counts}, backgroundColor: '#2E75B6' }},
    {{ label: '整机', data: {whole_counts}, backgroundColor: '#718096' }}
  ] }},
  options: {{ responsive: true }}
}});
{trends_js}
</script>
</body>
</html>
"""


def build_comparison_html(data: dict) -> str:
    """将多月对比数据渲染为 HTML 报告，保存到临时文件并返回文件路径。

    Args:
        data: get_comparison_data() 的返回值

    Returns:
        临时文件绝对路径
    """
    details = data["details"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    labels_js = json.dumps(data["labels"], ensure_ascii=False)

    # 汇总表格行
    table_rows = ""
    for i, d in enumerate(details):
        ratio = data["in_warranty_ratio"][i] if i < len(data["in_warranty_ratio"]) else 0
        cover_pct = data["cover_ratio"][i] if i < len(data["cover_ratio"]) else 0
        table_rows += (
            f"<tr>"
            f"<td>{d['month_label']}</td>"
            f"<td>{d['total_records']}</td>"
            f"<td>¥{d['total_cost']:,.0f}</td>"
            f"<td>{d['in_warranty_count']}</td>"
            f"<td>{d['out_warranty_count']}</td>"
            f"<td>{d['cover_count']}</td>"
            f"<td>{d['whole_count']}</td>"
            f"<td>{ratio}%</td>"
            f"<td>{cover_pct}%</td>"
            f"</tr>"
        )

    trends_html, trends_js = _build_trends_html(data, labels_js)
    insights_html = _build_insights_html(data, now)

    cover_counts = json.dumps([d["cover_count"] for d in details])
    whole_counts = json.dumps([d["whole_count"] for d in details])

    html = _HTML_TEMPLATE.format(
        now=now,
        range_start=data["labels"][0],
        range_end=data["labels"][-1],
        month_count=len(details),
        table_rows=table_rows,
        insights_html=insights_html,
        trends_html=trends_html,
        labels_js=labels_js,
        records_js=json.dumps(data["total_records"]),
        cost_js=json.dumps(data["total_cost"]),
        warranty_js=json.dumps(data["in_warranty_ratio"]),
        cover_counts=cover_counts,
        whole_counts=whole_counts,
        trends_js=trends_js,
    )

    temp_path = os.path.join(
        tempfile.gettempdir(), "after_sales_comparison.html"
    )
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(html)
    return temp_path
