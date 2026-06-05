# 售后数据分析后台管理系统

## 方式一：Python 环境运行（推荐）

### 新电脑上第一次运行

1. **安装 Python 3.8+**
   - 下载：https://www.python.org/downloads/
   - 安装时勾选 "Add Python to PATH"

2. **拷贝项目文件夹**到目标电脑任意位置

3. **双击 `start.bat`**，自动安装依赖并启动

4. 浏览器访问 **http://localhost:5859**

### 后续使用

直接双击 `start.bat` 即可。

---

## 方式二：打包成独立 EXE（无需安装 Python）

在**本机**（已装 Python 的电脑）上执行：

```bash
pip install pyinstaller
cd backend

pyinstaller --onefile --name 售后分析工具 --add-data "../frontend/index.html;frontend" app.py
```

生成的 `dist/售后分析工具.exe` 拷贝到任意 Windows 电脑直接运行，浏览器访问 `http://localhost:5859`。

> ⚠️ EXE 首次启动较慢（10-30 秒），正常现象。

---

## 项目结构

```
20260521102755/
├── start.bat          ← 一键启动
├── README.md
├── backend/
│   ├── app.py         ← Flask API 服务
│   ├── analyzer.py    ← 12 项数据分析引擎
│   ├── db.py          ← SQLite 数据库
│   ├── requirements.txt
│   └── after_sales.db ← 历月数据（自动生成）
└── frontend/
    └── index.html     ← Web 管理界面
```

## 数据说明

- 数据库文件 `after_sales.db` 保存在 `backend/` 下，拷贝项目时一并带走即可保留历月数据
- 不含 `after_sales.db` 则是全新空库，上传当月表格即可重新积累
