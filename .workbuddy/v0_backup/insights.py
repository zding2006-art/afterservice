# -*- coding: utf-8 -*-
"""AI 智能分析引擎 — 从多月对比数据中识别趋势、异常、生成结论与建议"""

import json
import numpy as np


def _safe_change_rate(old, new):
    """安全计算变化率"""
    if not old or old == 0:
        if new and new > 0:
            return 100.0  # 从零增长视为 100%
        return 0.0
    return round((new - old) / old * 100, 1)


def _mean(values):
    """均值"""
    v = [x for x in values if x is not None]
    if not v:
        return 0
    return sum(v) / len(v)


def _max_idx(values):
    """最大值所在索引"""
    return int(np.argmax(values))


def _min_idx(values):
    """最小值所在索引"""
    return int(np.argmin(values))


def generate_insights(comparison_data):
    """
    基于多月对比数据，生成 AI 智能分析结论。

    Returns:
        dict: {
            "summary": str,                    # 总体摘要
            "key_findings": [Finding],         # 关键发现（按严重程度排序）
            "risk_alerts": [Alert],            # 风险预警
            "recommendations": [Reco],         # 改进建议
            "analysis_angles": [Angle],        # 建议的分析角度
        }
    """
    details = comparison_data.get("details", [])
    trends = comparison_data.get("trends")
    labels = comparison_data.get("labels", [])
    n = len(labels)

    if n < 2:
        return {
            "summary": "数据不足（需要至少 2 个月的数据），无法进行趋势分析。",
            "key_findings": [],
            "risk_alerts": [],
            "recommendations": [],
            "analysis_angles": [],
        }

    findings = []
    alerts = []
    recommendations = []
    angles = []

    # ========================================
    # 1. 基础指标分析
    # ========================================
    total_records = comparison_data.get("total_records", [])
    total_cost = comparison_data.get("total_cost", [])
    in_warranty_ratio = comparison_data.get("in_warranty_ratio", [])
    cover_ratio = comparison_data.get("cover_ratio", [])

    # 费用趋势
    cost_change = _safe_change_rate(total_cost[0], total_cost[-1])
    records_change = _safe_change_rate(total_records[0], total_records[-1])

    if cost_change > 30:
        factors = []
        if records_change > 30:
            factors.append("售后件数同步增长")
        else:
            factors.append("单件维修成本可能上升")
        findings.append({
            "title": f"📈 总费用大幅增长 {cost_change}%",
            "detail": f"从 {labels[0]} 的 ¥{total_cost[0]:,.0f} 增至 {labels[-1]} 的 ¥{total_cost[-1]:,.0f}。" + "、".join(factors),
            "severity": "high" if cost_change > 50 else "medium",
        })
        alerts.append({
            "title": "总费用持续攀升",
            "detail": f"近 {n} 个月总费用增长 {cost_change}%，建议关注费用构成中增幅最大的品类。",
            "level": "warning" if cost_change > 50 else "info",
        })

    if cost_change > 20 and records_change < 10:
        findings.append({
            "title": "⚠️ 件数平稳但费用上升 — 单件成本在增加",
            "detail": f"总费用增长 {cost_change}%，但件数仅变化 {records_change}%，说明单件维修费用在上涨。建议排查部品费、运费、师傅费用各自变化。",
            "severity": "high",
        })

    # 保内占比趋势
    if len(in_warranty_ratio) >= 2:
        warranty_change = _safe_change_rate(in_warranty_ratio[0], in_warranty_ratio[-1])
        if warranty_change > 20:
            alerts.append({
                "title": "保内占比显著上升",
                "detail": f"保内件占比从 {in_warranty_ratio[0]}% 升至 {in_warranty_ratio[-1]}%，可能意味着近期出货产品品质问题增多。建议按出厂批次做交叉分析。",
                "level": "warning",
            })
            angles.append({
                "title": "按出厂批次分析保内故障率",
                "description": "将当前售后数据按产品出厂日期分组，计算各批次在保修期内的故障率（次/台），识别高风险批次。",
                "method": "分层分析 (Stratification)",
            })

    # 盖机占比
    if len(cover_ratio) >= 2:
        cover_change = _safe_change_rate(cover_ratio[0], cover_ratio[-1])
        if cover_change > 15:
            findings.append({
                "title": "🔧 盖机故障占比上升",
                "detail": f"盖机占比从 {cover_ratio[0]}% 升至 {cover_ratio[-1]}%，变化 {cover_change}%。座盖可能成为主要薄弱环节。",
                "severity": "medium",
            })

    # ========================================
    # 2. 型号级别趋势分析
    # ========================================
    if trends:
        _analyze_model_trends(trends, labels, n, findings, alerts, recommendations, angles)
        _analyze_parts_trends(trends, labels, n, findings, alerts, recommendations, angles)
        _analyze_special_trends(trends, findings, alerts, recommendations)
        _analyze_usage_patterns(trends, findings, alerts, recommendations)

    # ========================================
    # 3. 排名整理 & 总体摘要
    # ========================================
    findings.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 2))

    # 生成摘要（基于完整发现数量）
    summary_parts = []
    high_count = sum(1 for f in findings if f.get("severity") == "high")
    medium_count = sum(1 for f in findings if f.get("severity") == "medium")

    if high_count > 0:
        summary_parts.append(f"共发现 {high_count} 个高风险项、{medium_count} 个中风险项")
    elif medium_count > 0:
        summary_parts.append(f"共发现 {medium_count} 个需关注的变化趋势")
    else:
        summary_parts.append("当前数据显示各项指标总体稳定")

    if cost_change > 10:
        direction = "上升" if cost_change > 0 else "下降"
        summary_parts.append(f"总费用呈{direction}趋势（{cost_change:+.1f}%）")

    if findings:
        top_finding = findings[0]["title"].replace("📈 ", "").replace("⚠️ ", "").replace("🔧 ", "").replace("🔩 ", "")
        summary_parts.append(f"最突出问题是：{top_finding}")

    summary = "。".join(summary_parts) + "。"

    # 仅保留最有价值的发现用于展示（最多30项）
    findings = findings[:30]

    return {
        "summary": summary,
        "key_findings": findings,
        "risk_alerts": alerts,
        "recommendations": recommendations,
        "analysis_angles": angles,
        "generated_at": None,  # 由 API 端填充时间戳
    }


