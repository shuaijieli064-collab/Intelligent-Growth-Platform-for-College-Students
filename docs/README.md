# 大学生智能成长平台 v3.0

> Python 课程设计项目 | PyQt5 桌面 GUI + FastAPI Web 双界面 | MySQL 数据库 | 四层架构

---

## 目录

1. [项目简介](#1-项目简介)
2. [快速开始](#2-快速开始)
3. [项目结构](#3-项目结构)
4. [功能模块](#4-功能模块)
5. [架构设计](#5-架构设计)
6. [数据库设计](#6-数据库设计)
7. [配置说明](#7-配置说明)
8. [开发指南](#8-开发指南)
9. [打包部署](#9-打包部署)
10. [常见问题](#10-常见问题)

---

## 1. 项目简介

### 1.1 项目背景

**大学生智能成长平台**是一个面向大学生的综合性学习管理与成长辅助系统。本项目是《Python 程序设计技术》课程设计作品，通过实际项目锻炼面向对象编程、数据库操作、GUI 开发、Web 开发、数据分析与机器学习等综合技能。

### 1.2 核心目标

- **学习管理**：记录每日学习情况，追踪学习轨迹
- **健康评估**：从学业、身体、心理、社交四个维度量化学生综合健康度
- **智能预测**：基于历史成绩数据，使用机器学习预测期末成绩
- **知识可视化**：通过知识图谱展示课程知识结构与掌握程度
- **AI 辅助**：接入大语言模型，提供个性化学习建议与心理疏导
- **风险预警**：自动检测学业风险并及时告警

### 1.3 双界面架构

本项目同时提供两套独立的用户界面，共享同一套后端业务逻辑与数据层：

| 界面 | 技术栈 | 入口 | 适用场景 |
|------|--------|------|----------|
| 桌面 GUI | PyQt5 + Matplotlib | `main.py` | 单机使用、课程演示 |
| Web 界面 | FastAPI + React + ECharts | `web/main.py` + `frontend/` | 多用户访问、远程使用 |

### 1.4 技术栈

**后端（共享）**

| 技术 | 说明 |
|------|------|
| Python 3.12 | 主要开发语言 |
| pymysql | MySQL 数据库驱动 |
| pandas / numpy / scipy | 数据处理与科学计算 |
| scikit-learn | 机器学习（线性回归、梯度提升） |
| NetworkX 3.0+ | 知识图谱构建 |
| requests | LLM API 调用 |

**桌面 GUI**

| 技术 | 说明 |
|------|------|
| PyQt5 5.15+ | 桌面界面框架 |
| Matplotlib 3.6+ | 图表渲染（嵌入 PyQt5） |

**Web 界面**

| 技术 | 说明 |
|------|------|
| FastAPI | 后端 API 框架 |
| Uvicorn | ASGI 服务器 |
| Pydantic | 请求/响应数据校验 |
| React 19 + TypeScript | 前端框架 |
| Vite 8 | 前端构建工具 |
| ECharts 6 | 数据可视化 |
| Tailwind CSS 3 | 样式框架 |
| Zustand | 状态管理 |
| Axios | HTTP 请求 |

**数据库**

| 技术 | 说明 |
|------|------|
| MySQL 8.4 | 关系型数据库 |

---

## 2. 快速开始

### 2.1 环境要求

| 软件 | 最低版本 | 下载 |
|------|---------|------|
| Python | 3.12 | https://www.python.org/downloads/ |
| MySQL | 8.4 | https://dev.mysql.com/downloads/mysql/8.4.html |
| Node.js | 18+（仅 Web 前端） | https://nodejs.org/ |
| 操作系统 | Windows 10/11 64位 | — |

### 2.2 安装步骤

**第一步：安装 Python 依赖**

```batch
pip install -r requirements.txt
```

**第二步：安装 MySQL**

1. 下载 MySQL 8.4 ZIP Archive
2. 解压到 `C:\Program Files\MySQL\MySQL Server 8.4\`
3. 以管理员身份初始化数据目录：
   ```batch
   mkdir "%USERPROFILE%\mysql_data"
   "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --initialize-insecure --datadir="%USERPROFILE%\mysql_data"
   ```

**第三步：初始化数据库**

```batch
python scripts\init_database.py
python scripts\generate_mock_data.py
```

**第四步：启动**

- **桌面 GUI**：双击 `启动.bat` 或执行 `python 启动.py`（自动启动 MySQL）
- **Web 界面**：
  ```batch
  # 启动后端 API
  python -m uvicorn web.main:app --reload --port 8000

  # 启动前端（另开终端）
  cd frontend
  npm install
  npm run dev
  ```

### 2.3 演示数据

`scripts/generate_mock_data.py` 会自动生成：
- **5 个学生**（张三、李四、王五、赵六、钱七）
- **8 门课程**（程序设计基础、数据结构与算法、面向对象程序设计、数据库原理、人工智能导论、高等数学、线性代数、大学英语）
- **30 天学习记录**（约 150 条）
- **52 个课程专属知识点** + 掌握度记录
- **14 天健康数据**（身体/心理/社交）
- **健康评估快照**（14 天 × 5 人 = 75 条）

---

## 3. 项目结构

```
ChengZhang/
│
├── business_layer/              # 业务逻辑层（12 个业务模块）
│   ├── ai_coach.py             # AI 学习教练（LLM 对话）
│   ├── data_processor.py       # 数据处理器
│   ├── digital_twin.py         # 数字孪生（四维健康评估）
│   ├── focus_monitor.py        # 专注度监测
│   ├── grade_predictor_v2.py   # 成绩预测（线性回归/XGBoost）
│   ├── growth_archiver.py      # 成长档案生成
│   ├── knowledge_graph.py      # 知识图谱构建与分析
│   ├── resource_recommender.py # 资源推荐引擎
│   ├── risk_warning.py         # 风险预警系统（7 条规则）
│   ├── seed_data.py            # 默认课程种子数据
│   └── study_plan_generator.py # 学习计划生成器
│
├── data_layer/                  # 数据访问层
│   ├── database.py             # DatabaseManager（threading.local 连接池）
│   ├── models.py               # 12 个 dataclass 数据模型
│   └── dao/                    # 11 个 DAO 类（每表一个）
│
├── presentation_layer/          # PyQt5 桌面 GUI 层
│   ├── main_window.py          # 主窗口（侧边栏导航 + 堆栈页面）
│   ├── setup_dialog.py         # 首次运行配置对话框
│   ├── styles.py               # QSS 双主题样式
│   └── widgets/                # 12 个功能页面组件
│
├── web/                         # FastAPI Web 服务层
│   ├── main.py                 # FastAPI 应用入口（19 个路由）
│   ├── dependencies.py         # 依赖注入（DAO 实例）
│   ├── requirements-web.txt    # Web 独立依赖
│   ├── routers/                # 19 个 API 路由模块
│   └── schemas/                # 18 个 Pydantic 数据模型
│
├── frontend/                    # React + TypeScript 前端
│   ├── src/
│   │   ├── api/                # 19 个 API 接口封装
│   │   ├── components/         # 布局组件 + UI 基础组件
│   │   ├── hooks/              # 自定义 Hooks（主题/健康检查/ECharts）
│   │   ├── pages/              # 15 个页面
│   │   ├── router/             # 路由配置（含登录守卫）
│   │   ├── store/              # Zustand 状态管理
│   │   ├── styles/             # 全局样式 + 设计令牌
│   │   ├── types/              # TypeScript 类型定义
│   │   └── utils/              # 工具函数
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── sql/                         # 数据库脚本（3 个迁移版本）
│   ├── schema.sql              # 基础表结构（7 张表）
│   ├── v2_extend.sql           # V2 扩展（学习计划/资源/档案）
│   └── v3_health_extend.sql    # V3 健康扩展（身体/心理/社交）
│
├── utils/                       # 通用工具
│   ├── chart_canvas.py         # Matplotlib 画布封装
│   ├── helpers.py              # 通用辅助函数
│   └── llm_client.py           # LLM API 客户端
│
├── tests/                       # 单元测试（6 个）
│   ├── test_ai_coach.py
│   ├── test_database.py
│   ├── test_digital_twin.py
│   ├── test_grade_predictor.py
│   ├── test_knowledge_graph.py
│   └── test_risk_warning.py
│
├── scripts/                     # 运维脚本
│   ├── init_database.py        # 数据库初始化
│   └── generate_mock_data.py   # 演示数据生成
│
├── deploy/                      # 部署配置
│   └── build.spec              # PyInstaller 打包配置
│
├── legacy/                      # 旧版归档
│   ├── smart-growth-platform/  # 静态 HTML 原型（14 页面）
│   └── smart-growth-platform.design
│
├── docs/                        # 文档
│   └── README.md               # 本文件
│
├── config.py                    # 配置加载器（DB + LLM，支持 JSON 覆盖）
├── config.example.json          # 配置模板
├── main.py                      # GUI 主入口
├── 启动.py                      # 一键启动器（自动启动 MySQL）
├── 启动.bat                     # Windows 启动脚本
├── 一键安装.bat                  # 依赖安装脚本
├── requirements.txt             # Python 依赖
└── .gitignore
```

---

## 4. 功能模块

### 4.1 数据录入

系统的数据入口，包含 7 个 Tab 页面：

| Tab | 内容 | 数据表 |
|-----|------|--------|
| 学习记录 | 日期、课程、学习时长、专注度、完成任务数、备注 | study_record |
| 成绩录入 | 课程、平时成绩、期中成绩、期末成绩 | student_course |
| 身体健康 | 运动类型、时长、睡眠、步数 | physical_health_record |
| 心理健康 | 心情评分、压力等级、焦虑等级、日记 | mental_health_record |
| 社交健康 | 活动类型、时长、互动人数 | social_health_record |
| 个人信息 | 姓名、学号、性别、年级、专业 | student |
| 课程管理 | 课程代码、名称、学分、必修/选修 | course |

### 4.2 首页仪表盘

聚合展示核心数据：综合健康度、风险等级、活跃告警数、四维度评分、最近告警列表。每次打开自动生成一条健康评估快照。

### 4.3 数字孪生

从学业、身体、心理、社交四个维度量化学生健康状态：

| 维度 | 权重 | 数据来源 |
|------|------|---------|
| 学业健康 | 35% | 课程成绩加权平均（平时×0.3 + 期中×0.3 + 期末×0.4） |
| 身体健康 | 25% | 运动时长/频率 + 睡眠质量 + 步数 |
| 心理健康 | 25% | 心情评分 + 压力等级 + 焦虑等级 |
| 社交健康 | 15% | 社交活跃频率 + 活动时长 + 互动人数 |

风险等级：≥80 LOW / ≥60 MEDIUM / ≥40 HIGH / <40 CRITICAL

可视化：四维度雷达图 + 趋势折线图 + 历史评估列表。

### 4.4 成绩预测

两种算法可选：
- **线性回归**（LinearRegression）：简单可解释，数据少时更稳定
- **梯度提升**（GradientBoostingRegressor）：集成学习，数据多时精度更高

训练流程：选择课程 → 拉取历史成绩 → 交叉验证 → 输入平时+期中 → 输出预测值 + 95% 置信区间 + 及格概率。每个课程独立训练模型。

### 4.5 知识图谱

- 使用 NetworkX 创建有向图，节点 = 知识点，边 = 前置依赖
- 掌握度着色：绿色(≥80%) / 黄色(50-80%) / 红色(<50%)
- 薄弱节点识别 + 前置依赖链分析 + 拓扑排序推荐学习顺序

### 4.6 AI 学习教练

- 基于系统提示词的角色扮演（专业大学成长教练）
- 多轮对话记忆，按 session 管理，持久化存储
- 自动注入学生数据上下文（健康度、薄弱知识点、风险告警）
- 6 个快捷操作按钮（学习建议/情绪疏导/生涯规划/成绩分析/每日激励/新对话）
- 支持 DeepSeek / 智谱 AI / 通义千问 / 自定义 OpenAI 兼容端点
- API Key 使用 Base64 编码存储

### 4.7 风险预警

7 条自动检测规则：

| 规则 | 触发条件 | 风险等级 |
|------|---------|---------|
| 挂科风险 | 任一课程期末成绩 < 60 | HIGH |
| 成绩下滑 | 连续 3 周学习时长递减 | MEDIUM |
| 健康临界 | 综合健康度 < 40 | CRITICAL |
| 健康下降 | 两周健康度下降 > 15 分 | HIGH |
| 心理倦怠 | 7 天平均专注度 < 30 | MEDIUM |
| 学习不足 | 7 天日均学习 < 2 小时 | MEDIUM |
| 任务完成低 | 7 天日均完成任务 < 1.5 | LOW |

### 4.8 学习计划生成器

基于薄弱知识点，按剩余天数分 4 阶段分配任务（基础补强 → 综合练习 → 模拟考试 → 最终复习），支持逐项勾选和进度追踪。

### 4.9 资源推荐

三层匹配策略：精准匹配（知识点关键词）→ 课程补充（课程名关键词）→ 扩展兜底。按课程独立去重。资源类型：视频 / 练习 / 文章 / 课程。

### 4.10 专注度监测

实时专注指数（当天平均专注度）+ 14 天折线图 + 30 天热历图。

### 4.11 成长档案

自动生成阶段性报告（周报/月报/学期报告），包含四维度健康度、学习时长、任务完成率、专注度趋势。

### 4.12 数据可视化

4 个图表 Tab：学习曲线（柱状图+均线）、健康趋势（五维度折线）、成绩雷达（极坐标）、知识热力图（矩阵）。

---

## 5. 架构设计

### 5.1 四层架构

```
┌──────────────────────────────────────────────────┐
│        表现层 (Presentation Layer)                │
│  PyQt5: MainWindow + 12 Widgets + 双主题 QSS     │
│  Web:   React 15 Pages + ECharts + Tailwind      │
│  负责：界面渲染、用户交互、图表展示                │
├──────────────────────────────────────────────────┤
│        Web 服务层 (Web Layer)                      │
│  FastAPI: 19 Routers + 18 Schemas                │
│  负责：HTTP 接口、请求校验、依赖注入               │
├──────────────────────────────────────────────────┤
│        业务层 (Business Layer)                     │
│  12 个业务类，每个独立封装一种算法或规则            │
│  负责：健康计算、成绩预测、图谱分析、对话管理       │
├──────────────────────────────────────────────────┤
│        数据层 (Data Layer)                         │
│  DatabaseManager + 11 个 DAO + 12 个 Model        │
│  负责：数据库连接、CRUD、数据模型定义               │
└──────────────────────────────────────────────────┘
```

### 5.2 数据流

**桌面 GUI**：
```
用户操作 → Widget → Business → DAO → DatabaseManager → MySQL
```

**Web 界面**：
```
浏览器 → React → Axios → FastAPI Router → Business → DAO → MySQL
```

### 5.3 设计模式

| 模式 | 应用位置 | 说明 |
|------|---------|------|
| threading.local | DatabaseManager | 线程隔离数据库连接，防止并发冲突 |
| DAO | data_layer/dao/ | 每张表一个 DAO 类，封装 SQL 操作 |
| dataclass | data_layer/models.py | 12 个数据模型，类型安全 |
| Enum | RiskLevel | 风险等级枚举，避免魔术字符串 |
| Strategy | GradePredictorV2 | 线性回归/梯度提升可切换 |
| 依赖注入 | web/dependencies.py | FastAPI Depends 注入 DAO 实例 |

---

## 6. 数据库设计

### 6.1 表结构概览（14 张表）

| 表名 | 说明 | 所属版本 |
|------|------|---------|
| student | 学生信息 | schema.sql |
| course | 课程目录 | schema.sql |
| student_course | 选课与成绩 | schema.sql |
| study_record | 每日学习记录 | schema.sql |
| health_assessment | 健康评估快照 | schema.sql |
| knowledge_point | 知识点节点 | schema.sql |
| knowledge_mastery | 知识点掌握度 | schema.sql |
| risk_alert | 风险告警 | schema.sql |
| ai_coach_log | AI 对话日志 | schema.sql |
| study_plan | 学习计划 | v2_extend.sql |
| resource_recommendation | 资源推荐 | v2_extend.sql |
| growth_report | 成长档案 | v2_extend.sql |
| physical_health_record | 身体健康记录 | v3_health_extend.sql |
| mental_health_record | 心理健康记录 | v3_health_extend.sql |
| social_health_record | 社交健康记录 | v3_health_extend.sql |

### 6.2 ER 关系

```
student ──< student_course >── course
student ──< study_record
student ──< health_assessment
student ──< knowledge_mastery >── knowledge_point
knowledge_point ── knowledge_point (parent_kp_id 自引用)
course ──< knowledge_point
student ──< risk_alert
student ──< ai_coach_log
student ──< study_plan
student ──< resource_recommendation
student ──< growth_report
student ──< physical_health_record
student ──< mental_health_record
student ──< social_health_record
```

---

## 7. 配置说明

### 7.1 config.py

配置加载器按以下优先级查找 `config.json`：
1. PyInstaller 打包后 exe 同目录
2. 项目根目录
3. 环境变量 `TRAININGPROJECT_CONFIG` 指定路径
4. 系统 AppData 目录

### 7.2 config.example.json

```json
{
  "db_config": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "database": "student_growth_platform",
    "charset": "utf8mb4"
  },
  "llm_config": {
    "provider": "deepseek",
    "api_key": "",
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat"
  }
}
```

复制为 `config.json` 并修改数据库密码即可。首次启动 GUI 也会弹出配置对话框。

### 7.3 LLM 提供商

| 提供商 | API 地址 | 模型 | 费用 |
|--------|---------|------|------|
| DeepSeek | api.deepseek.com | deepseek-chat | 免费额度 |
| 智谱 AI | open.bigmodel.cn | glm-4-flash | 免费额度 |
| 通义千问 | dashscope.aliyuncs.com | qwen-turbo | 免费额度 |
| 自定义 | 任意 OpenAI 兼容端点 | — | — |

### 7.4 健康度权重

```python
HEALTH_WEIGHTS = {"academic": 0.35, "physical": 0.25, "mental": 0.25, "social": 0.15}
RISK_THRESHOLDS = {"low": 80, "medium": 60, "high": 40}
```

---

## 8. 开发指南

### 8.1 添加新功能

1. `data_layer/models.py` — 定义 dataclass 数据模型
2. `data_layer/dao/` — 创建 DAO 类
3. `business_layer/` — 实现业务逻辑类
4. GUI：`presentation_layer/widgets/` — 创建 Widget，注册到 `main_window.py`
5. Web：`web/routers/` + `web/schemas/` — 创建路由和 Schema，注册到 `web/main.py`
6. 前端：`frontend/src/pages/` — 创建页面，注册到 `frontend/src/router/index.tsx`

### 8.2 运行测试

```batch
python -m pytest tests/ -v
```

### 8.3 前端开发

```batch
cd frontend
npm install
npm run dev      # 开发模式（热更新）
npm run build    # 生产构建
npm run lint     # 代码检查
```

### 8.4 数据库连接注意事项

DatabaseManager 使用 `threading.local()` 实现线程隔离连接。FastAPI 的线程池模式下，多个并发请求（如 `Promise.all`）会各自获取独立连接，避免单例连接导致的 500 错误。

---

## 9. 打包部署

### 9.1 GUI 打包为 EXE

```batch
cd <项目根目录>
pyinstaller deploy/build.spec --clean --noconfirm
```

生成的 exe 位于 `dist/大学生智能成长平台.exe`（约 143 MB，单文件模式，无控制台窗口）。

内置资源：SQL 脚本 + 配置模板。首次运行弹出数据库配置对话框。

### 9.2 Web 部署

```batch
# 后端
pip install -r web/requirements-web.txt
uvicorn web.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm run build
# 将 dist/ 部署到 Nginx 或其他静态服务器
```

---

## 10. 常见问题

**Q: 启动提示 "Can't connect to MySQL"**
A: MySQL 未启动。使用 `启动.py`（自动启动 MySQL），或手动启动 MySQL 服务。

**Q: 图表中文显示方框**
A: 安装 Microsoft YaHei 或 SimHei 中文字体。

**Q: AI 教练无回复**
A: 未配置 API Key。打开 AI 教练页面 → 选择 DeepSeek → 注册获取 Key → 粘贴 → 测试连接 → 保存。

**Q: 健康趋势无数据**
A: 打开"首页仪表盘"触发首次评估。之后每次保存健康数据自动更新。

**Q: 成绩预测报"数据不足"**
A: 该课程需要至少 3 条完整成绩（平时+期中+期末都有值）。在"数据录入 → 成绩录入"补充数据。

**Q: Web 界面无法访问 API**
A: 检查后端是否在 8000 端口运行，前端 `vite.config.ts` 中的代理配置是否正确。

**Q: 如何重置数据库**
```batch
python scripts\init_database.py
python scripts\generate_mock_data.py
```

**Q: 打包后的 exe 首次启动慢**
A: 单文件模式需要解压到临时目录，属正常现象。如需加快启动，可改为目录模式（修改 `build.spec` 中 EXE 参数）。

---

**版本**：v3.0 | **日期**：2026-08-11 | **项目**：Python 程序设计技术课程设计
