# -*- coding: utf-8 -*-
"""AI 智能分析引擎 — 从多月对比数据中识别趋势、异常、生成结论与建议
多语言支持：lang=zh / en / ja
"""

import json
import numpy as np

# ── 多语言文案字典 ──────────────────────────────────────────────────────────────
I18N_INSIGHTS = {
    "zh": {
        "data_not_enough": "数据不足（需要至少 2 个月的数据），无法进行趋势分析。",
        "summary_high_risk": "共发现 {high} 个高风险项、{medium} 个中风险项",
        "summary_medium_risk": "共发现 {medium} 个需关注的变化趋势",
        "summary_stable": "当前数据显示各项指标总体稳定",
        "summary_cost_trend": "总费用呈{direction}趋势（{chg:+.1f}%）",
        "summary_top_finding": "最突出问题是：{title}",
        "direction_up": "上升",
        "direction_down": "下降",

        # 基础指标
        "cost_surge_title": "📈 总费用大幅增长 {chg}%",
        "cost_surge_detail": "从 {label0} 的 ¥{cost0:,.0f} 增至 {label1} 的 ¥{cost1:,.0f}。{factors}",
        "factor_records_up": "售后件数同步增长",
        "factor_unit_cost_up": "单件维修成本可能上升",
        "alert_cost_rising": "总费用持续攀升",
        "alert_cost_detail": "近 {n} 个月总费用增长 {chg}%，建议关注费用构成中增幅最大的品类。",
        "finding_unit_cost_up": "⚠️ 件数平稳但费用上升 — 单件成本在增加",
        "finding_unit_cost_detail": "总费用增长 {chg}%，但件数仅变化 {records_chg}%，说明单件维修费用在上涨。建议排查部品费、运费、师傅费用各自变化。",
        "warranty_up": "保内占比显著上升",
        "warranty_up_detail": "保内件占比从 {r0}% 升至 {r1}%，可能意味着近期出货产品品质问题增多。建议按出厂批次做交叉分析。",
        "angle_warranty": "按出厂批次分析保内故障率",
        "angle_warranty_desc": "将当前售后数据按产品出厂日期分组，计算各批次在保修期内的故障率（次/台），识别高风险批次。",
        "angle_warranty_method": "分层分析 (Stratification)",
        "cover_ratio_up": "🔧 盖机故障占比上升",
        "cover_ratio_up_detail": "盖机占比从 {r0}% 升至 {r1}%，变化 {chg}%。座盖可能成为主要薄弱环节。",

        # 型号趋势
        "model_cover_surge": "🔧 盖机型号 [{model}] 故障数增长 {chg}%",
        "model_cover_surge_detail": "{model} 的盖机故障从 {d0} 次增至 {d1} 次（{chg:+.0f}%）。峰值出现在 {peak_month}（{peak_val}次）。建议排查该型号在对应批次的部品供应或装配工艺变化。",
        "alert_model_cover": "[{model}] 盖机故障数异常增长",
        "alert_model_cover_detail": "{model} 盖机故障数月环比波动较大，建议追溯对应出货批次的部品来源与工艺参数。",
        "model_cover_mild": "盖机型号 [{model}] 故障数小幅上升 {chg}%",
        "model_cover_mild_detail": "{model} 盖机故障从 {d0}→{d1} 次，趋势向上，建议持续关注。",
        "spike_cover": "⚠️ 盖机型号 [{model}] 在 {month} 出现异常峰值",
        "spike_cover_detail": "{model} 在 {month} 达到 {peak} 次（均值 {avg:.1f} 次），为正常水平的 {ratio:.0f} 倍。强烈建议核查该月份对应的客户投诉原始记录，确认是否为同一批次/同一生产日期的集中故障。",
        "model_whole_surge": "📦 整机型号 [{model}] 故障数增长 {chg}%",
        "model_whole_surge_detail": "{model} 整机故障从 {d0}→{d1} 次。建议优先分析 TOP 部品中增长最快的组件。",
        "alert_model_whole": "[{model}] 整机故障在 {month} 异常集中",
        "alert_model_whole_detail": "峰值 {peak} 次 / 均值 {avg:.1f} 次，需分析是否为特定部品导致。",
        "angle_model_whole": "对 {model} 进行专项品质分析",
        "angle_model_whole_desc": "{model} 是整机故障数最高的型号。建议展开 Pareto 分析，识别 TOP3 故障部品，并与设计图纸、供应商来料检验记录对照。",
        "angle_model_whole_method": "Pareto 分析 + 5Why 根本原因分析",

        # 部品趋势
        "part_surge": "{emoji} [{tag}] 部品「{part}」故障数增长 {chg}%",
        "part_surge_detail": "{part} 的故障次数从 {d0}→{d1}，增幅显著。这是 {tag} 领域故障增长最快的部品之一。建议：\n① 核查该部品的供应商来料批次是否有变更\n② 对比该部品在不同型号中的故障率，确认是否为通用性问题\n③ 查看该部品对应的客诉描述，确认故障模式（破损/变形/失效等）",
        "reco_part_supplier": "对「{part}」进行供应商来料专项检查",
        "reco_part_supplier_detail": "建议品质工程师针对 {part} 做以下动作：\n• 调取近3个月供应商出货检验报告\n• 现场确认来料检验标准与抽样方案\n• 必要时进行批次追溯和封样对比",
        "reco_category_supplier": "供应商管理",
        "angle_fmea": "对「{part}」进行失效模式分析 (FMEA)",
        "angle_fmea_desc": "{part} 是 {tag} 领域的高频故障部品，建议建立 FMEA 表，评估该部品在设计、材料、制造、安装各环节的风险优先级 (RPN)，并制定改善对策。",
        "angle_fmea_method": "FMEA（失效模式与影响分析）",
        "alert_part_spike": "部品「{part}」在 {month} 异常集中",
        "alert_part_spike_detail": "{month} 月发生 {peak} 次（均值 {avg:.1f}），可能是某一批次来料问题。",

        # 型号×部品交叉
        "model_part_surge": "⚠️ [{tag}] {model} 的「{part}」故障数增长 {chg}%",
        "model_part_surge_detail": "在 {tag} 领域，型号 {model} 的部品「{part}」故障从 {d0}→{d1} 次。这是一个型号-部品级别的精准预警，建议优先排查该型号该部品的生产与供应的变更点。",

        # 专项投诉
        "special_surge": "🎯 「{name}」投诉量增长 {chg}%",
        "special_surge_detail": "{label}从 {d0} 次增至 {d1} 次。座盖类投诉增长需要重点关注材质耐久性和用户使用场景。",
        "reco_seat_cushion": "座盖软胶垫材料回弹率测试",
        "reco_seat_cushion_detail": "建议品质工程师抽取近期出货的座盖样品，测试软胶垫在长期压缩后的回弹率，评估是否存在材料老化导致密闭性下降的问题。",
        "reco_category_material": "材料品质",
        "reco_seat_durability": "座盖整体结构耐久性验证",
        "reco_seat_durability_detail": "建议对投诉率高的型号的座盖进行加速老化测试（温湿度循环 + 开合耐久），确认疲劳寿命是否满足设计规格。",
        "reco_category_reliability": "可靠性测试",
        "alert_new_issue": "「{label}」从无到有，为新增问题",
        "alert_new_issue_detail": "前几个月该项投诉为 0，本月出现 {d1} 次，需确认是否为设计变更或新批次引入的问题。",

        # 使用月数模式
        "early_fault_title": "⚠️ 座盖早期故障（0-6月）数量上升",
        "early_fault_detail_prefix": "短期使用即发生故障的比例在增加：",
        "early_fault_detail_suffix": "。早期故障通常与制造缺陷或来料不良直接相关，而非正常磨损。强烈建议对近期投诉件做拆解分析，定位根本原因。",
        "reco_teardown": "对早期故障件做拆解分析 (Teardown Analysis)",
        "reco_teardown_detail": "• 收集近期 0-6 月内故障的座盖实物\n• 拆解确认故障部位（铰链/座圈/阻尼器/软胶垫）\n• 对比正常品与故障品的尺寸、硬度、外观差异\n• 输出根本原因报告并反馈研发",
        "reco_category_fault": "故障分析",
        "alert_seat_bucket": "座盖故障集中在 {bucket}",
        "alert_seat_bucket_detail": "使用 {bucket} 后故障明显增多，可能是设计寿命拐点，建议评估该区间的耐久性是否满足用户预期。",
    },

    "en": {
        "data_not_enough": "Insufficient data (at least 2 months required) for trend analysis.",
        "summary_high_risk": "Found {high} high-risk items and {medium} medium-risk items",
        "summary_medium_risk": "Found {medium} trends requiring attention",
        "summary_stable": "All indicators are generally stable",
        "summary_cost_trend": "Total cost shows {direction} trend ({chg:+.1f}%)",
        "summary_top_finding": "Most prominent issue: {title}",
        "direction_up": "upward",
        "direction_down": "downward",

        "cost_surge_title": "📈 Total cost increased by {chg}%",
        "cost_surge_detail": "From ¥{cost0:,.0f} in {label0} to ¥{cost1:,.0f} in {label1}. {factors}",
        "factor_records_up": "repair count increased in parallel",
        "factor_unit_cost_up": "unit repair cost may have risen",
        "alert_cost_rising": "Total cost continues to climb",
        "alert_cost_detail": "Total cost increased {chg}% over the past {n} months. Focus on the categories with the largest increase.",
        "finding_unit_cost_up": "⚠️ Stable repair count but rising cost — unit cost is increasing",
        "finding_unit_cost_detail": "Total cost increased {chg}%, but repair count changed only {records_chg}%, indicating rising unit repair cost. Investigate parts cost, shipping, and labor cost separately.",
        "warranty_up": "In-warranty ratio significantly increased",
        "warranty_up_detail": "In-warranty ratio rose from {r0}% to {r1}%, suggesting possible quality issues in recent shipments. Recommended: cross-analysis by factory shipment batch.",
        "angle_warranty": "Analyze in-warranty failure rate by shipment batch",
        "angle_warranty_desc": "Group current after-sales data by product factory date, calculate failure rate (count/unit) within warranty period for each batch, and identify high-risk batches.",
        "angle_warranty_method": "Stratification Analysis",
        "cover_ratio_up": "🔧 Cover machine failure ratio increased",
        "cover_ratio_up_detail": "Cover machine ratio rose from {r0}% to {r1}% ({chg}% change). Seat cover may be becoming the primary weak point.",

        "model_cover_surge": "🔧 Cover model [{model}] failures increased by {chg}%",
        "model_cover_surge_detail": "{model} cover failures increased from {d0} to {d1} ({chg:+.0f}%). Peak occurred in {peak_month} ({peak_val} times). Investigate parts supply or assembly process changes for the corresponding batch.",
        "alert_model_cover": "[{model}] Cover failures growing abnormally",
        "alert_model_cover_detail": "{model} cover failures show large month-over-month fluctuations. Trace back to parts sources and process parameters of the corresponding shipment batch.",
        "model_cover_mild": "Cover model [{model}] failures slightly increased by {chg}%",
        "model_cover_mild_detail": "{model} cover failures: {d0}→{d1}, trend is upward. Recommend continued monitoring.",
        "spike_cover": "⚠️ Cover model [{model}] abnormal spike in {month}",
        "spike_cover_detail": "{model} reached {peak} occurrences in {month} (avg {avg:.1f}), {ratio:.0f}x normal level. Strongly recommend checking original customer complaint records for that month to confirm if failures are concentrated in the same batch/production date.",
        "model_whole_surge": "📦 Whole-unit model [{model}] failures increased by {chg}%",
        "model_whole_surge_detail": "{model} whole-unit failures: {d0}→{d1}. Prioritize analysis of the fastest-growing components among TOP parts.",
        "alert_model_whole": "[{model}] Whole-unit failures concentrated in {month}",
        "alert_model_whole_detail": "Peak {peak} times / avg {avg:.1f} times. Need to analyze if specific parts are responsible.",
        "angle_model_whole": "Conduct specialized quality analysis on {model}",
        "angle_model_whole_desc": "{model} has the highest whole-unit failure count. Recommend Pareto analysis to identify TOP3 failing parts, and cross-check with design drawings and supplier incoming inspection records.",
        "angle_model_whole_method": "Pareto Analysis + 5Why Root Cause Analysis",

        "part_surge": "{emoji} [{tag}] Part [{part}] failures increased by {chg}%",
        "part_surge_detail": "{part} failure count: {d0}→{d1}, significant increase. This is one of the fastest-growing parts in the {tag} category. Recommendations:\n① Check if supplier incoming batch changed\n② Compare failure rate of this part across models to confirm if it is a common issue\n③ Review customer complaint descriptions for this part to confirm failure mode (breakage/deformation/failure, etc.)",
        "reco_part_supplier": "Conduct supplier incoming inspection on [{part}]",
        "reco_part_supplier_detail": "Recommend quality engineer to do the following for {part}:\n• Retrieve supplier shipment inspection reports for the past 3 months\n• On-site confirmation of incoming inspection standards and sampling plan\n• Batch traceability and sealed sample comparison if necessary",
        "reco_category_supplier": "Supplier Management",
        "angle_fmea": "Conduct Failure Mode Analysis (FMEA) on [{part}]",
        "angle_fmea_desc": "{part} is a high-frequency failing part in {tag}. Recommend building an FMEA table, assessing risk priority number (RPN) across design, material, manufacturing, and installation, and formulating improvement measures.",
        "angle_fmea_method": "FMEA (Failure Mode and Effects Analysis)",
        "alert_part_spike": "Part [{part}] abnormal concentration in {month}",
        "alert_part_spike_detail": "{peak} occurrences in {month} (avg {avg:.1f}), possibly due to a specific incoming batch issue.",

        "model_part_surge": "⚠️ [{tag}] {model} part [{part}] failures increased by {chg}%",
        "model_part_surge_detail": "In {tag} category, {model} part [{part}] failures: {d0}→{d1}. This is a model-part level precise warning. Prioritize checking production and supply change points for this model and part.",
        "special_surge": "🎯 [{name}] complaints increased by {chg}%",
        "special_surge_detail": "{label} increased from {d0} to {d1} times. Seat cover complaints need focus on material durability and user usage scenarios.",
        "reco_seat_cushion": "Seat cushion soft rubber pad resilience test",
        "reco_seat_cushion_detail": "Recommend quality engineer to sample recent seat cover shipments, test the resilience rate of soft rubber pads after long-term compression, and assess whether material aging causes sealing performance degradation.",
        "reco_category_material": "Material Quality",
        "reco_seat_durability": "Seat cover overall structure durability verification",
        "reco_seat_durability_detail": "Recommend accelerated aging test (temp/humidity cycling + open/close endurance) on seat covers with high complaint rates, to confirm whether fatigue life meets design specifications.",
        "reco_category_reliability": "Reliability Testing",
        "alert_new_issue": "[{label}] appeared from zero — new issue",
        "alert_new_issue_detail": "Previous months had 0 such complaints; this month had {d1} occurrences. Need to confirm if design changes or new batches introduced the issue.",

        "early_fault_title": "⚠️ Seat cover early failures (0-6 months) increasing",
        "early_fault_detail_prefix": "Proportion of failures after short-term use is increasing: ",
        "early_fault_detail_suffix": ". Early failures are usually directly related to manufacturing defects or incoming material issues, not normal wear. Strongly recommend teardown analysis on recent complaint units to identify root cause.",
        "reco_teardown": "Conduct teardown analysis on early failure units",
        "reco_teardown_detail": "• Collect seat cover units that failed within 0-6 months\n• Disassemble to confirm failure location (hinge/seat ring/damper/soft rubber pad)\n• Compare dimensions, hardness, appearance between normal and failed units\n• Output root cause report and feedback to R&D",
        "reco_category_fault": "Failure Analysis",
        "alert_seat_bucket": "Seat cover failures concentrated in {bucket}",
        "alert_seat_bucket_detail": "Failures明显增加 after {bucket} of use, possibly indicating design life inflection point. Recommend evaluating whether durability in this range meets user expectations.",
    },

    "ja": {
        "data_not_enough": "データが不足しています（最低2ヶ月のデータが必要です）。トレンド分析はできません。",
        "summary_high_risk": "高リスク項目 {high} 件、中リスク項目 {medium} 件を検出",
        "summary_medium_risk": "要注意トレンド {medium} 件を検出",
        "summary_stable": "現在のデータは全体的に安定しています",
        "summary_cost_trend": "総費用は{direction}傾向です（{chg:+.1f}%）",
        "summary_top_finding": "最も顕著な問題：{title}",
        "direction_up": "上昇",
        "direction_down": "下降",

        "cost_surge_title": "📈 総費用が {chg}% 大幅増加",
        "cost_surge_detail": "{label0} の ¥{cost0:,.0f} から {label1} の ¥{cost1:,.0f} に増加。{factors}",
        "factor_records_up": "修理件数が同期間で増加",
        "factor_unit_cost_up": "単位修理コストが上昇した可能性",
        "alert_cost_rising": "総費用が継続的に上昇",
        "alert_cost_detail": "過去{n}ヶ月で総費用が {chg}% 増加。費用構成の中で増加幅が最大のカテゴリに注目してください。",
        "finding_unit_cost_up": "⚠️ 件数は安定しているが費用が上昇 — 単価が増加中",
        "finding_unit_cost_detail": "総費用が {chg}% 増加しているが、件数はわずか {records_chg}% の変化。部品費、送料、作業員費用それぞれの変化を個別に確認してください。",
        "warranty_up": "保内比率が显著に上昇",
        "warranty_up_detail": "保内件数比率が {r0}% から {r1}% に上昇。最近出荷した製品の品質問題が増えている可能性があります。出荷ロットごとのクロス分析を推奨します。",
        "angle_warranty": "出荷ロット別に保内故障率を分析",
        "angle_warranty_desc": "現在のアフターサービスデータを製品出荷日でグループ化し、各ロットの保証期間内故障率（回/台）を計算して、高リスクロットを特定します。",
        "angle_warranty_method": "層別分析 (Stratification)",
        "cover_ratio_up": "🔧 カバー機故障比率が上昇",
        "cover_ratio_up_detail": "カバー機比率が {r0}% から {r1}% に上昇（{chg}% 変化）。シートカバーが主要な弱点になっている可能性があります。",

        "model_cover_surge": "🔧 カバー機型式 [{model}] の故障数が {chg}% 増加",
        "model_cover_surge_detail": "{model} のカバー機故障が {d0} 回から {d1} 回に増加（{chg:+.0f}%）。ピークは {peak_month}（{peak_val}回）。該当ロットの部品供給または組立工程の変更を確認してください。",
        "alert_model_cover": "[{model}] カバー機故障数が異常増加",
        "alert_model_cover_detail": "{model} カバー機故障数の月次変動が大きいです。該当出荷ロットの部品供給元と工程パラメータを追跡してください。",
        "model_cover_mild": "カバー機型式 [{model}] 故障数が小幅上昇 {chg}%",
        "model_cover_mild_detail": "{model} カバー機故障：{d0}→{d1} 回、上昇傾向にあります。継続的な監視を推奨します。",
        "spike_cover": "⚠️ カバー機型式 [{model}] が {month} に異常ピーク",
        "spike_cover_detail": "{model} が {month} に {peak} 回に達しました（平均 {avg:.1f} 回）、正常水準の {ratio:.0f} 倍です。その月の顧客苦情原始記録を強く推奨します。同一ロット・同一生産日の集中故障かを確認してください。",
        "model_whole_surge": "📦 本体型式 [{model}] 故障数が {chg}% 増加",
        "model_whole_surge_detail": "{model} 本体故障が {d0}→{d1} 回。TOP 部品の中で増加が最も速いコンポーネントを優先的に分析してください。",
        "alert_model_whole": "[{model}] 本体故障が {month} に集中",
        "alert_model_whole_detail": "ピーク {peak} 回 / 平均 {avg:.1f} 回。特定の部品が原因か分析が必要です。",
        "angle_model_whole": "{model} に対する専門品質分析を実施",
        "angle_model_whole_desc": "{model} は本体故障数が最多の型式です。Pareto 分析を展開して TOP3 故障部品を特定し、設計図面・サプライヤー入荷検査記録と照合することを推奨します。",
        "angle_model_whole_method": "Pareto 分析 + 5Why 根本原因分析",

        "part_surge": "{emoji} [{tag}] 部品「{part}」故障数が {chg}% 増加",
        "part_surge_detail": "{part} の故障回数が {d0}→{d1} に増加、增幅が显著です。これは {tag} 分野で最も速く増加している部品の一つです。推奨事項：\n① この部品のサプライヤー入荷ロットに変更がないか確認\n② この部品の異なる型式での故障率を比較し、汎用性問題か確認\n③ この部品に対応する苦情内容を確認し、故障モード（破損/変形/機能失效など）を確認",
        "reco_part_supplier": "「{part}」に対するサプライヤー入荷専門検査",
        "reco_part_supplier_detail": "品質エンジニアが {part} に対して以下を実施することを推奨：\n• 過去3ヶ月のサプライヤー出荷検査報告書を入手\n• 現場で入荷検査基準とサンプリング方案を確認\n• 必要に応じてロット追跡と封筒見本对比を実施",
        "reco_category_supplier": "サプライヤー管理",
        "angle_fmea": "「{part}」に対する故障モード分析 (FMEA)",
        "angle_fmea_desc": "{part} は {tag} 分野の高頻度故障部品です。FMEA 表を構築し、設計・材料・製造・取り付け各工程のリスク優先度数 (RPN) を評価し、改善対策を策定することを推奨します。",
        "angle_fmea_method": "FMEA（故障モードと影響分析）",
        "alert_part_spike": "部品「{part}」が {month} に異常集中",
        "alert_part_spike_detail": "{month} に {peak} 回発生（平均 {avg:.1f} 回）、特定の入荷ロット問題の可能性があります。",

        "model_part_surge": "⚠️ [{tag}] {model} の「{part}」故障数が {chg}% 増加",
        "model_part_surge_detail": "{tag} 分野で、型式 {model} の部品「{part}」故障が {d0}→{d1} 回に増加。これは型式・部品レベルの正確な予警です。該当型式・該当部品の生産と供給の変更点を優先的に確認してください。",
        "special_surge": "🎯 「{name}」苦情量が {chg}% 増加",
        "special_surge_detail": "{label} が {d0} 回から {d1} 回に増加。シートカバー類の苦情増加は材質耐久性及びユーザー使用シーンに注目する必要があります。",
        "reco_seat_cushion": "シートカバー軟質ゴムパッド材料回弾率テスト",
        "reco_seat_cushion_detail": "品質エンジニアが最近出荷したシートカバーサンプルを抽出し、軟質ゴムパッドの長期圧縮後の回弾率をテストして、材料老化による気密性低下問題が存在するか評価することを推奨します。",
        "reco_category_material": "材料品質",
        "reco_seat_durability": "シートカバー全体構造耐久性検証",
        "reco_seat_durability_detail": "苦情率が高い型式のシートカバーに対して加速老化テスト（温湿度サイクル + 開閉耐久）を実施し、疲労寿命が設計仕様を満足するか確認することを推奨します。",
        "reco_category_reliability": "信頼性テスト",
        "alert_new_issue": "「{label}」がゼロから出現 — 新規問題",
        "alert_new_issue_detail": "前数ヶ月は当該苦情が 0 でしたが、今月は {d1} 回発生しました。設計変更または新ロットで導入された問題か確認が必要です。",

        "early_fault_title": "⚠️ シートカバー早期故障（0-6ヶ月）数が上昇",
        "early_fault_detail_prefix": "短期使用で故障が発生する比率が増加中：",
        "early_fault_detail_suffix": "。早期故障は通常、製造欠陥または入荷不良に直接関連しており、正常な摩耗ではありません。最近の苦情件に対する分解分析を強く推奨し、根本原因を特定してください。",
        "reco_teardown": "早期故障件に対する分解分析 (Teardown Analysis) を実施",
        "reco_teardown_detail": "• 最近 0-6 ヶ月以内に故障したシートカバー実物を収集\n• 分解して故障部位（ヒンジ/シートリング/ダンパー/軟質ゴムパッド）を確認\n• 正常品と故障品の寸法・硬度・外観差異を对比\n• 根本原因報告書を出力して R&D にフィードバック",
        "reco_category_fault": "故障分析",
        "alert_seat_bucket": "シートカバー故障が {bucket} に集中",
        "alert_seat_bucket_detail": "{bucket} 使用後に故障が顯著に増加しています。設計寿命の転換点の可能性があるため、この区間の耐久性がユーザーの期待を満足するか評価することを推奨します。",
    },
}


