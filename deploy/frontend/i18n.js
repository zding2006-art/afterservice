/**
 * 售后数据分析系统 — 多语言支持 (zh-CN / en / ja)
 * 浏览器自动检测 + localStorage 持久化 + 手动切换
 */
const I18N = {
  current: 'zh-CN',

  // ==================== 翻译字典 ====================
  dict: {
    'zh-CN': {
      // 页面标题
      'app.title': '售后数据分析后台',
      'app.subtitle': '客户投诉部品记录分析系统',
      'app.running': '系统运行中',
      'app.version': 'Version 1.2',
      // Tab 导航
      'tab.upload': '上传分析',
      'tab.monthly': '各月数据',
      'tab.comparison': '多月对比',
      'tab.knowledge': '知识库',
      // 上传页
      'upload.title': '上传月度售后数据',
      'upload.dropText': '点击或拖拽 Excel 文件到此处',
      'upload.formatHint': '支持 .xlsx 格式 · 文件名需包含年月 · 自动检测含多月份数据并拆分保存',
      'upload.analyzing': '正在分析数据...',
      'upload.detected': '检测到',
      'upload.months': '个月份',
      'upload.saved': '已保存',
      'upload.exists': '已存在（待确认）',
      'upload.detectedLabel': '检测到月份数',
      'upload.savedLabel': '已保存',
      'upload.existsLabel': '已有数据',
      'upload.overview': '各月数据概览',
      'upload.multiTitle': '多月份数据上传结果',
      'upload.summaryTitle': '汇总指标',
      // 汇总指标
      'summary.totalRecords': '总记录数',
      'summary.totalCost': '总费用',
      'summary.inWarranty': '保内件数',
      'summary.outWarranty': '保外件数',
      'summary.coverCount': '盖机件数',
      'summary.wholeCount': '整机件数',
      'summary.costUnit': '¥',
      // 多月对比
      'comparison.title': '月度总览',
      'comparison.table': '历月数据汇总表',
      'comparison.recordsTrend': '总记录数趋势',
      'comparison.costTrend': '总费用趋势 (¥)',
      'comparison.warrantyTrend': '保内占比趋势 (%)',
      'comparison.unitCompare': '盖机 / 整机对比',
      'comparison.colMonth': '月份',
      'comparison.colRecords': '总记录数',
      'comparison.colCost': '总费用(元)',
      'comparison.colInWarranty': '保内件数',
      'comparison.colOutWarranty': '保外件数',
      'comparison.colCover': '盖机件数',
      'comparison.colWhole': '整机件数',
      'comparison.colRatio': '保内占比',
      'comparison.empty': '暂无多月数据，需至少上传2个月数据后进行对比',
      'comparison.download': '下载对比报告 (HTML)',
      'comparison.coverTop10': '保内盖机 TOP10 型号推移',
      'comparison.wholeTop10': '保内整机 TOP10 型号推移',
      'comparison.coverParts': '保内盖机 TOP10 部品推移',
      'comparison.wholeParts': '保内整机 TOP10 部品推移',
      'comparison.partsDetail': '各型号 TOP10 部品明细',
      'comparison.special': '专项投诉推移',
      'comparison.seatUsage': '座盖故障使用月数推移',
      'comparison.recordsTrend': '总记录数趋势',
      'comparison.costTrend': '总费用趋势 (¥)',
      'comparison.warrantyTrend': '保内占比趋势 (%)',
      'comparison.unitCompare': '盖机 / 整机对比',
      // 各月数据
      'monthly.title': '已存储月份',
      'monthly.view': '查看',
      'monthly.export': '导出Excel',
      'monthly.delete': '删除',
      'monthly.records': '记录',
      'monthly.uploadedAt': '上传于',
      'monthly.empty': '暂无数据，请先上传月度报表',
      // 按钮
      'btn.confirm': '确认',
      'btn.cancel': '取消',
      'btn.save': '保存',
      'btn.close': '关闭',
      // Toast 消息
      'toast.uploadSuccess': '分析完成！数据已保存',
      'toast.uploadFail': '上传失败',
      'toast.deleteConfirm': '确定删除该月份数据？此操作不可撤销。',
      'toast.deleted': '已删除',
      'toast.cancelled': '已取消，数据未保存',
      'toast.savedByDate': '已按记录时间保存',
      'toast.overwritten': '已覆盖保存',
      'toast.allOverwritten': '个月份已全部覆盖保存',
      'toast.partialOverwritten': '完成',
      'toast.success': '成功',
      'toast.fail': '失败',
      'toast.keepOriginal': '已取消，原有数据保留',
      'toast.downloading': '对比报告下载中...',
      'toast.viewFail': '查看失败',
      'toast.deleteFail': '删除失败',
      'toast.loadFail': '加载失败',
      'toast.overwriteFail': '覆盖失败',
      // 确认对话框
      'modal.exists.title': '数据已存在',
      'modal.exists.body': '的数据已存在于数据库中。是否覆盖保存？覆盖后原有数据将被替换。',
      'modal.exists.cancel': '取消，保留原数据',
      'modal.exists.overwrite': '覆盖保存',
      'modal.multiExists.title': '以下月份数据已存在',
      'modal.multiExists.hint': '是否覆盖上述月份的数据？新数据将替换原有记录。',
      'modal.multiExists.cancel': '取消，保留原数据',
      'modal.multiExists.overwrite': '全部覆盖',
      'modal.mismatch.title': '文件名与记录时间不一致',
      'modal.mismatch.filename': '文件名',
      'modal.mismatch.dataDate': '记录时间',
      'modal.mismatch.hint': '系统将依据记录时间处理并保存数据。确认继续？',
      'modal.mismatch.no': 'No，放弃保存',
      'modal.mismatch.yes': 'Yes，按记录时间保存',
      // AI 分析
      'ai.summary': 'AI 智能分析结论',
      'ai.findings': '关键发现',
      'ai.alerts': '风险预警',
      'ai.recommendations': '改进建议',
      'ai.angles': '建议分析角度',
      'ai.alertWarning': '预警',
      'ai.alertInfo': '关注',
      'ai.generatedAt': '生成时间',
      'ai.autoAnalysis': 'AI 自动分析',
      'ai.insufficient': '数据不足（需要至少 2 个月的数据），无法进行 AI 分析。',
      // 状态
      'status.pendingOverwrite': '待确认覆盖',
      'status.saved': '已保存',
      // 列名
      'col.rank': '排名',
      'col.model': '型号',
      'col.unitType': '盖机整机',
      'col.warranty': '保内保外',
      'col.count': '件数',
      'col.occurrences': '发生次数',
      'col.part': '配件',
      'col.partCost': '部品费合计',
      'col.freightCost': '运费合计',
      'col.laborCost': '师傅费用合计',
      'col.totalCost': '总费用合计',
      'col.avgMonths': '平均使用月数',
      'col.minMonths': '最小使用月数',
      'col.maxMonths': '最大使用月数',
      'col.usageRange': '使用月数区间',
      'col.totalCount': '总次数',
      'col.monthTotal': '月数合计',
      // Footer
      'footer.company': '株式会社 Water X Technologies',
      'footer.tagline': '制造产业和AI的融合 · Manufacturing × Artificial Intelligence',
      'footer.copyright': '售后数据分析系统 Version 1.2',
      'footer.rights': '© 2026 Water X Technologies. All rights reserved.',
      'footer.released': 'Released: 2026年5月',
      // 登录
      'login.title': '售后数据分析后台',
      'login.subtitle': '请输入密码以继续',
      'login.password': '密码',
      'login.placeholder': '请输入访问密码',
      'login.submit': '登录',
      'login.error': '密码错误，请重试',
      'login.networkError': '无法连接到服务器，请确认后端服务已启动',
      'login.logout': '退出登录',
      // 语言切换器
      'lang.zh': '中',
      'lang.en': 'EN',
      'lang.ja': '日',
      // 知识库
      'kb.title': '分析知识库',
      'kb.empty': '知识库为空，请在上传分析结果后点击"保存到知识库"按钮添加条目。',
      'kb.savedAt': '保存于',
      'kb.saveHint': '将本次分析结果保存到知识库，便于长期查阅',
      'kb.saveBtn': '保存到知识库',
      'kb.saveMultiHint': '将检测到的所有月份分别保存到知识库',
      'kb.saveAllBtn': '全部保存到知识库',
      'kb.saved': '已保存到知识库',
      'kb.allSaved': '个月份已全部保存到知识库',
      'kb.partialSaved': '部分保存完成',
      'kb.saveFail': '保存到知识库失败',
      'kb.saveNoData': '没有可保存的分析数据',
      'kb.saveNoYear': '分析数据中缺少年月信息',
      'kb.saveConfirmTitle': '📚 确认保存到知识库',
      'kb.saveConfirmHint': '点击确定将保存以上数据到知识库',
      'kb.deleteConfirm': '确定从知识库中删除该条目？删除后不可恢复，但不影响原始月度数据。',
      'kb.deleted': '已从知识库中删除',
      'kb.deleteFail': '删除失败',
      'kb.duplicateWarn': '⚠️ 知识库中已存在相同月份的记录',
      'kb.existingCount': '已有',
      'kb.existingUnit': '条记录',
      'kb.duplicateConfirm': '是否仍然保存？（不会覆盖已有记录）',
    },

    'en': {
      'app.title': 'After-Sales Data Analysis',
      'app.subtitle': 'Customer Complaint Parts Record Analysis',
      'app.running': 'System Running',
      'app.version': 'Version 1.2',
      'tab.upload': 'Upload & Analyze',
      'tab.monthly': 'Monthly Data',
      'tab.comparison': 'Comparison',
      'tab.knowledge': 'Knowledge Base',
      'upload.title': 'Upload Monthly After-Sales Data',
      'upload.dropText': 'Click or drag Excel file here',
      'upload.formatHint': 'Supports .xlsx · Filename should include year-month · Auto-detects multi-month data',
      'upload.analyzing': 'Analyzing data...',
      'upload.detected': 'Detected',
      'upload.months': 'months',
      'upload.saved': 'Saved',
      'upload.exists': 'Already exists (pending)',
      'upload.detectedLabel': 'Months Detected',
      'upload.savedLabel': 'Saved',
      'upload.existsLabel': 'Already Exists',
      'upload.overview': 'Monthly Data Overview',
      'upload.multiTitle': 'Multi-Month Upload Result',
      'upload.summaryTitle': 'Summary',
      'summary.totalRecords': 'Total Records',
      'summary.totalCost': 'Total Cost',
      'summary.inWarranty': 'In Warranty',
      'summary.outWarranty': 'Out of Warranty',
      'summary.coverCount': 'Cover Units',
      'summary.wholeCount': 'Complete Units',
      'summary.costUnit': '$',
      'comparison.title': 'Monthly Overview',
      'comparison.table': 'Monthly Data Summary',
      'comparison.recordsTrend': 'Total Records Trend',
      'comparison.costTrend': 'Total Cost Trend ($)',
      'comparison.warrantyTrend': 'In-Warranty Ratio Trend (%)',
      'comparison.unitCompare': 'Cover vs Complete Units',
      'comparison.colMonth': 'Month',
      'comparison.colRecords': 'Total Records',
      'comparison.colCost': 'Total Cost($)',
      'comparison.colInWarranty': 'In Warranty',
      'comparison.colOutWarranty': 'Out of Warranty',
      'comparison.colCover': 'Cover Units',
      'comparison.colWhole': 'Complete Units',
      'comparison.colRatio': 'In-Warranty %',
      'comparison.empty': 'No comparison data available. Please upload at least 2 months of data.',
      'comparison.download': 'Download Comparison Report (HTML)',
      'comparison.coverTop10': 'In-Warranty Cover Unit TOP10 Trend',
      'comparison.wholeTop10': 'In-Warranty Complete Unit TOP10 Trend',
      'comparison.coverParts': 'In-Warranty Cover Unit TOP10 Parts Trend',
      'comparison.wholeParts': 'In-Warranty Complete Unit TOP10 Parts Trend',
      'comparison.partsDetail': 'TOP10 Parts by Model',
      'comparison.special': 'Special Complaint Trends',
      'comparison.seatUsage': 'Seat Cover Failure Usage Months Trend',
      'comparison.recordsTrend': 'Total Records Trend',
      'comparison.costTrend': 'Total Cost Trend ($)',
      'comparison.warrantyTrend': 'In-Warranty Ratio Trend (%)',
      'comparison.unitCompare': 'Cover vs Complete Units',
      'monthly.title': 'Stored Months',
      'monthly.view': 'View',
      'monthly.export': 'Export Excel',
      'monthly.delete': 'Delete',
      'monthly.records': 'records',
      'monthly.uploadedAt': 'Uploaded',
      'monthly.empty': 'No data. Please upload monthly reports first.',
      'btn.confirm': 'Confirm',
      'btn.cancel': 'Cancel',
      'btn.save': 'Save',
      'btn.close': 'Close',
      'toast.uploadSuccess': 'Analysis complete! Data saved.',
      'toast.uploadFail': 'Upload failed',
      'toast.deleteConfirm': 'Delete this month\'s data? This cannot be undone.',
      'toast.deleted': 'Deleted',
      'toast.cancelled': 'Cancelled, data not saved.',
      'toast.savedByDate': 'Saved by record date',
      'toast.overwritten': 'Overwritten successfully',
      'toast.allOverwritten': 'months all overwritten',
      'toast.partialOverwritten': 'Completed',
      'toast.success': 'succeeded',
      'toast.fail': 'failed',
      'toast.keepOriginal': 'Cancelled, original data kept.',
      'toast.downloading': 'Downloading comparison report...',
      'toast.viewFail': 'View failed',
      'toast.deleteFail': 'Delete failed',
      'toast.loadFail': 'Load failed',
      'toast.overwriteFail': 'Overwrite failed',
      'modal.exists.title': 'Data Already Exists',
      'modal.exists.body': 'data already exists in the database. Overwrite? Existing data will be replaced.',
      'modal.exists.cancel': 'Cancel, keep original',
      'modal.exists.overwrite': 'Overwrite',
      'modal.multiExists.title': 'Following Months Already Exist',
      'modal.multiExists.hint': 'Overwrite the above months? New data will replace existing records.',
      'modal.multiExists.cancel': 'Cancel, keep original',
      'modal.multiExists.overwrite': 'Overwrite All',
      'modal.mismatch.title': 'Filename / Record Date Mismatch',
      'modal.mismatch.filename': 'Filename',
      'modal.mismatch.dataDate': 'Record Date',
      'modal.mismatch.hint': 'System will use the record date for processing and saving. Continue?',
      'modal.mismatch.no': 'No, discard',
      'modal.mismatch.yes': 'Yes, save by record date',
      'ai.summary': 'AI Analysis Summary',
      'ai.findings': 'Key Findings',
      'ai.alerts': 'Risk Alerts',
      'ai.recommendations': 'Recommendations',
      'ai.angles': 'Suggested Analysis Angles',
      'ai.alertWarning': 'Warning',
      'ai.alertInfo': 'Info',
      'ai.generatedAt': 'Generated at',
      'ai.autoAnalysis': 'AI Auto Analysis',
      'ai.insufficient': 'Insufficient data (at least 2 months required). Cannot perform AI analysis.',
      'status.pendingOverwrite': 'Pending Overwrite',
      'status.saved': 'Saved',
      'col.rank': 'Rank',
      'col.model': 'Model',
      'col.unitType': 'Unit Type',
      'col.warranty': 'Warranty',
      'col.count': 'Count',
      'col.occurrences': 'Occurrences',
      'col.part': 'Part',
      'col.partCost': 'Parts Cost',
      'col.freightCost': 'Freight Cost',
      'col.laborCost': 'Labor Cost',
      'col.totalCost': 'Total Cost',
      'col.avgMonths': 'Avg Months',
      'col.minMonths': 'Min Months',
      'col.maxMonths': 'Max Months',
      'col.usageRange': 'Usage Months Range',
      'col.totalCount': 'Total Count',
      'col.monthTotal': 'Month Total',
      'footer.company': 'Water X Technologies Co., Ltd.',
      'footer.tagline': 'Manufacturing × Artificial Intelligence',
      'footer.copyright': 'After-Sales Data Analysis System Version 1.2',
      'footer.rights': '© 2026 Water X Technologies. All rights reserved.',
      'footer.released': 'Released: May 2026',
      'login.title': 'After-Sales Data Analysis',
      'login.subtitle': 'Enter password to continue',
      'login.password': 'Password',
      'login.placeholder': 'Enter access password',
      'login.submit': 'Login',
      'login.error': 'Incorrect password. Please try again.',
      'login.networkError': 'Cannot connect to server. Please ensure the backend service is running.',
      'login.logout': 'Logout',
      'lang.zh': '中',
      'lang.en': 'EN',
      'lang.ja': '日',
      // Knowledge Base
      'kb.title': 'Analysis Knowledge Base',
      'kb.empty': 'Knowledge base is empty. After uploading and analyzing data, click "Save to Knowledge Base" to add entries.',
      'kb.savedAt': 'Saved at',
      'kb.saveHint': 'Save this analysis result to knowledge base for long-term reference',
      'kb.saveBtn': 'Save to Knowledge Base',
      'kb.saveMultiHint': 'Save all detected months to knowledge base separately',
      'kb.saveAllBtn': 'Save All to Knowledge Base',
      'kb.saved': 'Saved to knowledge base',
      'kb.allSaved': 'months all saved to knowledge base',
      'kb.partialSaved': 'Partial save completed',
      'kb.saveFail': 'Failed to save to knowledge base',
      'kb.saveNoData': 'No analysis data to save',
      'kb.saveNoYear': 'Missing year/month info in analysis data',
      'kb.saveConfirmTitle': '📚 Confirm Save to Knowledge Base',
      'kb.saveConfirmHint': 'Click OK to save this data to Knowledge Base',
      'kb.deleteConfirm': 'Delete this entry from knowledge base? This cannot be undone, but does NOT affect original monthly data.',
      'kb.deleted': 'Deleted from knowledge base',
      'kb.deleteFail': 'Delete failed',
      'kb.duplicateWarn': '⚠️ Same month already exists in knowledge base',
      'kb.existingCount': 'Existing',
      'kb.existingUnit': 'record(s)',
      'kb.duplicateConfirm': 'Save anyway? (Will not overwrite existing records)',
    },

    'ja': {
      'app.title': 'アフターサービスデータ分析',
      'app.subtitle': '顧客クレーム部品記録分析システム',
      'app.running': 'システム稼働中',
      'app.version': 'Version 1.2',
      'tab.upload': 'アップロード',
      'tab.monthly': '月別データ',
      'tab.comparison': '多月比較',
      'tab.knowledge': 'ナレッジベース',
      'upload.title': '月次アフターサービスデータをアップロード',
      'upload.dropText': 'クリックまたはExcelファイルをドラッグ',
      'upload.formatHint': '.xlsx形式対応 · ファイル名に年月を含める · 複数月データの自動検出・分割保存',
      'upload.analyzing': 'データ分析中...',
      'upload.detected': '検出',
      'upload.months': 'ヶ月',
      'upload.saved': '保存済み',
      'upload.exists': '既存（確認待ち）',
      'upload.detectedLabel': '検出月数',
      'upload.savedLabel': '保存済み',
      'upload.existsLabel': '既存データ',
      'upload.overview': '各月データ概要',
      'upload.multiTitle': '複数月アップロード結果',
      'upload.summaryTitle': 'サマリー指標',
      'summary.totalRecords': '総レコード数',
      'summary.totalCost': '総費用',
      'summary.inWarranty': '保証内件数',
      'summary.outWarranty': '保証外件数',
      'summary.coverCount': 'カバーユニット数',
      'summary.wholeCount': '一体型ユニット数',
      'summary.costUnit': '¥',
      'comparison.title': '月次概要',
      'comparison.table': '月次データサマリー',
      'comparison.recordsTrend': '総レコード数推移',
      'comparison.costTrend': '総費用推移 (¥)',
      'comparison.warrantyTrend': '保証内比率推移 (%)',
      'comparison.unitCompare': 'カバー vs 一体型比較',
      'comparison.colMonth': '月',
      'comparison.colRecords': '総レコード数',
      'comparison.colCost': '総費用(円)',
      'comparison.colInWarranty': '保証内件数',
      'comparison.colOutWarranty': '保証外件数',
      'comparison.colCover': 'カバーユニット',
      'comparison.colWhole': '一体型ユニット',
      'comparison.colRatio': '保証内比率',
      'comparison.empty': '比較データがありません。最低2ヶ月分のデータをアップロードしてください。',
      'comparison.download': '比較レポートをダウンロード (HTML)',
      'comparison.coverTop10': '保証内カバーユニット TOP10 推移',
      'comparison.wholeTop10': '保証内一体型ユニット TOP10 推移',
      'comparison.coverParts': '保証内カバーユニット TOP10 部品推移',
      'comparison.wholeParts': '保証内一体型ユニット TOP10 部品推移',
      'comparison.partsDetail': 'モデル別 TOP10 部品詳細',
      'comparison.special': '特化クレーム推移',
      'comparison.seatUsage': 'シートカバー故障使用月数推移',
      'comparison.recordsTrend': '総レコード数推移',
      'comparison.costTrend': '総費用推移 (¥)',
      'comparison.warrantyTrend': '保証内比率推移 (%)',
      'comparison.unitCompare': 'カバー vs 一体型比較',
      'monthly.title': '保存済み月',
      'monthly.view': '表示',
      'monthly.export': 'Excel出力',
      'monthly.delete': '削除',
      'monthly.records': '件',
      'monthly.uploadedAt': 'アップロード日',
      'monthly.empty': 'データがありません。月次レポートをアップロードしてください。',
      'btn.confirm': '確認',
      'btn.cancel': 'キャンセル',
      'btn.save': '保存',
      'btn.close': '閉じる',
      'toast.uploadSuccess': '分析完了！データを保存しました。',
      'toast.uploadFail': 'アップロード失敗',
      'toast.deleteConfirm': 'この月のデータを削除しますか？この操作は元に戻せません。',
      'toast.deleted': '削除しました',
      'toast.cancelled': 'キャンセルしました。データは保存されていません。',
      'toast.savedByDate': '記録日付で保存しました',
      'toast.overwritten': '上書き保存しました',
      'toast.allOverwritten': 'ヶ月すべて上書き保存しました',
      'toast.partialOverwritten': '完了',
      'toast.success': '成功',
      'toast.fail': '失敗',
      'toast.keepOriginal': 'キャンセルしました。元のデータを保持します。',
      'toast.downloading': '比較レポートをダウンロード中...',
      'toast.viewFail': '表示に失敗しました',
      'toast.deleteFail': '削除に失敗しました',
      'toast.loadFail': '読み込みに失敗しました',
      'toast.overwriteFail': '上書きに失敗しました',
      'modal.exists.title': 'データが既に存在します',
      'modal.exists.body': 'のデータは既にデータベースに存在します。上書き保存しますか？上書きすると元のデータは置き換えられます。',
      'modal.exists.cancel': 'キャンセル、元のデータを保持',
      'modal.exists.overwrite': '上書き保存',
      'modal.multiExists.title': '以下の月のデータが既に存在します',
      'modal.multiExists.hint': '上記の月のデータを上書きしますか？新しいデータが既存のレコードを置き換えます。',
      'modal.multiExists.cancel': 'キャンセル、元のデータを保持',
      'modal.multiExists.overwrite': 'すべて上書き',
      'modal.mismatch.title': 'ファイル名と記録日付が不一致',
      'modal.mismatch.filename': 'ファイル名',
      'modal.mismatch.dataDate': '記録日付',
      'modal.mismatch.hint': 'システムは記録日付に基づいてデータを処理・保存します。続行しますか？',
      'modal.mismatch.no': 'いいえ、破棄',
      'modal.mismatch.yes': 'はい、記録日付で保存',
      'ai.summary': 'AI分析サマリー',
      'ai.findings': '主な発見',
      'ai.alerts': 'リスク警告',
      'ai.recommendations': '改善提案',
      'ai.angles': '推奨分析视角',
      'ai.alertWarning': '警告',
      'ai.alertInfo': '情報',
      'ai.generatedAt': '生成日時',
      'ai.autoAnalysis': 'AI自動分析',
      'ai.insufficient': 'データ不足（最低2ヶ月分必要）。AI分析を実行できません。',
      'status.pendingOverwrite': '上書き確認待ち',
      'status.saved': '保存済み',
      'col.rank': '順位',
      'col.model': 'モデル',
      'col.unitType': 'ユニット種別',
      'col.warranty': '保証内外',
      'col.count': '件数',
      'col.occurrences': '発生回数',
      'col.part': '部品',
      'col.partCost': '部品費合計',
      'col.freightCost': '運送費合計',
      'col.laborCost': '作業費合計',
      'col.totalCost': '総費用合計',
      'col.avgMonths': '平均使用月数',
      'col.minMonths': '最小使用月数',
      'col.maxMonths': '最大使用月数',
      'col.usageRange': '使用月数区分',
      'col.totalCount': '総回数',
      'col.monthTotal': '月数合計',
      'footer.company': '株式会社 Water X Technologies',
      'footer.tagline': '製造業とAIの融合 · Manufacturing × Artificial Intelligence',
      'footer.copyright': 'アフターサービスデータ分析システム Version 1.2',
      'footer.rights': '© 2026 Water X Technologies. All rights reserved.',
      'footer.released': 'Released: 2026年5月',
      'login.title': 'アフターサービスデータ分析',
      'login.subtitle': 'パスワードを入力してください',
      'login.password': 'パスワード',
      'login.placeholder': 'アクセスパスワードを入力',
      'login.submit': 'ログイン',
      'login.error': 'パスワードが間違っています。再入力してください。',
      'login.networkError': 'サーバーに接続できません。バックエンドサービスが起動しているか確認してください。',
      'login.logout': 'ログアウト',
      'lang.zh': '中',
      'lang.en': 'EN',
      'lang.ja': '日',
      // ナレッジベース
      'kb.title': '分析ナレッジベース',
      'kb.empty': 'ナレッジベースは空です。データをアップロードして分析後、「ナレッジベースに保存」をクリックしてエントリを追加してください。',
      'kb.savedAt': '保存日時',
      'kb.saveHint': 'この分析結果をナレッジベースに保存し、長期間参照できます',
      'kb.saveBtn': 'ナレッジベースに保存',
      'kb.saveMultiHint': '検出されたすべての月を個別にナレッジベースに保存',
      'kb.saveAllBtn': 'すべてナレッジベースに保存',
      'kb.saved': 'ナレッジベースに保存しました',
      'kb.allSaved': 'ヶ月すべてナレッジベースに保存しました',
      'kb.partialSaved': '一部保存完了',
      'kb.saveFail': 'ナレッジベースへの保存に失敗しました',
      'kb.saveNoData': '保存する分析データがありません',
      'kb.saveNoYear': '分析データに年月情報がありません',
      'kb.saveConfirmTitle': '📚 ナレッジベースに保存確認',
      'kb.saveConfirmHint': 'OKをクリックすると上記データをナレッジベースに保存します',
      'kb.deleteConfirm': 'ナレッジベースからこのエントリを削除しますか？元に戻せませんが、元の月次データには影響しません。',
      'kb.deleted': 'ナレッジベースから削除しました',
      'kb.deleteFail': '削除に失敗しました',
      'kb.duplicateWarn': '⚠️ ナレッジベースに同じ月の記録が既に存在します',
      'kb.existingCount': '既存',
      'kb.existingUnit': '件',
      'kb.duplicateConfirm': 'それでも保存しますか？（既存の記録は上書きされません）',
    }
  },

  // ==================== 中文→翻译 key 的反向映射（用于分析数据列名翻译） ====================
  // 当后端返回中文列名时，根据此映射找到对应的 i18n key，再转为目标语言
  columnMap: {
    'zh-CN': {
      '排名': 'col.rank', '型号': 'col.model', '盖机整机': 'col.unitType', '保内保外': 'col.warranty',
      '件数': 'col.count', '发生次数': 'col.occurrences', '配件': 'col.part',
      '部品费合计': 'col.partCost', '运费合计': 'col.freightCost', '师傅费用合计': 'col.laborCost',
      '总费用合计': 'col.totalCost', '平均使用月数': 'col.avgMonths', '最小使用月数': 'col.minMonths',
      '最大使用月数': 'col.maxMonths', '使用月数区间': 'col.usageRange', '总次数': 'col.totalCount',
      '月数合计': 'col.monthTotal', '总记录数': 'summary.totalRecords', '总费用': 'summary.totalCost',
      '总费用(元)': 'summary.totalCost', '保内件数': 'summary.inWarranty', '保外件数': 'summary.outWarranty',
      '盖机件数': 'summary.coverCount', '整机件数': 'summary.wholeCount',
    }
  },

  // ==================== 方法 ====================

  /** 获取当前语言标识（用于后端 API，zh-CN → zh） */
  getLang() {
    const m = { 'zh-CN': 'zh', 'en': 'en', 'ja': 'ja' };
    return m[this.current] || 'zh';
  },

  /** 获取翻译文本 */
  t(key) {
    return this.dict[this.current]?.[key] || this.dict['zh-CN']?.[key] || key;
  },

  /** 翻译中文列名到当前语言 */
  translateColumn(cnName) {
    const map = this.columnMap['zh-CN'];
    const i18nKey = map?.[cnName];
    if (i18nKey) return this.t(i18nKey);
    // 动态月份列（如 "1个月", "2个月" ... "大于4年" 等）
    if (this.current === 'en') {
      const m = cnName.match(/^(\d+)个月$/);
      if (m) return `${m[1]}mo`;
      if (cnName === '3年(25~36月)') return '3yr(25~36mo)';
      if (cnName === '4年(37~48月)') return '4yr(37~48mo)';
      if (cnName === '大于4年') return '>4yr';
    }
    if (this.current === 'ja') {
      const m = cnName.match(/^(\d+)个月$/);
      if (m) return `${m[1]}ヶ月`;
      if (cnName === '3年(25~36月)') return '3年(25~36ヶ月)';
      if (cnName === '4年(37~48月)') return '4年(37~48ヶ月)';
      if (cnName === '大于4年') return '4年以上';
    }
    return cnName;
  },

  /** 翻译分析结果中所有标题和列名 */
  translateResults(results) {
    if (!results || this.current === 'zh-CN') return results;
    const translated = {};
    for (const [key, analysis] of Object.entries(results)) {
      if (!analysis) { translated[key] = analysis; continue; }
      const copy = JSON.parse(JSON.stringify(analysis));
      // 翻译标题（从后端返回的中文标题转目标语言）
      copy.title = this._translateAnalysisTitle(copy.title, key);
      // 翻译列名
      if (copy._orderedColumns) {
        copy._orderedColumns = copy._orderedColumns.map(c => this.translateColumn(c));
      }
      if (copy.data && Array.isArray(copy.data)) {
        copy.data = copy.data.map(row => {
          const newRow = {};
          for (const [cnKey, val] of Object.entries(row)) {
            const translatedKey = cnKey === 'TOP10部品' ? cnKey : this.translateColumn(cnKey);
            if (cnKey === 'TOP10部品' && Array.isArray(val)) {
              newRow[translatedKey] = val.map(part => {
                const np = {};
                for (const [pk, pv] of Object.entries(part)) {
                  np[this.translateColumn(pk)] = pv;
                }
                return np;
              });
            } else {
              newRow[translatedKey] = val;
            }
          }
          return newRow;
        });
      }
      translated[key] = copy;
    }
    return translated;
  },

  /** 根据中文标题和 analysis key 翻译为当前语言 */
  _translateAnalysisTitle(cnTitle, key) {
    if (!cnTitle) return '';
    // 分析标题格式如："2025年9月售后费用" → 需要提取日期前缀 + 翻译后缀
    // 匹配模式：年份年月份月 + 后缀
    const prefixMatch = cnTitle.match(/^(\d{4}年\d{1,2}月)(.+)$/);
    let datePrefix = '';
    let suffix = cnTitle;

    if (prefixMatch) {
      datePrefix = prefixMatch[1];
      suffix = prefixMatch[2];
      // 翻译日期前缀
      if (this.current === 'en') {
        datePrefix = datePrefix.replace(/^(\d{4})年(\d{1,2})月$/, (_, y, m) => {
          const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
          return `${months[parseInt(m)-1]} ${y}`;
        });
      }
      // 日语保持"2025年9月"格式不变
    }

    // 翻译后缀
    const titleMap = {
      'zh-CN': {
        '售后费用': '售后费用', '各产品投诉的使用月数和售后情况': '各产品投诉的使用月数和售后情况',
        '盖机TOP10': '盖机TOP10', '保内盖机TOP10': '保内盖机TOP10',
        '保内盖机TOP10各TOP10部品': '保内盖机TOP10各TOP10部品',
        '整机TOP10': '整机TOP10', '保内整机TOP10': '保内整机TOP10',
        '保内整机TOP10各TOP10部品': '保内整机TOP10各TOP10部品',
        '保内座盖投诉数量': '保内座盖投诉数量', '保内座盖软胶垫投诉数量': '保内座盖软胶垫投诉数量',
        '柔光灯投诉数量': '柔光灯投诉数量', '座盖故障数量和使用月数': '座盖故障数量和使用月数',
        '所有产品使用月数汇总': '所有产品使用月数汇总',
      },
      'en': {
        '售后费用': 'After-Sales Costs', '各产品投诉的使用月数和售后情况': 'Usage Months & After-Sales by Product',
        '盖机TOP10': 'Cover Unit TOP10', '保内盖机TOP10': 'In-Warranty Cover Unit TOP10',
        '保内盖机TOP10各TOP10部品': 'In-Warranty Cover Unit TOP10 Parts',
        '整机TOP10': 'Complete Unit TOP10', '保内整机TOP10': 'In-Warranty Complete Unit TOP10',
        '保内整机TOP10各TOP10部品': 'In-Warranty Complete Unit TOP10 Parts',
        '保内座盖投诉数量': 'In-Warranty Seat Cover Complaints',
        '保内座盖软胶垫投诉数量': 'In-Warranty Seat Cover Pad Complaints',
        '柔光灯投诉数量': 'Soft Light Complaints',
        '座盖故障数量和使用月数': 'Seat Cover Failures & Usage Months',
        '所有产品使用月数汇总': 'All Products Usage Months Summary',
      },
      'ja': {
        '售后费用': 'アフターサービス費用', '各产品投诉的使用月数和售后情况': '製品別使用月数・アフターサービス状況',
        '盖机TOP10': 'カバーユニットTOP10', '保内盖机TOP10': '保証内カバーユニットTOP10',
        '保内盖机TOP10各TOP10部品': '保証内カバーユニットTOP10部品',
        '整机TOP10': '一体型ユニットTOP10', '保内整机TOP10': '保証内一体型ユニットTOP10',
        '保内整机TOP10各TOP10部品': '保証内一体型ユニットTOP10部品',
        '保内座盖投诉数量': '保証内シートカバークレーム',
        '保内座盖软胶垫投诉数量': '保証内シートカバーパッドクレーム',
        '柔光灯投诉数量': 'ソフトライトクレーム',
        '座盖故障数量和使用月数': 'シートカバー故障数・使用月数',
        '所有产品使用月数汇总': '全製品使用月数サマリー',
      }
    };

    const translatedSuffix = titleMap[this.current]?.[suffix] || suffix;
    return datePrefix ? `${datePrefix} ${translatedSuffix}` : translatedSuffix;
  },

  /** 翻译汇总指标 */
  translateSummary(summary) {
    if (!summary || this.current === 'zh-CN') return summary;
    const s = { ...summary };
    // month_label: "2025年9月" → "Sep 2025" or keep "2025年9月"
    if (s.month_label) {
      s.month_label = this._translateMonthLabel(s.month_label);
    }
    return s;
  },

  _translateMonthLabel(label) {
    if (this.current === 'en') {
      return label.replace(/^(\d{4})年(\d{1,2})月$/, (_, y, m) => {
        const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        return `${months[parseInt(m)-1]} ${y}`;
      });
    }
    return label; // ja keeps the same format
  },

  // ==================== 初始化 ====================

  /** 检测浏览器语言 */
  detectBrowserLang() {
    const lang = navigator.language || navigator.userLanguage || 'zh-CN';
    if (lang.startsWith('ja')) return 'ja';
    if (lang.startsWith('zh')) return 'zh-CN';
    if (lang.startsWith('en')) return 'en';
    return 'zh-CN';
  },

  /** 初始化语言 */
  init() {
    const stored = localStorage.getItem('shouhou_lang');
    this.current = stored || this.detectBrowserLang();
    if (!stored) {
      localStorage.setItem('shouhou_lang', this.current);
    }
    this._applyToDOM();
    this._updateLangButtons();
    return this.current;
  },

  /** 切换语言 */
  switchTo(lang) {
    if (lang === this.current) return;
    this.current = lang;
    localStorage.setItem('shouhou_lang', lang);
    this._applyToDOM();
    this._updateLangButtons();
  },

  /** 将 data-i18n 属性替换为当前语言 */
  _applyToDOM() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const text = this.t(key);
      if (text) {
        if (el.tagName === 'INPUT' && el.type === 'placeholder') {
          el.placeholder = text;
        } else if (el.tagName === 'INPUT') {
          el.value = text;
        } else {
          el.textContent = text;
        }
      }
    });
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      el.title = this.t(el.getAttribute('data-i18n-title'));
    });
    document.documentElement.lang = this.current === 'ja' ? 'ja' : this.current === 'en' ? 'en' : 'zh-CN';
  },

  /** 更新语言切换按钮状态 */
  _updateLangButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      const lang = btn.getAttribute('data-lang');
      btn.classList.toggle('active', lang === this.current);
    });
  },
};

// 全局快捷函数
const __ = (key) => I18N.t(key);