def _analyze_model_trends(trends, labels, n, findings, alerts, recommendations, angles):
    """分析型号级别趋势"""
    # 盖机 TOP10 型号
    cover = trends.get("cover_top10")
    if cover and cover.get("datasets"):
        for ds in cover["datasets"]:
            model = ds.get("model", "")
            data = ds.get("data", [])
            if len(data) < 2 or sum(data) == 0:
                continue
            chg = _safe_change_rate(data[0] or 0, data[-1])
            max_val = max(data)
            avg_val = _mean(data)

            # 检出增长 >50% 且在最近月份有实质数量的
            if chg > 50 and data[-1] >= 2:
                findings.append({
                    "title": f"🔧 盖机型号 [{model}] 故障数增长 {chg}%",
                    "detail": f"{model} 的盖机故障从 {data[0]} 次增至 {data[-1]} 次（{chg:+.0f}%）。"
                              f"峰值出现在 {labels[_max_idx(data)]}（{max_val}次）。建议排查该型号在对应批次的部品供应或装配工艺变化。",
                    "severity": "high" if chg > 100 and data[-1] >= 3 else "medium",
                })
                alerts.append({
                    "title": f"[{model}] 盖机故障数异常增长",
                    "detail": f"{model} 盖机故障数月环比波动较大，建议追溯对应出货批次的部品来源与工艺参数。",
                    "level": "warning" if chg > 100 else "info",
                })
            elif chg > 30 and data[-1] >= 3:
                findings.append({
                    "title": f"盖机型号 [{model}] 故障数小幅上升 {chg}%",
                    "detail": f"{model} 盖机故障从 {data[0]}→{data[-1]} 次，趋势向上，建议持续关注。",
                    "severity": "low",
                })

            # 检出骤增（单月 spike）
            if max_val >= 3 and max_val >= avg_val * 2:
                spike_month = labels[_max_idx(data)]
                findings.append({
                    "title": f"⚠️ 盖机型号 [{model}] 在 {spike_month} 出现异常峰值",
                    "detail": f"{model} 在 {spike_month} 达到 {max_val} 次（均值 {avg_val:.1f} 次），为正常水平的 {max_val/max(avg_val,0.1):.0f} 倍。"
                              f"强烈建议核查该月份对应的客户投诉原始记录，确认是否为同一批次/同一生产日期的集中故障。",
                    "severity": "high",
                })

    # 整机 TOP10 型号
    whole = trends.get("whole_top10")
    if whole and whole.get("datasets"):
        for ds in whole["datasets"]:
            model = ds.get("model", "")
            data = ds.get("data", [])
            if len(data) < 2 or sum(data) == 0:
                continue
            chg = _safe_change_rate(data[0] or 0, data[-1])

            if chg > 50 and data[-1] >= 2:
                findings.append({
                    "title": f"📦 整机型号 [{model}] 故障数增长 {chg}%",
                    "detail": f"{model} 整机故障从 {data[0]}→{data[-1]} 次。建议优先分析 TOP 部品中增长最快的组件。",
                    "severity": "high" if chg > 100 and data[-1] >= 3 else "medium",
                })

            max_val = max(data)
            avg_val = _mean(data)
            if max_val >= 3 and max_val >= avg_val * 2:
                spike_month = labels[_max_idx(data)]
                alerts.append({
                    "title": f"[{model}] 整机故障在 {spike_month} 异常集中",
                    "detail": f"峰值 {max_val} 次 / 均值 {avg_val:.1f} 次，需分析是否为特定部品导致。",
                    "level": "warning",
                })

        # 如果整机 Top1 型号在多个月份出现，建议深入分析
        if whole.get("datasets"):
            top_model = max(whole["datasets"], key=lambda d: sum(d.get("data", [])))
            if sum(top_model.get("data", [])) >= 5:
                angles.append({
                    "title": f"对 {top_model['model']} 进行专项品质分析",
                    "description": f"{top_model['model']} 是整机故障数最高的型号。建议展开 Pareto 分析，识别 TOP3 故障部品，"
                                   f"并与设计图纸、供应商来料检验记录对照。",
                    "method": "Pareto 分析 + 5Why 根本原因分析",
                })