def _safe_change_rate(old, new):
    """安全计算变化率"""
    if not old or old == 0:
        if new and new > 0:
            return 100.0
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


def _t(lang, key, **kwargs):
    """多语言文案快捷函数"""
    txt = I18N_INSIGHTS.get(lang, I18N_INSIGHTS["zh"]).get(key, key)
    try:
        return txt.format(**kwargs)
    except Exception:
        return txt


def generate_insights(comparison_data, lang="zh"):
    """
    基于多月对比数据，生成 AI 智能分析结论。

    Args:
        comparison_data: dict from get_comparison_data()
        lang: "zh" | "en" | "ja"

    Returns:
        dict: {
            "summary": str,
            "key_findings": [Finding],
            "risk_alerts": [Alert],
            "recommendations": [Reco],
            "analysis_angles": [Angle],
        }
    """
    # 语言兜底
    if lang not in I18N_INSIGHTS:
        lang = "zh"
    T = lambda key, **kw: _t(lang, key, **kw)

    details = comparison_data.get("details", [])
    trends = comparison_data.get("trends")
    labels = comparison_data.get("labels", [])
    n = len(labels)

    if n < 2:
        return {
            "summary": T("data_not_enough"),
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
            factors.append(T("factor_records_up"))
        else:
            factors.append(T("factor_unit_cost_up"))
        findings.append({
            "title": T("cost_surge_title", chg=cost_change),
            "detail": T("cost_surge_detail",
                         label0=labels[0], cost0=total_cost[0],
                         label1=labels[-1], cost1=total_cost[-1],
                         factors="、" + "".join(factors) if factors else ""),
            "severity": "high" if cost_change > 50 else "medium",
        })
        alerts.append({
            "title": T("alert_cost_rising"),
            "detail": T("alert_cost_detail", n=n, chg=cost_change),
            "level": "warning" if cost_change > 50 else "info",
        })

    if cost_change > 20 and records_change < 10:
        findings.append({
            "title": T("finding_unit_cost_up"),
            "detail": T("finding_unit_cost_detail", chg=cost_change, records_chg=records_change),
            "severity": "high",
        })

    # 保内占比趋势
    if len(in_warranty_ratio) >= 2:
        warranty_change = _safe_change_rate(in_warranty_ratio[0], in_warranty_ratio[-1])
        if warranty_change > 20:
            alerts.append({
                "title": T("warranty_up"),
                "detail": T("warranty_up_detail",
                             r0=in_warranty_ratio[0], r1=in_warranty_ratio[-1]),
                "level": "warning",
            })
            angles.append({
                "title": T("angle_warranty"),
                "description": T("angle_warranty_desc"),
                "method": T("angle_warranty_method"),
            })

    # 盖机占比
    if len(cover_ratio) >= 2:
        cover_change = _safe_change_rate(cover_ratio[0], cover_ratio[-1])
        if cover_change > 15:
            findings.append({
                "title": T("cover_ratio_up"),
                "detail": T("cover_ratio_up_detail",
                             r0=cover_ratio[0], r1=cover_ratio[-1], chg=cover_change),
                "severity": "medium",
            })

    # ========================================
    # 2. 型号级别趋势分析
    # ========================================
    if trends:
        _analyze_model_trends(trends, labels, n, findings, alerts, recommendations, angles, lang)
        _analyze_parts_trends(trends, labels, n, findings, alerts, recommendations, angles, lang)
        _analyze_special_trends(trends, findings, alerts, recommendations, lang)
        _analyze_usage_patterns(trends, findings, alerts, recommendations, lang)

    # ========================================
    # 3. 排名整理 & 总体摘要
    # ========================================
    findings.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("severity", "low"), 2))

    summary_parts = []
    high_count = sum(1 for f in findings if f.get("severity") == "high")
    medium_count = sum(1 for f in findings if f.get("severity") == "medium")

    if high_count > 0:
        summary_parts.append(T("summary_high_risk", high=high_count, medium=medium_count))
    elif medium_count > 0:
        summary_parts.append(T("summary_medium_risk", medium=medium_count))
    else:
        summary_parts.append(T("summary_stable"))

    if cost_change > 10:
        direction = T("direction_up") if cost_change > 0 else T("direction_down")
        summary_parts.append(T("summary_cost_trend", direction=direction, chg=cost_change))

    if findings:
        top_finding = findings[0]["title"]
        summary_parts.append(T("summary_top_finding", title=top_finding))

    summary = "。".join(summary_parts) + "。" if lang == "zh" else ". ".join(summary_parts) + "."

    findings = findings[:30]

    return {
        "summary": summary,
        "key_findings": findings,
        "risk_alerts": alerts,
        "recommendations": recommendations,
        "analysis_angles": angles,
        "generated_at": None,
    }


