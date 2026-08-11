"""生成项目计划书 Word 文档（纯文本排版版）."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path


CN_FONT = "微软雅黑"


def _set_run_font(run, size=10.5, bold=False):
    """设置 run 字体."""
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = CN_FONT
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:eastAsia"), CN_FONT)
    r_fonts.set(qn("w:ascii"), CN_FONT)
    r_fonts.set(qn("w:hAnsi"), CN_FONT)


def _add_para(doc, text="", size=10.5, bold=False, alignment=WD_ALIGN_PARAGRAPH.LEFT,
              space_before=0, space_after=6, line_spacing=1.5, indent=None):
    """添加段落."""
    p = doc.add_paragraph()
    p.alignment = alignment
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if indent is not None:
        pf.left_indent = Cm(indent)
    if text:
        run = p.add_run(text)
        _set_run_font(run, size=size, bold=bold)
    return p


def _add_h1(doc, text):
    """一级标题（章节标题）."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(18)
    pf.space_after = Pt(10)
    pf.line_spacing = 1.5
    run = p.add_run(text)
    _set_run_font(run, size=16, bold=True)


def _add_h2(doc, text):
    """二级标题."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(12)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    run = p.add_run(text)
    _set_run_font(run, size=12, bold=True)


def _add_bullet(doc, text, indent=0.8):
    """添加项目符号."""
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Cm(indent)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.5
    run = p.add_run("• " + text)
    _set_run_font(run, size=10.5)


def _add_text_table(doc, headers, rows, col_widths=None):
    """纯文本表格（无颜色，仅边框）."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = 1  # 居中

    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = Cm(w)

    # 表头
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        if col_widths:
            cell.width = Cm(col_widths[i])
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(h)
        _set_run_font(run, size=10, bold=True)

    # 数据行
    for row_idx, row_data in enumerate(rows, 1):
        for col_idx, val in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            if col_widths:
                cell.width = Cm(col_widths[col_idx])
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if col_idx > 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.3
            run = p.add_run(str(val))
            _set_run_font(run, size=9.5)

    _add_para(doc, "", size=4, space_after=0)


def _setup_page(doc):
    """设置页面边距."""
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)