def _analyze_parts_trends(trends, labels, n, findings, alerts, recommendations, angles):
    """分析部品级别趋势"""
    for category, tag, emoji in [
        ("cover_parts", "盖机", "🔩"),
        ("whole_parts", "整机", "⚙️"),
    ]:
        parts_trend = trends.get(category)
        if not parts_trend or not parts_trend.get("datasets"):
            continue

        for ds in parts_trend["datasets"]:
            part_name = ds.get("part", "")
            data = ds.get("data", [])
            if len(data) < 2 or sum(data) == 0:
                continue

            chg = _safe_change_rate(data[0] or 0, data[-1])
            max_val = max(data)
            avg_val = _mean(data)

            if chg > 80 and data[-1] >= 2:
                findings.append({
                    "title": f"{emoji} [{tag}] 部品「{part_name}」故障数增长 {chg}%",
                    "detail": f"{part_name} 的故障次数从 {data[0]}→{data[-1]}，增幅显著。"
                              f"这是 {tag} 领域故障增长最快的部品之一。建议：\n"
                              f"① 核查该部品的供应商来料批次是否有变更\n"
                              f"② 对比该部品在不同型号中的故障率，确认是否为通用性问题\n"
                              f"③ 查看该部品对应的客诉描述，确认故障模式（破损/变形/失效等）",
                    "severity": "high" if chg > 150 and data[-1] >= 3 else "medium",
                })
                recommendations.append({
                    "title": f"对「{part_name}」进行供应商来料专项检查",
                    "detail": f"建议品质工程师针对 {part_name} 做以下动作：\n"
                              f"• 调取近3个月供应商出货检验报告\n"
                              f"• 现场确认来料检验标准与抽样方案\n"
                              f"• 必要时进行批次追溯和封样对比",
                    "category": "供应商管理",
                })

            # 部品在总故障中的集中度
            if any(d >= 5 for d in data):
                angles.append({
                    "title": f"对「{part_name}」进行失效模式分析 (FMEA)",
                    "description": f"{part_name} 是 {tag} 领域的高频故障部品，建议建立 FMEA 表，评估该部品在"
                                   f"设计、材料、制造、安装各环节的风险优先级 (RPN)，并制定改善对策。",
                    "method": "FMEA（失效模式与影响分析）",
                })

            # 检出 spike
            if max_val >= 3 and max_val >= avg_val * 2.5:
                spike_month = labels[_max_idx(data)]
                alerts.append({
                    "title": f"部品「{part_name}」在 {spike_month} 异常集中",
                    "detail": f"{spike_month} 月发生 {max_val} 次（均值 {avg_val:.1f}），可能是某一批次来料问题。",
                    "level": "warning",
                })

    # 部品型号交叉分析：查找哪个型号的哪个部品增长最快
    for detail_key, tag in [("cover_parts_detail", "盖机"), ("whole_parts_detail", "整机")]:
        detail = trends.get(detail_key)
        if not detail or not detail.get("models"):
            continue
        for model_info in detail["models"]:
            model = model_info.get("model", "")
            for part in model_info.get("parts", []):
                pname = part.get("name", "")
                pdata = part.get("data", [])
                if len(pdata) < 2 or sum(pdata) == 0:
                    continue
                chg = _safe_change_rate(pdata[0] or 0, pdata[-1])
                # 过滤噪声：只有绝对数量达到阈值且增长率有意义时才报警
                if chg > 80 and pdata[-1] >= 3:
                    findings.append({
                        "title": f"⚠️ [{tag}] {model} 的「{pname}」故障数增长 {chg}%",
                        "detail": f"在 {tag} 领域，型号 {model} 的部品「{pname}」故障从 {pdata[0]}→{pdata[-1]} 次。"
                                  f"这是一个型号-部品级别的精准预警，建议优先排查该型号该部品的生产与供应的变更点。",
                        "severity": "high" if chg > 150 else "medium",
                    })