def _analyze_model_trends(trends, labels, n, findings, alerts, recommendations, angles, lang):
    """分析型号级别趋势"""
    T = lambda key, **kw: _t(lang, key, **kw)
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

            if chg > 50 and data[-1] >= 2:
                findings.append({
                    "title": T("model_cover_surge", model=model, chg=chg),
                    "detail": T("model_cover_surge_detail",
                                 model=model, d0=data[0], d1=data[-1], chg=chg,
                                 peak_month=labels[_max_idx(data)], peak_val=max_val),
                    "severity": "high" if chg > 100 and data[-1] >= 3 else "medium",
                })
                alerts.append({
                    "title": T("alert_model_cover", model=model),
                    "detail": T("alert_model_cover_detail", model=model),
                    "level": "warning" if chg > 100 else "info",
                })
            elif chg > 30 and data[-1] >= 3:
                findings.append({
                    "title": T("model_cover_mild", model=model, chg=chg),
                    "detail": T("model_cover_mild_detail",
                                 model=model, d0=data[0], d1=data[-1]),
                    "severity": "low",
                })

            if max_val >= 3 and max_val >= avg_val * 2:
                spike_month = labels[_max_idx(data)]
                findings.append({
                    "title": T("spike_cover", model=model, month=spike_month),
                    "detail": T("spike_cover_detail",
                                 model=model, month=spike_month,
                                 peak=max_val, avg=avg_val,
                                 ratio=max_val / max(avg_val, 0.1)),
                    "severity": "high",
                })

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
                    "title": T("model_whole_surge", model=model, chg=chg),
                    "detail": T("model_whole_surge_detail",
                                 model=model, d0=data[0], d1=data[-1]),
                    "severity": "high" if chg > 100 and data[-1] >= 3 else "medium",
                })

            max_val = max(data)
            avg_val = _mean(data)
            if max_val >= 3 and max_val >= avg_val * 2:
                spike_month = labels[_max_idx(data)]
                alerts.append({
                    "title": T("alert_model_whole", model=model, month=spike_month),
                    "detail": T("alert_model_whole_detail",
                                 peak=max_val, avg=avg_val),
                    "level": "warning",
                })

        if whole.get("datasets"):
            top_model = max(whole["datasets"], key=lambda d: sum(d.get("data", [])))
            if sum(top_model.get("data", [])) >= 5:
                angles.append({
                    "title": T("angle_model_whole", model=top_model['model']),
                    "description": T("angle_model_whole_desc", model=top_model['model']),
                    "method": T("angle_model_whole_method"),
                })


