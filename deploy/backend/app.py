# -*- coding: utf-8 -*-
"""Flask API — 售后数据分析后台（V2.0 重构版）

本文件只负责：路由注册 + 鉴权逻辑 + 请求/响应处理。
业务逻辑已拆分至：
  - analyzer.py        Excel 数据解析与 12 项分析
  - db.py              数据库读写
  - insights.py        AI 智能分析引擎
  - services/
      export_excel.py  Excel 报告生成
      export_html.py   HTML 多月对比报告生成
      trends.py        （由 db.py 内部调用）
"""

from datetime import datetime
from functools import wraps

from flask import Flask, jsonify, redirect, request, send_file, send_from_directory, session
from flask_cors import CORS

import config
from analyzer import _df_to_json, run_all_analysis
from db import (
    delete_month, get_all_months, get_comparison_data,
    get_month_detail, init_db, save_monthly, _to_native,
    kb_save, kb_list, kb_get, kb_delete,
)
from insights import generate_insights
from services.export_excel import build_monthly_excel
from services.export_html import build_comparison_html

import os
import db as _db_module

# ── 初始化 Flask ──────────────────────────────────────────
app = Flask(__name__, static_folder=config.STATIC_DIR, static_url_path="")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.secret_key = config.SECRET_KEY

# ── Session 配置：确保浏览器正确携带 session cookie ──
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",       # 同站请求携带 cookie（fetch 兼容）
    SESSION_COOKIE_HTTPONLY=True,        # 禁止 JS 读取 cookie（安全）
    SESSION_COOKIE_SECURE=False,         # HTTP 环境下无需 Secure（生产 HTTPS 时改为 True）
)
app.permanent_session_lifetime = 86400  # 24 小时

# 同步 db 模块使用统一配置的数据库路径
_db_module.DB_PATH = config.DB_PATH
if config.IS_FROZEN:
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)

# ── CORS ──────────────────────────────────────────────────
if config.CORS_ORIGINS.strip() == "*":
    CORS(app, supports_credentials=False, origins="*")
elif config.CORS_ORIGINS.strip():
    CORS(app, supports_credentials=True,
         origins=[o.strip() for o in config.CORS_ORIGINS.split(",")])
else:
    CORS(app, supports_credentials=True, origins=config.DEFAULT_CORS_ORIGINS)

# ── 上传目录 ──────────────────────────────────────────────
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# ── 数据库初始化 ──────────────────────────────────────────
init_db()


# ══════════════════════════════════════════════════════════
#  鉴权
# ══════════════════════════════════════════════════════════