def _analyze_special_trends(trends, findings, alerts, recommendations):
    """分析专项投诉趋势"""
    special = trends.get("special")
    if not special or not special.get("datasets"):
        return

    for ds in special["datasets"]:
        label = ds.get("label", "")
        data = ds.get("data", [])
        if len(data) < 2:
            continue
        chg = _safe_change_rate(data[0] or 0, data[-1])
        if chg > 50 and data[-1] > 0:
            item_name = label.replace("保内", "").replace("投诉", "")
            findings.append({
                "title": f"🎯 「{item_name}」投诉量增长 {chg}%",
                "detail": f"{label}从 {data[0]} 次增至 {data[-1]} 次。座盖类投诉增长需要重点关注材质耐久性和用户使用场景。",
                "severity": "medium" if chg <= 100 else "high",
            })
            if "软胶垫" in label:
                recommendations.append({
                    "title": "座盖软胶垫材料回弹率测试",
                    "detail": "建议品质工程师抽取近期出货的座盖样品，测试软胶垫在长期压缩后的回弹率，"
                             "评估是否存在材料老化导致密闭性下降的问题。",
                    "category": "材料品质",
                })
            if "座盖" in label and "软胶垫" not in label:
                recommendations.append({
                    "title": "座盖整体结构耐久性验证",
                    "detail": "建议对投诉率高的型号的座盖进行加速老化测试（温湿度循环 + 开合耐久），"
                             "确认疲劳寿命是否满足设计规格。",
                    "category": "可靠性测试",
                })

        # 零值变有值的预警
        if sum(data) > 0 and data[0] == 0 and data[-1] > 0:
            alerts.append({
                "title": f"「{label}」从无到有，为新增问题",
                "detail": f"前几个月该项投诉为 0，本月出现 {data[-1]} 次，需确认是否为设计变更或新批次引入的问题。",
                "level": "warning",
            })


def _analyze_usage_patterns(trends, findings, alerts, recommendations):
    """分析故障-使用月数模式"""
    seat = trends.get("seat_usage")
    if not seat or not seat.get("datasets"):
        return

    # 检查早期故障（0-6月）是否在增加
    early_buckets = ["0-3月", "3-6月", "4-6月", "0-6月"]
    early_increasing = False
    early_detail = []

    for ds in seat["datasets"]:
        bucket = ds.get("bucket", "")
        data = ds.get("data", [])
        if len(data) < 2:
            continue
        if any(eb in bucket for eb in ["0-3", "0-6", "3-6"]):
            chg = _safe_change_rate(data[0] or 0, data[-1])
            if chg > 30 and data[-1] > 0:
                early_increasing = True
                early_detail.append(f"{bucket}区间：{data[0]}→{data[-1]} 次（+{chg}%）")

    if early_increasing:
        findings.append({
            "title": "⚠️ 座盖早期故障（0-6月）数量上升",
            "detail": "短期使用即发生故障的比例在增加：" + "；".join(early_detail) +
                      "。早期故障通常与制造缺陷或来料不良直接相关，而非正常磨损。"
                      "强烈建议对近期投诉件做拆解分析，定位根本原因。",
            "severity": "high",
        })
        recommendations.append({
            "title": "对早期故障件做拆解分析 (Teardown Analysis)",
            "detail": "• 收集近期 0-6 月内故障的座盖实物\n"
                      "• 拆解确认故障部位（铰链/座圈/阻尼器/软胶垫）\n"
                      "• 对比正常品与故障品的尺寸、硬度、外观差异\n"
                      "• 输出根本原因报告并反馈研发",
            "category": "故障分析",
        })

    # 检查是否存在特定使用月数区间的异常集中
    for ds in seat["datasets"]:
        data = ds.get("data", [])
        bucket = ds.get("bucket", "")
        if len(data) < 2:
            continue
        avg_val = _mean(data)
        max_val = max(data)
        if avg_val > 0 and max_val >= 3 and max_val >= avg_val * 2:
            alerts.append({
                "title": f"座盖故障集中在 {bucket}",
                "detail": f"使用 {bucket} 后故障明显增多，可能是设计寿命拐点，建议评估该区间的耐久性是否满足用户预期。",
                "level": "info",
            })