def _analyze_parts_trends(trends, labels, n, findings, alerts, recommendations, angles, lang):
    """分析部品级别趋势"""
    T = lambda key, **kw: _t(lang, key, **kw)
    tag_map = {"zh": "盖机", "en": "Cover", "ja": "カバー機"}
    tag_whole_map = {"zh": "整机", "en": "Whole-unit", "ja": "本体"}
    emoji_map = {"zh": "🔩", "en": "🔩", "ja": "🔩"}

    for category, tag_key, emoji_key in [
        ("cover_parts", "cover", "emoji_cover"),
        ("whole_parts", "whole", "emoji_whole"),
    ]:
        tag = tag_map.get(lang, "盖机") if "cover" in category else tag_whole_map.get(lang, "整机")
        emoji = "🔩" if "cover" in category else "⚙️"
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
                    "title": T("part_surge",
                                 emoji=emoji, tag=tag,
                                 part=part_name, chg=chg),
                    "detail": T("part_surge_detail",
                                 part=part_name, tag=tag,
                                 d0=data[0], d1=data[-1]),
                    "severity": "high" if chg > 150 and data[-1] >= 3 else "medium",
                })
                recommendations.append({
                    "title": T("reco_part_supplier", part=part_name),
                    "detail": T("reco_part_supplier_detail", part=part_name),
                    "category": T("reco_category_supplier"),
                })

            if any(d >= 5 for d in data):
                angles.append({
                    "title": T("angle_fmea", part=part_name),
                    "description": T("angle_fmea_desc", part=part_name, tag=tag),
                    "method": T("angle_fmea_method"),
                })

            if max_val >= 3 and max_val >= avg_val * 2.5:
                spike_month = labels[_max_idx(data)]
                alerts.append({
                    "title": T("alert_part_spike", part=part_name, month=spike_month),
                    "detail": T("alert_part_spike_detail",
                                 part=part_name, month=spike_month,
                                 peak=max_val, avg=avg_val),
                    "level": "warning",
                })

    # 部品型号交叉分析
    for detail_key, tag_key in [("cover_parts_detail", "cover"), ("whole_parts_detail", "whole")]:
        tag = tag_map.get(lang, "盖机") if "cover" in detail_key else tag_whole_map.get(lang, "整机")
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
                if chg > 80 and pdata[-1] >= 3:
                    findings.append({
                        "title": T("model_part_surge",
                                     tag=tag, model=model, part=pname, chg=chg),
                        "detail": T("model_part_surge_detail",
                                     tag=tag, model=model, part=pname,
                                     d0=pdata[0], d1=pdata[-1]),
                        "severity": "high" if chg > 150 else "medium",
                    })