def login_required(f):
    """登录验证装饰器：API 返回 401，页面重定向到登录页。"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "unauthorized", "redirect": "/login"}), 401
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


def _get_lang() -> str:
    """从请求中提取语言参数（query string 优先，其次 Header）。"""
    lang = request.args.get("lang") or request.headers.get("X-Lang") or "zh-CN"
    return lang if lang in ("zh-CN", "en", "ja") else "zh-CN"


# ══════════════════════════════════════════════════════════
#  页面路由
# ══════════════════════════════════════════════════════════

@app.route("/")
@app.route("/login")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ══════════════════════════════════════════════════════════
#  鉴权 API
# ══════════════════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    if data.get("password", "") == config.ACCESS_PASSWORD:
        session["logged_in"] = True
        session.permanent = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "密码错误"}), 401


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/check-auth", methods=["GET"])
def check_auth():
    return jsonify({"logged_in": bool(session.get("logged_in"))})


# ══════════════════════════════════════════════════════════
#  数据上传 & 月份管理
# ══════════════════════════════════════════════════════════

@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    """上传 Excel 并执行全部分析。自动检测多月份数据并拆分保存。"""
    if "file" not in request.files:
        return jsonify({"error": "未上传文件"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "文件名为空"}), 400

    lang = _get_lang()
    filepath = os.path.join(config.UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        df, results, summary, is_multi, month_details = run_all_analysis(filepath, lang=lang)
        existing_months = get_all_months()

        def _month_exists(y, m):
            return any(ex["year"] == y and ex["month"] == m for ex in existing_months)

        if is_multi and month_details:
            saved, already_exists = [], []
            for md in month_details:
                if _month_exists(md["year"], md["month"]):
                    already_exists.append({
                        "year": md["year"], "month": md["month"],
                        "month_label": md["month_label"],
                        "record_count": md["record_count"],
                        "summary": md["summary"],
                    })
                else:
                    save_monthly(md["year"], md["month"], md["month_label"],
                                 md["summary"], md["results"], md.get("raw_data_json"))
                    saved.append(md["month_label"])

            return jsonify({
                "success": True,
                "is_multi_month": True,
                "total_months_detected": len(month_details),
                "saved_months": saved,
                "already_exists_months": already_exists,
                "summary": summary,
                "results": _to_native(results),
                "month_details": [{
                    "year": md["year"], "month": md["month"],
                    "month_label": md["month_label"],
                    "record_count": md["record_count"],
                    "summary": md["summary"],
                } for md in month_details],
                "_month_results_for_overwrite": {
                    f"{md['year']}-{md['month']}": {
                        "summary": md["summary"],
                        "results": _to_native(md["results"]),
                        "raw_data_json": md.get("raw_data_json"),
                    }
                    for md in month_details if _month_exists(md["year"], md["month"])
                },
            })

        # ── 单月处理 ──
        filename_mismatch = summary.pop("filename_mismatch", False)
        filename_year     = summary.pop("filename_year", summary["year"])
        filename_month    = summary.pop("filename_month", summary["month"])
        raw_json          = _df_to_json(df)

        if filename_mismatch:
            return jsonify({
                "success": True, "is_multi_month": False,
                "already_exists": False, "filename_mismatch": True,
                "filename_year": filename_year, "filename_month": filename_month,
                "data_year": summary["year"], "data_month": summary["month"],
                "summary": summary, "results": _to_native(results),
                "raw_data_json": raw_json,
            })

        already = _month_exists(summary["year"], summary["month"])
        if already:
            return jsonify({
                "success": True, "is_multi_month": False,
                "already_exists": True,
                "summary": summary, "results": _to_native(results),
                "raw_data_json": raw_json,
            })

        save_monthly(summary["year"], summary["month"], summary["month_label"],
                     summary, results, raw_json)
        return jsonify({
            "success": True, "is_multi_month": False, "already_exists": False,
            "summary": summary, "results": _to_native(results),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/overwrite", methods=["POST"])
@login_required
def overwrite_month():
    """覆盖保存指定月份（在前端确认后调用）。"""
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "无数据"}), 400

    year, month = payload.get("year"), payload.get("month")
    month_label, summary  = payload.get("month_label"), payload.get("summary")
    results, raw_data_json = payload.get("results"), payload.get("raw_data_json")

    if not all([year, month, month_label, summary, results]):
        return jsonify({"error": "参数不完整"}), 400

    try:
        for m in get_all_months():
            if m["year"] == year and m["month"] == month:
                delete_month(m["id"])
                break
        save_monthly(year, month, month_label, summary, results, raw_data_json)
        return jsonify({"success": True, "month_label": month_label})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/months", methods=["GET"])
@login_required
def list_months():
    return jsonify({"months": get_all_months()})


@app.route("/api/months/<int:month_id>", methods=["GET"])
@login_required
def get_month(month_id):
    detail = get_month_detail(month_id)
    if not detail:
        return jsonify({"error": "未找到"}), 404
    return jsonify(detail)


@app.route("/api/months/<int:month_id>", methods=["DELETE"])
@login_required
def del_month(month_id):
    delete_month(month_id)
    return jsonify({"success": True})


@app.route("/api/comparison", methods=["GET"])
@login_required
def comparison():
    return jsonify(get_comparison_data())


# ══════════════════════════════════════════════════════════
#  导出
# ══════════════════════════════════════════════════════════

@app.route("/api/export/<int:month_id>", methods=["GET"])
@login_required
def export_excel(month_id):
    """导出单月分析结果为 Excel。"""
    detail = get_month_detail(month_id)
    if not detail:
        return jsonify({"error": "未找到"}), 404

    temp_path = build_monthly_excel(detail["month_label"], detail)
    return send_file(
        temp_path, as_attachment=True,
        download_name=f"{detail['month_label']}售后分析.xlsx",
    )


@app.route("/api/export/comparison-html", methods=["GET"])
@login_required
def export_comparison_html():
    """导出多月对比结果为 HTML 报告。"""
    data = get_comparison_data()
    if not data["details"]:
        return jsonify({"error": "暂无数据"}), 404

    temp_path = build_comparison_html(data)
    return send_file(
        temp_path, as_attachment=True,
        download_name=f"售后多月对比报告_{datetime.now().strftime('%Y%m%d')}.html",
        mimetype="text/html; charset=utf-8",
    )


# ══════════════════════════════════════════════════════════
#  知识库 API
# ══════════════════════════════════════════════════════════

@app.route("/api/knowledge/save", methods=["POST"])
@login_required
def kb_save_entry():
    """将指定月份的分析结果存入知识库（独立于月度数据，删除源数据后依然保留）。"""
    payload = request.get_json()
    if not payload:
        return jsonify({"error": "无数据"}), 400

    year = payload.get("year")
    month = payload.get("month")
    month_label = payload.get("month_label")
    summary = payload.get("summary")
    analysis_data = payload.get("analysis_data")
    raw_data_json = payload.get("raw_data_json")

    # ── 诊断日志 ──
    app.logger.info(f"[KB SAVE] 收到保存请求: year={year}, month={month}, month_label={month_label}, "
                    f"records={summary.get('total_records') if summary else 'N/A'}, "
                    f"cost={summary.get('total_cost') if summary else 'N/A'}")

    if not all([year, month, month_label, summary, analysis_data]):
        return jsonify({"error": "参数不完整"}), 400

    try:
        kb_save(year, month, month_label, summary, analysis_data, raw_data_json)
        app.logger.info(f"[KB SAVE] 保存成功: {month_label}")
        return jsonify({"success": True, "month_label": month_label})
    except Exception as e:
        app.logger.error(f"[KB SAVE] 保存失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/knowledge/list", methods=["GET"])
@login_required
def kb_list_entries():
    """列出知识库中所有条目（仅摘要信息）。"""
    return jsonify({"entries": kb_list()})


@app.route("/api/knowledge/<int:kb_id>", methods=["GET"])
@login_required
def kb_get_entry(kb_id):
    """获取知识库单条完整数据。"""
    entry = kb_get(kb_id)
    if not entry:
        return jsonify({"error": "未找到"}), 404
    return jsonify(entry)


@app.route("/api/knowledge/<int:kb_id>", methods=["DELETE"])
@login_required
def kb_delete_entry(kb_id):
    """删除知识库中的一条记录。"""
    kb_delete(kb_id)
    return jsonify({"success": True})


# ══════════════════════════════════════════════════════════
#  AI 分析 & 健康检查
# ══════════════════════════════════════════════════════════

@app.route("/api/analysis/insights", methods=["GET"])
def ai_insights():
    """AI 智能分析 — 从多月对比数据中识别趋势、异常、生成结论与建议。
    支持 ?lang=zh|en|ja 参数。
    """
    lang = request.args.get("lang", "zh")
    if lang not in ("zh", "en", "ja"):
        lang = "zh"

    data = get_comparison_data()
    if not data.get("details") or len(data["details"]) < 2:
        msgs = {
            "zh": "数据不足（需要至少 2 个月的数据），无法进行 AI 分析。",
            "en": "Insufficient data (at least 2 months required) for AI analysis.",
            "ja": "データが不足しています（最低2ヶ月のデータが必要です）。AI 分析はできません。",
        }
        return jsonify({
            "summary": msgs.get(lang, msgs["zh"]),
            "key_findings": [], "risk_alerts": [],
            "recommendations": [], "analysis_angles": [],
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    insights = generate_insights(data, lang=lang)
    insights["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return jsonify(insights)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "2.0"})


# ══════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=not config.IS_FROZEN)
