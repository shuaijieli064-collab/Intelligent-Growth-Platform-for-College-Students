# 大学生智能成长平台 v2.1 — 完整文档

> Python 课程设计项目 | PyQt5 桌面 GUI | MySQL 数据库 | 三层架构

---

## 目录

1. [项目简介](#1-项目简介)
2. [快速开始](#2-快速开始)
3. [功能模块详解](#3-功能模块详解)
4. [架构设计](#4-架构设计)
5. [数据库设计](#5-数据库设计)
6. [配置说明](#6-配置说明)
7. [开发指南](#7-开发指南)
8. [常见问题](#8-常见问题)

---

## 1. 项目简介

### 1.1 项目背景

**大学生智能成长平台**是一个面向大学生的综合性学习管理与成长辅助系统。本项目是《Python 程序设计技术》课程设计作品，旨在通过实际项目锻炼面向对象编程、数据库操作、GUI 开发、数据分析与机器学习等综合技能。

### 1.2 核心目标

- **学习管理**：记录每日学习情况，追踪学习轨迹
- **健康评估**：从学业、身体、心理、社交四个维度量化学生综合健康度
- **智能预测**：基于历史成绩数据，使用机器学习预测期末成绩
- **知识可视化**：通过知识图谱展示课程知识结构与掌握程度
- **AI 辅助**：接入大语言模型，提供个性化学习建议与心理疏导
- **风险预警**：自动检测学业风险并及时告警

### 1.3 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.12 | 主要开发语言 |
| GUI | PyQt5 5.15+ | 桌面界面框架 |
| 数据库 | MySQL 8.4 | 关系型数据库 |
| ORM/DB | pymysql | 数据库驱动 |
| 数据分析 | pandas | 数据处理 |
| 机器学习 | scikit-learn | 线性回归、梯度提升 |
| 图分析 | NetworkX 3.0+ | 知识图谱构建 |
| 可视化 | Matplotlib 3.6+ | 图表渲染 |
| LLM | DeepSeek / 智谱 / 通义千问 | AI 教练对话 |
| 科学计算 | numpy, scipy | 数值计算与统计 |

### 1.4 设计特色

- **三层架构**：数据层(DAO) → 业务层(Business) → 表现层(Presentation)，职责分离
- **单例数据库连接**：持久复用连接，避免反复 TCP 握手
- **双主题切换**：浅色 Claude 风格 + 暗色暖炭风格，一键切换
- **面向对象设计**：dataclass 模型、Enum 枚举、继承与多态

---

## 2. 快速开始

### 2.1 环境要求

| 软件 | 最低版本 | 下载 |
|------|---------|------|
| Python | 3.12 | https://www.python.org/downloads/ |
| MySQL | 8.4 | https://dev.mysql.com/downloads/mysql/8.4.html |
| 操作系统 | Windows 10/11 64位 | — |

### 2.2 安装步骤

**第一步：安装 Python**

下载 Python 3.12+ 安装包，**务必勾选 "Add Python to PATH"**，一路 Next 完成。

**第二步：安装 MySQL**

1. 下载 MySQL 8.4 ZIP Archive（约 200MB）
2. 解压到 `C:\Program Files\MySQL\MySQL Server 8.4\`
3. 以管理员身份打开 cmd，初始化数据目录：
   ```batch
   mkdir "%USERPROFILE%\mysql_data"
   "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --initialize-insecure --datadir="%USERPROFILE%\mysql_data"
   ```

**第三步：安装依赖**

将项目文件夹解压到任意位置，双击 `一键安装.bat`：
```batch
pip install -r requirements.txt
```

**第四步：初始化数据库**

```batch
python init_database.py
python generate_mock_data.py
```

**第五步：启动**

双击 `启动.bat`，程序自动启动 MySQL 并打开主界面。

### 2.3 演示数据

`generate_mock_data.py` 会自动生成：
- **5 个学生**（张三、李四、王五、赵六、钱七）
- **8 门课程**（程序设计基础、数据结构与算法、面向对象程序设计、数据库原理、人工智能导论、高等数学、线性代数、大学英语）
- **30 天学习记录**（约 150 条）
- **52 个课程专属知识点** + 掌握度记录
- **14 天健康数据**（身体/心理/社交）
- **健康评估快照**（14 天 × 5 人 = 75 条）

---

## 3. 功能模块详解

### 3.1 📝 数据录入（7 个 Tab）

系统的数据入口，所有分析功能依赖此模块的数据。

**Tab 1 — 学习记录**
- 录入项：日期、课程、学习时长(0-24h)、专注度自评(0-100)、完成任务数、备注
- 自动生成时间戳，支持查看最近 30 条
- 操作：保存 / 删除选中 / 删除全部
- 保存后自动更新健康评估

**Tab 2 — 成绩录入**
- 录入项：选择课程、平时成绩、期中成绩、期末成绩（可勾选"已参加考试"）
- 未勾选"已参加"时期末成绩置灰，体现缺考情况
- 历史成绩列表，支持删除
- 数据为成绩预测模型提供训练样本

**Tab 3 — 身体健康**
- 运动类型：跑步/球类/健身/瑜伽/游泳/骑行/步行/其他
- 选"游泳""瑜伽""健身"时自动隐藏步数字段（逻辑合理）
- 包含睡眠时长(0-24h)
- 保存后自动更新健康评估

**Tab 4 — 心理健康**
- 心情评分 1-10、压力等级 1-5、焦虑等级 1-5
- 心情日记（文本）
- 最近 30 天历史 + 删除

**Tab 5 — 社交健康**
- 活动类型：社团/聚会/团队项目/志愿/学术交流/其他
- 时长(分钟) + 互动人数
- 最近 30 天历史 + 删除

**Tab 6 — 个人信息**
- 姓名、学号、性别(男/女)、年级、专业、入学年份
- 修改后同步更新侧边栏学生下拉框

**Tab 7 — 课程管理**
- 添加课程：课程代码、名称、学分、学期、必修/选修
- 课程列表展示，支持删除（级联删除成绩/知识点等关联数据）

---

### 3.2 🏠 首页仪表盘

打开应用的第一屏，聚合展示核心数据。

**展示内容**：
- **综合健康度**：数字孪生计算的加权总分（满分 100）
- **风险等级**：LOW(green) / MEDIUM(yellow) / HIGH(orange) / CRITICAL(red)
- **活跃告警**：当前未处理的风险告警数量
- **四维度评分**：学业、身体、心理、社交各维度分数
- **最近告警列表**：显示最近的 5 条风险告警

**自动行为**：每次打开仪表盘，自动调用 DigitalTwin 生成一条健康评估快照，确保健康趋势图表有持续数据。

---

### 3.3 👤 数字孪生

核心理念：为每位学生建立一个"数字影子"，从多维度量化健康状态。

**四维度算法**：

| 维度 | 权重 | 数据来源 |
|------|------|---------|
| 学业健康 | 35% | 课程成绩加权平均（平时×0.3 + 期中×0.3 + 期末×0.4） |
| 身体健康 | 25% | 运动时长/频率 + 睡眠质量 + 步数；无真实数据时从学习规律推算 |
| 心理健康 | 25% | 心情评分 + 压力等级 + 焦虑等级；无数据时从专注度波动推算 |
| 社交健康 | 15% | 社交活跃频率(天/30) + 活动时长 + 互动人数 |

```
综合健康度 = 学业×0.35 + 身体×0.25 + 心理×0.25 + 社交×0.15

风险等级：
  ≥ 80 → LOW（健康）
  ≥ 60 → MEDIUM（一般）
  ≥ 40 → HIGH（关注）
  < 40 → CRITICAL（预警）
```

**可视化**：四维度雷达图 + 趋势折线图 + 历史评估列表。

---

### 3.4 📊 成绩预测

**两种算法可选**：
- **线性回归**（LinearRegression）：简单可解释，数据少时更稳定
- **XGBoost**（GradientBoostingRegressor）：集成学习，数据多时精度更高

**训练流程**：
1. 选择课程（或"全部课程"）
2. 点击"训练模型" → 从数据库拉取该课程的历史成绩（平时+期中→期末）
3. 交叉验证计算 MAE 和残差标准差
4. 模型就绪后，输入平时成绩和期中成绩
5. 点击"预测成绩" → 输出预测值 + 95% 置信区间 + 及格概率

**输出示例**：
```
预测: 82.3 分 | 95%置信区间: [75.1, 89.5] | 及格概率: 94.2% | 低风险
```

**设计要点**：每个课程独立训练模型，不同课程之间数据不混合，保证预测的课程针对性。

---

### 3.5 🧠 知识图谱

**构建方式**：
- 使用 NetworkX 创建有向图（DiGraph）
- 节点 = 知识点，边 = 前置依赖关系
- 每个课程有 6-8 个专属知识点（如"二叉树与遍历""SQL查询语言"等）

**掌握度着色**：
- 🟢 绿色：掌握度 ≥ 80%
- 🟡 黄色：50% ≤ 掌握度 < 80%
- 🔴 红色：掌握度 < 50%

**分析功能**：
- **薄弱节点识别**：筛选掌握度 < 50% 的知识点，按拓扑排序
- **前置依赖链**：双击节点展示到达该知识点的完整学习路径
- **推荐学习顺序**：基于拓扑排序，优先学习前置依赖

**优化**：使用单次查询代替 N+1 模式获取掌握度数据。

---

### 3.6 🤖 AI 学习教练

**对话功能**：
- 基于系统提示词的角色扮演：专业大学成长教练
- 多轮对话记忆（按 session 管理）
- 对话持久化存储

**上下文注入**：自动融合学生的学习数据（健康度、薄弱知识点、风险告警）到对话中。

**快捷操作**：

| 按钮 | 触发内容 |
|------|---------|
| 📚 学习建议 | 基于学习数据生成 3 条本周建议 |
| 💪 情绪疏导 | 压力缓解方法与心理支持 |
| 🎯 生涯规划 | 基于专业和成绩的职业方向建议 |
| 📋 成绩分析 | 薄弱环节分析与提分策略 |
| 🌟 每日激励 | 励志话语与学习动力 |
| 🔄 新对话 | 清空上下文，开始新话题 |

**支持的 LLM 提供商**：

| 提供商 | API 地址 | 费用 |
|--------|---------|------|
| DeepSeek | api.deepseek.com | 免费额度 |
| 智谱 AI (GLM-4) | open.bigmodel.cn | 免费额度 |
| 通义千问 | dashscope.aliyuncs.com | 免费额度 |
| 自定义 | 任意 OpenAI 兼容端点 | — |

**安全**：API Key 使用 Base64 编码存储，不会明文写入 config.json。

---

### 3.7 ⚠ 风险预警

**7 条自动检测规则**：

| 规则 | 触发条件 | 风险等级 |
|------|---------|---------|
| 挂科风险 | 任一课程期末成绩 < 60 | HIGH |
| 成绩下滑 | 连续 3 周学习时长递减 | MEDIUM |
| 健康临界 | 综合健康度 < 40 | CRITICAL |
| 健康下降 | 两周健康度下降 > 15 分 | HIGH |
| 心理倦怠 | 7 天平均专注度 < 30 | MEDIUM |
| 学习不足 | 7 天日均学习 < 2 小时 | MEDIUM |
| 任务完成低 | 7 天日均完成任务 < 1.5 | LOW |

**操作**：标记已处理 / 删除 / 批量删除。

---

### 3.8 📋 学习计划生成器

**生成逻辑**：
1. 获取课程薄弱知识点列表
2. 按剩余天数分阶段分配任务（4 阶段）
3. 避免同一天任务冲突（`alloc_day` 偏移算法）
4. 每个任务带 `done` 标记，支持逐项勾选

**4 个阶段**：
- **阶段 1 — 基础补强**：按薄弱知识点逐日安排复习任务
- **阶段 2 — 综合练习**：每周一次综合性练习
- **阶段 3 — 模拟考试**：考前 3 天模拟
- **阶段 4 — 最终复习**：考前 1 天查漏补缺

**进度追踪**：实际完成 / 总任务数，点击"完成下个任务"自动推进。

---

### 3.9 💡 资源推荐

**三层匹配策略**：
1. **精准匹配**：薄弱知识点名 → 关键词匹配 → 对应资源库（如"二叉树"→"数据"分类→数据结构视频）
2. **课程补充**：课程名关键词匹配（如"数据库原理"→"数据库"分类资源）
3. **扩展兜底**：其他分类各取 1 条 → 通用默认资源

**20 组关键词覆盖**：程序、数据、算法、数学、语言、网络、原理、面向对象、数据库、linux、概念、方法、实践、案例、综合、回顾、web

**去重逻辑**：按课程独立去重（A 课的推荐不影响 B 课），避免越用越少。

**资源类型**：🎬 视频 / 📝 练习 / 📖 文章 / 🎓 课程

---

### 3.10 🎯 专注度监测

**核心指标**：
- **实时专注指数**：当天所有学习记录的平均专注度
- **专注等级**：高度专注(≥80) / 正常(≥60) / 分散(≥40) / 严重分心(<40)
- **趋势**：近 7 天变化方向（改善中/下降中/稳定）

**可视化**：
- 14 天折线图 + 优秀线(80)/正常线(60)
- 30 天热历图（绿=优/蓝=正常/橙=差/红=严重）

---

### 3.11 📁 成长档案

自动生成阶段性学习报告，包含：
- 四维度健康度汇总
- 学习总时长与日均时长
- 任务完成率
- 专注度趋势
- 活跃天数

**报告类型**：周报 / 月报 / 学期报告

---

### 3.12 📈 数据可视化

**4 个图表 Tab**：

| Tab | 内容 | 说明 |
|-----|------|------|
| 学习曲线 | 每日学习时长柱状图 + 7日移动均线 + 专注度折线（双Y轴） | 需学习记录数据 |
| 健康趋势 | 五维度折线（综合/学术/身体/心理/社交）+ 健康线(80)/警戒线(60) | 需健康评估数据 |
| 成绩雷达 | 各课程平时/期中/期末极坐标对比图 | 需成绩数据 |
| 知识热力图 | 课程×知识点矩阵（颜色深浅=掌握度，标注百分比） | 需知识点掌握度 |

---

## 4. 架构设计

### 4.1 三层架构

```
┌─────────────────────────────────────────────────┐
│          表现层 (Presentation Layer)             │
│  MainWindow + 12 个 Widget + 双主题 QSS          │
│  负责：界面渲染、用户交互、图表展示               │
├─────────────────────────────────────────────────┤
│          业务层 (Business Layer)                  │
│  12 个业务类，每个独立封装一种算法或规则           │
│  负责：健康计算、成绩预测、图谱分析、对话管理      │
├─────────────────────────────────────────────────┤
│          数据层 (Data Layer)                      │
│  DatabaseManager (单例) + 11 个 DAO + 12 个 Model │
│  负责：数据库连接、CRUD、数据模型定义              │
└─────────────────────────────────────────────────┘
```

### 4.2 数据流

```
用户操作 → Widget → Business → DAO → DatabaseManager → MySQL
                ↓
          Widget ← Business 返回值 ← DAO 查询结果 ← MySQL
```

### 4.3 设计模式

| 模式 | 应用位置 | 说明 |
|------|---------|------|
| 单例 | DatabaseManager | 全局唯一数据库连接，避免反复握手 |
| DAO | data_layer/dao/ | 每张表一个 DAO 类，封装 SQL 操作 |
| dataclass | data_layer/models.py | 12 个数据模型，类型安全 |
| Enum | RiskLevel | 风险等级枚举，避免魔术字符串 |
| Strategy | GradePredictorV2 | 线性回归/XGBoost 可切换 |

---

## 5. 数据库设计

### 5.1 表结构（15 张表）

#### 核心表

**student — 学生信息**
| 字段 | 类型 | 说明 |
|------|------|------|
| student_id | INT PK AUTO_INCREMENT | 主键 |
| student_no | VARCHAR(20) UNIQUE | 学号 |
| name | VARCHAR(50) | 姓名 |
| gender | ENUM('M','F') | 性别 |
| grade_level | VARCHAR(20) | 年级 |
| major | VARCHAR(100) | 专业 |
| enrollment_year | INT | 入学年份 |

**course — 课程目录**
| 字段 | 类型 | 说明 |
|------|------|------|
| course_id | INT PK | 主键 |
| course_code | VARCHAR(20) UNIQUE | 课程代码 |
| course_name | VARCHAR(100) | 课程名称 |
| credit | DECIMAL(3,1) | 学分 |
| prerequisite_course_id | INT FK | 先修课程(自引用) |
| is_compulsory | BOOLEAN | 是否必修 |

**student_course — 选课与成绩**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| course_id | INT FK | 课程 |
| usual_score | DECIMAL(5,2) | 平时成绩(可空) |
| midterm_score | DECIMAL(5,2) | 期中成绩(可空) |
| final_score | DECIMAL(5,2) | 期末成绩(可空) |
| predicted_final | DECIMAL(5,2) | ML 预测值 |
| UNIQUE(student_id, course_id) | — | 唯一约束 |

**study_record — 每日学习记录**
| 字段 | 类型 | 说明 |
|------|------|------|
| record_id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| study_date | DATE | 日期 |
| study_hours | DECIMAL(4,1) | 学习时长 |
| course_id | INT FK | 关联课程(可空) |
| task_completed | INT | 完成任务数 |
| focus_score | TINYINT | 专注度 0-100 |
| notes | TEXT | 备注 |

**health_assessment — 健康评估快照**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| assessment_date | DATE | 评估日期 |
| academic_score | DECIMAL(5,1) | 学业健康 |
| physical_score | DECIMAL(5,1) | 身体健康 |
| mental_score | DECIMAL(5,1) | 心理健康 |
| social_score | DECIMAL(5,1) | 社交健康 |
| overall_health | DECIMAL(5,1) | 综合健康度 |
| risk_level | ENUM | LOW/MEDIUM/HIGH/CRITICAL |

**knowledge_point — 知识点节点**
| 字段 | 类型 | 说明 |
|------|------|------|
| kp_id | INT PK | 主键 |
| course_id | INT FK | 所属课程 |
| kp_name | VARCHAR(100) | 知识点名称 |
| parent_kp_id | INT FK | 前置知识点(自引用) |
| difficulty | TINYINT | 难度 1-5 |
| weight | DECIMAL(3,2) | 权重 |

**knowledge_mastery — 知识点掌握度**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| kp_id | INT FK | 知识点 |
| mastery_level | DECIMAL(5,1) | 掌握度 0-100 |
| last_assessed | DATE | 最近评估日期 |
| UNIQUE(student_id, kp_id) | — | 唯一约束 |

**risk_alert — 风险告警**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| alert_type | VARCHAR(50) | 告警类型 |
| risk_level | ENUM | 风险等级 |
| alert_message | TEXT | 告警详情 |
| rule_triggered | VARCHAR(100) | 触发的规则名 |
| is_resolved | BOOLEAN | 是否已处理 |
| created_at | DATETIME | 创建时间 |

**ai_coach_log — AI 对话日志**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| session_id | VARCHAR(20) | 会话 ID |
| role | ENUM('user','assistant','system') | 角色 |
| message | TEXT | 消息内容 |
| tokens_used | INT | Token 消耗 |

#### V2 扩展表

**study_plan — 学习计划**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| subject | VARCHAR(100) | 课程名 |
| goal_score | DECIMAL(5,1) | 目标分数 |
| exam_date | DATE | 考试日期 |
| plan_content | LONGTEXT(JSON) | 任务列表 |
| progress | DECIMAL(5,1) | 完成进度 |
| status | VARCHAR(20) | active/completed/cancelled |

**resource_recommendation — 资源推荐**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| kp_id | INT FK | 关联知识点(可空) |
| resource_type | VARCHAR(20) | video/exercise/article/course |
| title | VARCHAR(200) | 资源标题 |
| url | VARCHAR(500) | 资源链接 |
| reason | TEXT | 推荐理由 |
| is_completed | BOOLEAN | 是否完成 |

**growth_report — 成长档案**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT PK | 主键 |
| student_id | INT FK | 学生 |
| report_type | VARCHAR(20) | weekly/monthly/semester |
| detail | LONGTEXT(JSON) | 报告内容 |
| created_at | DATETIME | 生成时间 |

#### V3 健康扩展表

**physical_health_record — 身体健康**
- student_id, record_date, exercise_type, exercise_duration, sleep_hours, steps

**mental_health_record — 心理健康**
- student_id, record_date, mood_score(1-10), stress_level(1-5), anxiety_level(1-5), notes

**social_health_record — 社交健康**
- student_id, record_date, activity_type, duration_minutes, interaction_count

### 5.2 ER 关系图

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

## 6. 配置说明

### 6.1 config.py

```python
# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "xxx",
    "database": "student_growth_platform",
    "charset": "utf8mb4",
}

# LLM 配置（可运行时在 AI 教练页面修改）
LLM_CONFIG = {
    "provider": "deepseek",  # deepseek / zhipu / qwen / custom
    "api_key": "...",
    "api_url": "https://api.deepseek.com/v1/chat/completions",
    "model": "deepseek-chat",
}

# 健康度权重
HEALTH_WEIGHTS = {"academic": 0.35, "physical": 0.25, "mental": 0.25, "social": 0.15}
RISK_THRESHOLDS = {"low": 80, "medium": 60, "high": 40}
```

### 6.2 config.json（运行时覆盖）

程序启动时自动加载项目目录下的 `config.json`，可覆盖 `config.py` 中的默认值。AI 教练页面修改 API Key 后会自动写入此文件（Key 经 Base64 编码存储）。

---

## 7. 开发指南

### 7.1 添加新功能

1. `data_layer/models.py` — 定义数据模型
2. `data_layer/dao/` — 创建 DAO 类（继承 DatabaseManager 单例）
3. `business_layer/` — 实现业务逻辑类
4. `presentation_layer/widgets/` — 创建 UI Widget
5. `presentation_layer/main_window.py` — 注册到导航

### 7.2 运行测试

```batch
python -m pytest tests/ -v
```

### 7.3 打包分发

```batch
python -c "..." # 见打包脚本
```

排除目录：`__pycache__` `.vscode` `.claude` `venv` `dist` `.git` `build`

---

## 8. 常见问题

**Q: 启动提示 "Can't connect to MySQL"**
A: MySQL 未启动。使用 `启动.py`（自动启动），或手动运行 `启动.bat`。

**Q: 图表中文显示方框**
A: 安装 Microsoft YaHei 或 SimHei 中文字体。

**Q: AI 教练无回复**
A: 未配置 API Key。打开 AI 教练页面 → 选择 DeepSeek → 注册获取 Key → 粘贴 → 测试连接 → 保存。

**Q: 资源推荐为空**
A: 先点"删除全部"清空旧推荐，再切换不同课程重新推荐。

**Q: 健康趋势无数据**
A: 打开"首页仪表盘"触发首次评估。之后每次保存健康数据自动更新。

**Q: 成绩预测报"数据不足"**
A: 该课程需要至少 3 条完整成绩（平时+期中+期末都有值）。在"数据录入 → 成绩录入"补充数据。

**Q: 如何切换学生**
A: 侧边栏顶部下拉框选择不同学生。

**Q: 如何重置数据库**
```batch
python init_database.py && python generate_mock_data.py
```

---

**版本**：v2.1 | **日期**：2026-06-03 | **作者**：Python 课程设计