def _analyze_special_trends(trends, findings, alerts, recommendations, lang):
    """分析专项投诉趋势"""
    T = lambda key, **kw: _t(lang, key, **kw)
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
            item_name = label.replace("保内", "").replace("投诉", "")\
                             .replace("In-warranty", "").replace("complaint", "")\
                             .replace("保内", "").replace("クレーム", "")
            findings.append({
                "title": T("special_surge", name=item_name, chg=chg),
                "detail": T("special_surge_detail", label=label, d0=data[0], d1=data[-1]),
                "severity": "medium" if chg <= 100 else "high",
            })
            if "软胶垫" in label or "cushion" in label.lower() or "クッション" in label:
                recommendations.append({
                    "title": T("reco_seat_cushion"),
                    "detail": T("reco_seat_cushion_detail"),
                    "category": T("reco_category_material"),
                })
            if ("座盖" in label or "seat" in label.lower()) and "软胶垫" not in label and "cushion" not in label.lower():
                recommendations.append({
                    "title": T("reco_seat_durability"),
                    "detail": T("reco_seat_durability_detail"),
                    "category": T("reco_category_reliability"),
                })

        if sum(data) > 0 and data[0] == 0 and data[-1] > 0:
            alerts.append({
                "title": T("alert_new_issue", label=label),
                "detail": T("alert_new_issue_detail", label=label, d1=data[-1]),
                "level": "warning",
            })


