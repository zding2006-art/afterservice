# CHANGELOG

## [v1.1.0] - 2026-06-07

### ♻️ 代码重构（Code Refactoring）

本次更新在**不改变任何现有功能**的前提下，对代码结构进行了系统性重构，
目标是「更易维护、更好扩展、更方便部署」。

#### 新增文件结构

```
backend/
├── config.py                  # 新增：统一配置管理
├── services/
│   ├── __init__.py
│   ├── trends.py              # 新增：多月推移数据构建（从 db.py 拆出）
│   ├── export_excel.py        # 新增：Excel 报告生成服务（从 app.py 拆出）
│   └── export_html.py         # 新增：HTML 多月对比报告生成（从 app.py 拆出）
└── tests/                     # 新增：调试/测试文件统一存放
    ├── debug_dates.py
    ├── debug_multi.py
    ├── test_api_multi.py
    └── test_multi.py
```

#### 具体改动

**`config.py`（新增）**
- 将原先散落在 `app.py` 顶部的所有配置常量（端口、密码、路径、CORS 等）集中到此文件
- 所有配置均优先读取环境变量，部署时只需设置环境变量，无需修改源码
- 支持 PyInstaller 冻结环境路径自动适配

**`services/trends.py`（新增，从 `db.py` 拆出）**
- 将原 `db.py` 中 ~400 行的 `_build_trends()` 函数迁移至此
- 重构为多个独立工具函数：`_build_model_trend()`、`_build_parts_trend()` 等
- 消除大量重复的嵌套循环，降低圈复杂度
- 与数据库完全解耦，可单独进行单元测试

**`services/export_excel.py`（新增，从 `app.py` 拆出）**
- 将原 `app.py` 中 Excel 导出相关的全部逻辑（样式常量、辅助函数、主导出逻辑）迁移至此
- Excel 样式定义为模块级常量，避免每次导出时重复创建对象
- 表段配置（`_SECTION_MAP`）集中管理，新增分析项只需在此处添加一行
- 对外暴露单一入口：`build_monthly_excel(month_label, detail) -> str`

**`services/export_html.py`（新增，从 `app.py` 拆出）**
- 将原 `app.py` 中 HTML 报告生成逻辑（~200 行字符串拼接）迁移至此
- 重构为职责单一的子函数：`_tbl_html()`、`_chart_js()`、`_build_trends_html()`、`_build_insights_html()`
- HTML 页面结构提取为 `_HTML_TEMPLATE` 模板字符串，与动态数据完全分离
- 对外暴露单一入口：`build_comparison_html(data) -> str`

**`app.py`（精简）**
- 从 ~800 行缩减至 ~200 行，只保留路由注册、鉴权逻辑、请求/响应处理
- 所有业务实现委托给 `services/` 和其他专职模块
- CORS 和数据库路径配置改为从 `config.py` 读取

**`db.py`（精简）**
- 移除 `_build_trends()` 函数（已迁至 `services/trends.py`）
- 改为从 `services.trends` 导入 `build_trends`，调用方式不变
- 职责聚焦于纯数据库读写（CRUD）

**`tests/`（新增目录）**
- 将原 `backend/` 根目录下的 `debug_dates.py`、`debug_multi.py`、`test_api_multi.py`、`test_multi.py` 统一移入 `tests/` 目录

---

## [v1.0.0] - 2026-06-05

### 🎉 初始发布

- Flask + SQLite 后端，端口 5859
- 12 项售后数据分析（保修期费用、型号使用月数、TOP10 型号与部品等）
- 多月份数据自动拆分与对比（趋势图 + 推移表）
- AI 智能分析引擎（`insights.py`），自动识别异常趋势、生成建议
- 多语言支持：简体中文 / English / 日本語（前后端完整三语支持）
- 登录鉴权（Session + 密码，支持环境变量配置）
- Excel 单月导出、HTML 多月对比报告导出
- PyInstaller 打包支持（Windows EXE 一键运行）
- 部署包（`deploy/`）支持 Linux 服务器部署