def build_docx(output_path: str) -> str:
    """生成项目计划书 Word 文档（纯文本排版）."""
    doc = Document()

    # 默认样式
    style = doc.styles["Normal"]
    style.font.name = CN_FONT
    style.font.size = Pt(10.5)
    r_pr = style.element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:eastAsia"), CN_FONT)

    _setup_page(doc)

    # ============================================================
    # 封面
    # ============================================================
    _add_para(doc, "", size=14, space_after=0)
    _add_para(doc, "", size=14, space_after=0)
    _add_para(doc, "", size=14, space_after=0)

    _add_para(doc, "大学生智能成长平台", size=28, bold=True,
              alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)
    _add_para(doc, "项目计划书", size=18, bold=False,
              alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)

    # 封面信息（纯文本）
    cover_lines = [
        "项目名称：大学生智能成长平台",
        "项目类型：Python 程序设计课程设计",
        "项目周期：8 周",
        "文档版本：v1.0",
        "编制日期：2026 年 8 月 11 日",
    ]
    for line in cover_lines:
        _add_para(doc, line, size=12, alignment=WD_ALIGN_PARAGRAPH.CENTER,
                  space_after=8, line_spacing=2.0)

    doc.add_page_break()

    # ============================================================
    # 目录
    # ============================================================
    _add_para(doc, "目  录", size=18, bold=True,
              alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=20)

    toc_items = [
        "一、项目概述",
        "二、项目目标",
        "三、功能模块设计",
        "四、技术架构方案",
        "五、项目进度安排",
        "六、关键技术难点与解决方案",
        "七、风险评估与应对",
        "八、测试计划",
        "九、交付物清单",
        "十、团队分工与协作",
    ]
    for item in toc_items:
        _add_para(doc, item, size=11, indent=1.5, space_after=8, line_spacing=1.8)

    doc.add_page_break()

    # ============================================================
    # 一、项目概述
    # ============================================================
    _add_h1(doc, "一、项目概述")

    _add_para(doc, "项目名称：大学生智能成长平台", size=10.5, space_after=4)
    _add_para(doc, "项目类型：Python 程序设计课程设计", size=10.5, space_after=4)
    _add_para(doc, "项目周期：8 周", size=10.5, space_after=4)
    _add_para(doc, "项目背景：", size=10.5, bold=True, space_after=4)
    _add_para(doc, "当前高校学生普遍缺乏系统化的学习管理和健康追踪工具，传统教务系统仅提供成绩查询，无法提供个性化分析与智能建议。本项目旨在构建一个集学习管理、四维健康评估、机器学习预测、AI 辅助决策于一体的综合性平台，助力大学生全面成长。",
              size=10.5, indent=0.5)

    # ============================================================
    # 二、项目目标
    # ============================================================
    _add_h1(doc, "二、项目目标")

    _add_h2(doc, "2.1 核心目标")
    goals = [
        "构建数字孪生健康评估模型，量化学生学业、身体、心理、社交四维度状态",
        "实现机器学习成绩预测，准确率达到 85% 以上",
        "接入大语言模型提供个性化 AI 教练服务",
        "构建课程知识图谱，可视化展示知识依赖与掌握程度",
        "提供桌面 GUI 与 Web 双界面，满足不同使用场景",
    ]
    for i, g in enumerate(goals, 1):
        _add_para(doc, f"{i}. {g}", size=10.5, indent=0.8, space_after=3)

    _add_h2(doc, "2.2 量化指标")
    _add_text_table(doc, ["指标项", "目标值"],
                    [
                        ("支持课程数", "≥ 5 门"),
                        ("学习记录存储", "≥ 100 条"),
                        ("健康评估响应时间", "< 2 秒"),
                        ("成绩预测最少训练数据", "≥ 3 条"),
                        ("风险预警规则数", "≥ 7 条"),
                        ("AI 教练支持模型数", "≥ 3 种"),
                    ],
                    col_widths=[8, 5])

    # ============================================================
    # 三、功能模块设计
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "三、功能模块设计")

    _add_para(doc, "本项目共包含 12 个核心功能模块，覆盖数据采集、智能分析、可视化展示、AI 辅助全流程：",
              size=10.5, space_after=8)

    _add_text_table(doc, ["编号", "模块名称", "功能说明"],
                    [
                        ("3.1", "数据录入模块", "学习记录、成绩、健康（身体/心理/社交）、个人信息、课程管理"),
                        ("3.2", "仪表盘模块", "综合健康度、风险等级、活跃告警、四维度评分概览"),
                        ("3.3", "数字孪生模块", "学业/身体/心理/社交四维度计算，雷达图+趋势折线图"),
                        ("3.4", "成绩预测模块", "线性回归/梯度提升两种算法，置信区间与及格概率输出"),
                        ("3.5", "知识图谱模块", "NetworkX 有向图构建，掌握度着色，薄弱点识别"),
                        ("3.6", "AI 学习教练模块", "LLM 对话，上下文注入，多轮记忆，快捷操作"),
                        ("3.7", "风险预警模块", "7 条检测规则，四级风险分级，自动告警与解除"),
                        ("3.8", "学习计划模块", "薄弱点驱动，四阶段任务分配，进度追踪"),
                        ("3.9", "资源推荐模块", "三层匹配策略，按课程去重，多类型资源"),
                        ("3.10", "专注度监测模块", "实时专注指数，14 天趋势，30 天热力图"),
                        ("3.11", "成长档案模块", "周报/月报/学期报告自动生成"),
                        ("3.12", "数据可视化模块", "学习曲线、健康趋势、成绩雷达、知识热力图"),
                    ],
                    col_widths=[1.3, 3.7, 11])

    # ============================================================
    # 四、技术架构方案
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "四、技术架构方案")

    _add_h2(doc, "4.1 四层架构")
    _add_para(doc, "项目采用四层架构设计，实现业务逻辑与界面的完全解耦，桌面 GUI 与 Web 界面共享同一套后端：",
              size=10.5, space_after=8)

    _add_text_table(doc, ["层次", "技术栈", "职责"],
                    [
                        ("数据层", "MySQL 8.4 + pymysql + DAO 模式 + threading.local", "数据库连接、CRUD 操作、数据模型定义"),
                        ("业务层", "Python 3.12 + scikit-learn + NetworkX + pandas", "健康计算、成绩预测、图谱分析、对话管理"),
                        ("服务层", "FastAPI + Uvicorn + Pydantic + 依赖注入", "HTTP 接口、请求校验、依赖注入"),
                        ("表现层", "PyQt5 + React 19 + TypeScript + ECharts + Tailwind", "界面渲染、用户交互、图表展示"),
                    ],
                    col_widths=[2, 8, 6])

    _add_h2(doc, "4.2 数据库设计（15 张表）")
    _add_text_table(doc, ["类别", "表名", "说明"],
                    [
                        ("基础表", "student", "学生信息"),
                        ("基础表", "course", "课程目录"),
                        ("基础表", "student_course", "选课与成绩"),
                        ("学习表", "study_record", "每日学习记录"),
                        ("学习表", "knowledge_point", "知识点节点"),
                        ("学习表", "knowledge_mastery", "知识点掌握度"),
                        ("健康表", "health_assessment", "健康评估快照"),
                        ("健康表", "physical_health_record", "身体健康记录"),
                        ("健康表", "mental_health_record", "心理健康记录"),
                        ("健康表", "social_health_record", "社交健康记录"),
                        ("智能表", "risk_alert", "风险告警"),
                        ("智能表", "ai_coach_log", "AI 对话日志"),
                        ("智能表", "study_plan", "学习计划"),
                        ("智能表", "resource_recommendation", "资源推荐"),
                        ("智能表", "growth_report", "成长档案"),
                    ],
                    col_widths=[2.5, 6.5, 7])

    # ============================================================
    # 五、项目进度安排
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "五、项目进度安排")

    _add_para(doc, "项目总周期 8 周，按敏捷开发模式分阶段交付：",
              size=10.5, space_after=8)

    _add_text_table(doc, ["周次", "阶段", "任务内容", "交付物"],
                    [
                        ("第 1 周", "需求分析与设计", "需求分析、技术选型、数据库设计与 ER 图", "需求文档、ER 图、数据库脚本"),
                        ("第 2 周", "数据层开发", "DatabaseManager、11 个 DAO 类、12 个数据模型", "数据层代码、单元测试"),
                        ("第 3 周", "业务层核心开发", "数字孪生健康评估、成绩预测、知识图谱模块", "核心业务模块、算法验证"),
                        ("第 4 周", "业务层进阶开发", "风险预警、AI 教练、学习计划、资源推荐", "完整业务层代码"),
                        ("第 5 周", "桌面 GUI 开发", "PyQt5 主窗口、12 个功能页面、双主题 QSS", "桌面端可运行程序"),
                        ("第 6 周", "Web 后端开发", "FastAPI 19 个路由、Pydantic Schema、依赖注入", "Web API 接口文档"),
                        ("第 7 周", "Web 前端开发", "React 15 个页面、ECharts 图表、路由守卫、状态管理", "前端页面可访问"),
                        ("第 8 周", "集成与交付", "集成测试、性能优化、PyInstaller 打包、文档编写、答辩", "EXE 安装包、完整文档"),
                    ],
                    col_widths=[1.6, 3, 6, 5.4])

    # ============================================================
    # 六、关键技术难点与解决方案
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "六、关键技术难点与解决方案")

    _add_text_table(doc, ["编号", "技术难点", "问题描述", "解决方案"],
                    [
                        ("6.1", "多线程数据库连接安全", "并发请求下共享单连接可能导致 500 错误", "使用 threading.local() 实现线程隔离连接"),
                        ("6.2", "成绩预测数据不足", "新课程数据少时模型训练效果差", "支持线性回归与梯度提升策略切换"),
                        ("6.3", "API Key 安全存储", "配置文件明文存储 API Key 存在风险", "Base64 编码存储，运行时解码"),
                        ("6.4", "双界面共享业务逻辑", "桌面 GUI 与 Web 界面逻辑重复开发", "业务层独立，统一调用 Business 类接口"),
                        ("6.5", "知识图谱可视化布局", "知识点多且关系复杂，布局易混乱", "NetworkX spring_layout + 掌握度着色"),
                    ],
                    col_widths=[1.2, 3.3, 5.5, 6])

    # ============================================================
    # 七、风险评估与应对
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "七、风险评估与应对")

    _add_text_table(doc, ["编号", "风险类型", "风险描述", "应对措施"],
                    [
                        ("7.1", "技术风险", "机器学习预测精度不达标", "增加梯度提升集成算法，支持交叉验证调参"),
                        ("7.2", "进度风险", "双界面开发工作量大", "优先完成桌面 GUI，Web 界面并行开发"),
                        ("7.3", "依赖风险", "大语言模型 API 可用性", "支持多家提供商切换，兼容自定义端点"),
                        ("7.4", "数据风险", "数据库迁移失败", "分版本 SQL 脚本，幂等执行，可回滚"),
                    ],
                    col_widths=[1.2, 2.5, 5, 7.3])

    # ============================================================
    # 八、测试计划
    # ============================================================
    _add_h1(doc, "八、测试计划")

    _add_text_table(doc, ["测试类型", "测试内容", "通过标准"],
                    [
                        ("单元测试", "数据库连接、数字孪生、成绩预测、知识图谱、风险预警、AI 教练", "6 个测试模块全部通过"),
                        ("集成测试", "GUI Widget 与业务层联动、Web API 端到端请求", "核心流程无异常"),
                        ("性能测试", "健康评估响应时间、批量导入 100 条学习记录", "响应 < 2 秒，无内存泄漏"),
                        ("兼容性测试", "Windows 10/11 桌面端、Chrome/Edge 浏览器", "主流环境均可正常运行"),
                    ],
                    col_widths=[2.5, 8, 5.5])

    # ============================================================
    # 九、交付物清单
    # ============================================================
    doc.add_page_break()
    _add_h1(doc, "九、交付物清单")

    _add_text_table(doc, ["编号", "交付物", "说明"],
                    [
                        ("9.1", "源代码", "四层架构完整代码（business_layer / data_layer / presentation_layer / web / frontend）"),
                        ("9.2", "数据库脚本", "SQL 建表脚本（schema / v2_extend / v3_health_extend）+ 演示数据"),
                        ("9.3", "桌面端程序", "PyInstaller 打包的单文件 EXE（含 logo 图标），约 143 MB"),
                        ("9.4", "Web 端", "FastAPI 后端源码 + React 前端构建产物"),
                        ("9.5", "文档", "README 使用说明 + 项目计划书 + 架构设计文档"),
                        ("9.6", "配置文件", "config.example.json 配置模板 + build.spec 打包配置"),
                    ],
                    col_widths=[1.2, 3, 11.8])

    # ============================================================
    # 十、团队分工与协作
    # ============================================================
    _add_h1(doc, "十、团队分工与协作")

    _add_text_table(doc, ["角色", "职责", "主要产出"],
                    [
                        ("后端开发工程师", "数据层 + 业务层 + Web API", "DatabaseManager、DAO、Business 类、FastAPI 路由"),
                        ("前端开发工程师", "桌面 GUI + Web 前端界面", "PyQt5 Widget、React 页面、ECharts 图表、主题样式"),
                        ("算法开发工程师", "成绩预测模型、知识图谱算法、风险预警规则", "机器学习模型、NetworkX 图谱、规则引擎"),
                        ("测试运维工程师", "单元测试、打包部署、文档编写", "pytest 测试用例、PyInstaller 打包、README 文档"),
                    ],
                    col_widths=[3.5, 5, 7.5])

    # ---------- 文末 ----------
    _add_para(doc, "", size=12, space_after=20)
    _add_para(doc, "—— 文档结束 ——", size=10,
              alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    _add_para(doc, "版本 v1.0    2026-08-11", size=10,
              alignment=WD_ALIGN_PARAGRAPH.CENTER)

    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    output = str(Path(__file__).resolve().parent.parent / "docs" / "项目计划书.docx")
    result = build_docx(output)
    print(f"Word 文档生成成功：{result}")