def _analyze_usage_patterns(trends, findings, alerts, recommendations, lang):
    """分析故障-使用月数模式"""
    T = lambda key, **kw: _t(lang, key, **kw)
    seat = trends.get("seat_usage")
    if not seat or not seat.get("datasets"):
        return

    early_increasing = False
    early_detail_parts = []

    for ds in seat["datasets"]:
        bucket = ds.get("bucket", "")
        data = ds.get("data", [])
        if len(data) < 2:
            continue
        if any(eb in bucket for eb in ["0-3", "0-6", "3-6"]):
            chg = _safe_change_rate(data[0] or 0, data[-1])
            if chg > 30 and data[-1] > 0:
                early_increasing = True
                early_detail_parts.append(
                    T("early_fault_detail_prefix").split("：")[0] + f"：{bucket}区间：{data[0]}→{data[-1]} 次（+{chg}%）"
                    if lang == "zh" else
                    f"{bucket}: {data[0]}→{data[-1]} times ({chg:+}%)"
                )

    if early_increasing:
        # 重构 early_detail 为中文冒号格式
        ed_zh = "；".join(
            f"{ds.get('bucket', '')}区间：{ds.get('data', [0, 0])[0]}→{ds.get('data', [0, 0])[-1]} 次"
            for ds in seat["datasets"]
            if any(eb in ds.get("bucket", "") for eb in ["0-3", "0-6", "3-6"])
            and _safe_change_rate((ds.get("data") or [0, 0])[0], (ds.get("data") or [0, 0])[-1]) > 30
        )
        findings.append({
            "title": T("early_fault_title"),
            "detail": T("early_fault_detail_prefix") + ed_zh + T("early_fault_detail_suffix") if lang == "zh"
                       else T("early_fault_detail_prefix") + " " + ed_zh + T("early_fault_detail_suffix"),
            "severity": "high",
        })
        recommendations.append({
            "title": T("reco_teardown"),
            "detail": T("reco_teardown_detail"),
            "category": T("reco_category_fault"),
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
                "title": T("alert_seat_bucket", bucket=bucket),
                "detail": T("alert_seat_bucket_detail", bucket=bucket),
                "level": "info",
            })
