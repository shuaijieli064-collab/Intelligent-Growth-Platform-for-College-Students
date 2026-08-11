"""直接生成项目计划书 PDF（使用 reportlab）- 优化布局版."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, Image, Flowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from pathlib import Path
import os


# ============================================================
# 字体注册
# ============================================================
def _register_chinese_fonts():
    """注册系统中文字体，解决中文乱码问题."""
    font_paths = {
        "MSYH": r"C:\Windows\Fonts\msyh.ttc",
        "MSYHBD": r"C:\Windows\Fonts\msyhbd.ttc",
        "SimSun": r"C:\Windows\Fonts\simsun.ttc",
        "SimHei": r"C:\Windows\Fonts\simhei.ttf",
    }
    registered = {}
    for name, path in font_paths.items():
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered[name] = path
            except Exception as e:
                print(f"警告：注册字体 {name} 失败：{e}")
    if "MSYH" in registered and "MSYHBD" in registered:
        addMapping("MSYH", 0, 0, "MSYH")
        addMapping("MSYH", 1, 0, "MSYHBD")
    return registered


_fonts = _register_chinese_fonts()
if "MSYH" in _fonts:
    BASE_FONT = "MSYH"
    BOLD_FONT = "MSYHBD" if "MSYHBD" in _fonts else "MSYH"
elif "SimSun" in _fonts:
    BASE_FONT = "SimSun"
    BOLD_FONT = "SimSun"
elif "SimHei" in _fonts:
    BASE_FONT = "SimHei"
    BOLD_FONT = "SimHei"
else:
    BASE_FONT = "Helvetica"
    BOLD_FONT = "Helvetica-Bold"
    print("警告：未找到中文字体")


# ============================================================
# 色彩体系
# ============================================================
COLOR_PRIMARY = colors.HexColor("#1a3a6b")       # 主色：深蓝
COLOR_SECONDARY = colors.HexColor("#2c5282")     # 次色：中蓝
COLOR_ACCENT = colors.HexColor("#3182ce")        # 强调：亮蓝
COLOR_LIGHT = colors.HexColor("#ebf4ff")         # 浅蓝背景
COLOR_LIGHTER = colors.HexColor("#f7f9fc")       # 更浅背景（斑马纹）
COLOR_TEXT = colors.HexColor("#2d3748")          # 正文文字
COLOR_MUTED = colors.HexColor("#718096")         # 次要文字
COLOR_BORDER = colors.HexColor("#cbd5e0")        # 边框
COLOR_SUCCESS = colors.HexColor("#38a169")       # 成功绿
COLOR_WARNING = colors.HexColor("#d69e2e")       # 警告黄
COLOR_DANGER = colors.HexColor("#e53e3e")        # 危险红


# ============================================================
# 自定义 Flowable：章节标题色块
# ============================================================
class ChapterHeader(Flowable):
    """章节标题色块：左侧色条 + 章节编号 + 标题文字."""

    def __init__(self, number, title, width=17 * cm):
        Flowable.__init__(self)
        self.number = number
        self.title = title
        self.width = width
        self.height = 1.1 * cm

    def draw(self):
        c = self.canv
        # 左侧色条
        c.setFillColor(COLOR_PRIMARY)
        c.rect(0, 0, 0.15 * cm, self.height, fill=1, stroke=0)
        # 章节编号色块
        c.setFillColor(COLOR_PRIMARY)
        c.roundRect(0.3 * cm, 0.1 * cm, 1.5 * cm, 0.9 * cm, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont(BOLD_FONT, 12)
        c.drawCentredString(1.05 * cm, 0.4 * cm, self.number)
        # 标题文字
        c.setFillColor(COLOR_PRIMARY)
        c.setFont(BOLD_FONT, 14)
        c.drawString(2.1 * cm, 0.35 * cm, self.title)
        # 底部细线
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.line(0, 0, self.width, 0)


# ============================================================
# 页眉页脚
# ============================================================
def _draw_header_footer(canvas, doc):
    """绘制页眉页脚."""
    canvas.saveState()
    page_num = canvas.getPageNumber()

    if page_num > 1:
        # 页眉
        canvas.setFont(BASE_FONT, 8)
        canvas.setFillColor(COLOR_MUTED)
        canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "大学生智能成长平台")
        canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, "项目计划书")
        # 页眉横线
        canvas.setStrokeColor(COLOR_BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)

        # 页脚横线
        canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
        # 页码
        canvas.setFont(BASE_FONT, 8)
        canvas.setFillColor(COLOR_MUTED)
        canvas.drawCentredString(A4[0] / 2, 1 * cm, f"— {page_num} —")
        canvas.drawString(2 * cm, 1 * cm, "v1.0")
        canvas.drawRightString(A4[0] - 2 * cm, 1 * cm, "2026-08-11")

    canvas.restoreState()


# ============================================================
# 表格样式生成器
# ============================================================
def _make_table_style(header_bg=COLOR_PRIMARY, zebra=True, font_size=9):
    """生成统一的表格样式."""
    style = [
        # 表头
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), BOLD_FONT),
        ("FONTSIZE", (0, 0), (-1, 0), font_size + 0.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
        # 数据行
        ("FONTNAME", (0, 1), (-1, -1), BASE_FONT),
        ("FONTSIZE", (0, 1), (-1, -1), font_size),
        ("TEXTCOLOR", (0, 1), (-1, -1), COLOR_TEXT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]
    if zebra:
        style.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COLOR_LIGHTER]))
    return TableStyle(style)


# ============================================================
# 主构建函数
# ============================================================
def build_pdf(output_path: str) -> str:
    """生成项目计划书 PDF."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="大学生智能成长平台 - 项目计划书",
        author="大学生智能成长平台项目组",
    )

    styles = getSampleStyleSheet()

    # ---------- 样式定义 ----------
    cover_title = ParagraphStyle(
        "CoverTitle", parent=styles["Title"], fontName=BOLD_FONT,
        fontSize=32, textColor=COLOR_PRIMARY, alignment=TA_CENTER,
        spaceAfter=10, leading=42,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle", parent=styles["Title"], fontName=BASE_FONT,
        fontSize=16, textColor=COLOR_SECONDARY, alignment=TA_CENTER,
        spaceAfter=30, leading=22,
    )
    cover_info = ParagraphStyle(
        "CoverInfo", parent=styles["Normal"], fontName=BASE_FONT,
        fontSize=11, textColor=COLOR_MUTED, alignment=TA_CENTER,
        leading=20,
    )
    toc_title = ParagraphStyle(
        "TocTitle", parent=styles["Heading2"], fontName=BOLD_FONT,
        fontSize=18, textColor=COLOR_PRIMARY, alignment=TA_CENTER,
        spaceAfter=25,
    )
    toc_item = ParagraphStyle(
        "TocItem", parent=styles["Normal"], fontName=BASE_FONT,
        fontSize=11, textColor=COLOR_TEXT, leftIndent=20, leading=24,
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"], fontName=BOLD_FONT,
        fontSize=12, textColor=COLOR_SECONDARY, spaceBefore=12, spaceAfter=6, leading=18,
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"], fontName=BASE_FONT,
        fontSize=10.5, leading=18, textColor=COLOR_TEXT,
        alignment=TA_JUSTIFY, spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=body_style, leftIndent=22, bulletIndent=8, spaceAfter=3,
    )
    info_label_style = ParagraphStyle(
        "InfoLabel", parent=body_style, fontSize=10.5, leading=20,
    )
    footer_style = ParagraphStyle(
        "Footer", parent=body_style, alignment=TA_CENTER, fontSize=9,
        textColor=COLOR_MUTED,
    )

    story = []

    # ============================================================
    # 封面页
    # ============================================================
    story.append(Spacer(1, 4 * cm))
    # 顶部装饰线
    story.append(HRFlowable(width="60%", thickness=2, color=COLOR_PRIMARY,
                            hAlign="CENTER", spaceAfter=30))
    story.append(Paragraph("大学生智能成长平台", cover_title))
    story.append(Paragraph("项目计划书", cover_subtitle))
    # 中间装饰线
    story.append(HRFlowable(width="40%", thickness=1, color=COLOR_ACCENT,
                            hAlign="CENTER", spaceAfter=50))

    # 封面信息表
    cover_data = [
        ["项目名称", "大学生智能成长平台"],
        ["项目类型", "Python 程序设计课程设计"],
        ["项目周期", "8 周"],
        ["文档版本", "v1.0"],
        ["编制日期", "2026 年 8 月 11 日"],
    ]
    cover_table = Table(cover_data, colWidths=[4 * cm, 8 * cm], hAlign="CENTER")
    cover_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), BOLD_FONT),
        ("FONTNAME", (1, 0), (1, -1), BASE_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (0, -1), COLOR_PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), COLOR_TEXT),
        ("BACKGROUND", (0, 0), (0, -1), COLOR_LIGHT),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (1, 0), (1, -1), 15),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, COLOR_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.8, COLOR_PRIMARY),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 60))
    # 底部装饰线
    story.append(HRFlowable(width="60%", thickness=2, color=COLOR_PRIMARY,
                            hAlign="CENTER"))
    story.append(PageBreak())

    # ============================================================
    # 目录页
    # ============================================================
    story.append(Paragraph("目 录", toc_title))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY,
                            spaceAfter=20))
    toc_items = [
        ("一、项目概述", "03"),
        ("二、项目目标", "03"),
        ("三、功能模块设计", "04"),
        ("四、技术架构方案", "05"),
        ("五、项目进度安排", "06"),
        ("六、关键技术难点与解决方案", "07"),
        ("七、风险评估与应对", "08"),
        ("八、测试计划", "08"),
        ("九、交付物清单", "09"),
        ("十、团队分工与协作", "09"),
    ]
    for title, page in toc_items:
        dots = "·" * max(1, (55 - len(title) - len(page)))
        story.append(Paragraph(f"{title} <font color='#cbd5e0'>{dots}</font> {page}", toc_item))
    story.append(PageBreak())

    # ============================================================
    # 一、项目概述
    # ============================================================
    story.append(ChapterHeader("01", "项目概述"))
    story.append(Spacer(1, 12))

    overview_data = [
        ["项目名称", "大学生智能成长平台"],
        ["项目类型", "Python 程序设计课程设计"],
        ["项目周期", "8 周"],
        ["项目背景", "当前高校学生普遍缺乏系统化的学习管理和健康追踪工具，传统教务系统仅提供成绩查询，无法提供个性化分析与智能建议。本项目旨在构建一个集学习管理、四维健康评估、机器学习预测、AI辅助决策于一体的综合性平台，助力大学生全面成长。"],
    ]
    overview_table = Table(overview_data, colWidths=[3 * cm, 14 * cm])
    overview_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), BOLD_FONT),
        ("FONTNAME", (1, 0), (1, -1), BASE_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), COLOR_PRIMARY),
        ("TEXTCOLOR", (1, 0), (1, -1), COLOR_TEXT),
        ("BACKGROUND", (0, 0), (0, -1), COLOR_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER),
    ]))
    story.append(overview_table)

    # ============================================================
    # 二、项目目标
    # ============================================================
    story.append(Spacer(1, 20))
    story.append(ChapterHeader("02", "项目目标"))
    story.append(Spacer(1, 12))

    story.append(Paragraph("2.1 核心目标", h3_style))
    goals = [
        "构建数字孪生健康评估模型，量化学生学业、身体、心理、社交四维度状态",
        "实现机器学习成绩预测，准确率达到 85% 以上",
        "接入大语言模型提供个性化 AI 教练服务",
        "构建课程知识图谱，可视化展示知识依赖与掌握程度",
        "提供桌面 GUI 与 Web 双界面，满足不同使用场景",
    ]
    for i, g in enumerate(goals, 1):
        story.append(Paragraph(f"<font color='#3182ce'><b>{i}.</b></font> {g}", bullet_style))

    story.append(Paragraph("2.2 量化指标", h3_style))
    metric_data = [
        ["指标项", "目标值"],
        ["支持课程数", "≥ 5 门"],
        ["学习记录存储", "≥ 100 条"],
        ["健康评估响应时间", "< 2 秒"],
        ["成绩预测最少训练数据", "≥ 3 条"],
        ["风险预警规则数", "≥ 7 条"],
        ["AI 教练支持模型数", "≥ 3 种"],
    ]
    metric_table = Table(metric_data, colWidths=[8 * cm, 4 * cm], hAlign="LEFT")
    metric_table.setStyle(_make_table_style(font_size=10))
    story.append(metric_table)

    # ============================================================
    # 三、功能模块设计
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("03", "功能模块设计"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("本项目共包含 12 个核心功能模块，覆盖数据采集、智能分析、可视化展示、AI 辅助全流程：", body_style))
    story.append(Spacer(1, 8))

    module_data = [
        ["编号", "模块名称", "功能说明"],
        ["3.1", "数据录入模块", "学习记录、成绩、健康（身体/心理/社交）、个人信息、课程管理"],
        ["3.2", "仪表盘模块", "综合健康度、风险等级、活跃告警、四维度评分概览"],
        ["3.3", "数字孪生模块", "学业/身体/心理/社交四维度计算，雷达图+趋势折线图"],
        ["3.4", "成绩预测模块", "线性回归/梯度提升两种算法，置信区间与及格概率输出"],
        ["3.5", "知识图谱模块", "NetworkX 有向图构建，掌握度着色，薄弱点识别"],
        ["3.6", "AI 学习教练模块", "LLM 对话，上下文注入，多轮记忆，快捷操作"],
        ["3.7", "风险预警模块", "7 条检测规则，四级风险分级，自动告警与解除"],
        ["3.8", "学习计划模块", "薄弱点驱动，四阶段任务分配，进度追踪"],
        ["3.9", "资源推荐模块", "三层匹配策略，按课程去重，多类型资源"],
        ["3.10", "专注度监测模块", "实时专注指数，14 天趋势，30 天热力图"],
        ["3.11", "成长档案模块", "周报/月报/学期报告自动生成"],
        ["3.12", "数据可视化模块", "学习曲线、健康趋势、成绩雷达、知识热力图"],
    ]
    module_table = Table(module_data, colWidths=[1.3 * cm, 3.7 * cm, 12 * cm])
    module_table.setStyle(_make_table_style(font_size=9))
    story.append(module_table)

    # ============================================================
    # 四、技术架构方案
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("04", "技术架构方案"))
    story.append(Spacer(1, 12))

    story.append(Paragraph("4.1 四层架构", h3_style))
    story.append(Paragraph("项目采用四层架构设计，实现业务逻辑与界面的完全解耦，桌面 GUI 与 Web 界面共享同一套后端：", body_style))
    story.append(Spacer(1, 6))

    arch_data = [
        ["层次", "技术栈", "职责"],
        ["数据层", "MySQL 8.4 + pymysql + DAO 模式 + threading.local", "数据库连接、CRUD 操作、数据模型定义"],
        ["业务层", "Python 3.12 + scikit-learn + NetworkX + pandas", "健康计算、成绩预测、图谱分析、对话管理"],
        ["服务层", "FastAPI + Uvicorn + Pydantic + 依赖注入", "HTTP 接口、请求校验、依赖注入"],
        ["表现层", "PyQt5 + React 19 + TypeScript + ECharts + Tailwind", "界面渲染、用户交互、图表展示"],
    ]
    arch_table = Table(arch_data, colWidths=[2 * cm, 8 * cm, 7 * cm])
    arch_table.setStyle(_make_table_style(font_size=9.5))
    story.append(arch_table)

    story.append(Paragraph("4.2 数据库设计（15 张表）", h3_style))
    db_data = [
        ["类别", "表名", "说明"],
        ["基础表", "student", "学生信息"],
        ["基础表", "course", "课程目录"],
        ["基础表", "student_course", "选课与成绩"],
        ["学习表", "study_record", "每日学习记录"],
        ["学习表", "knowledge_point", "知识点节点"],
        ["学习表", "knowledge_mastery", "知识点掌握度"],
        ["健康表", "health_assessment", "健康评估快照"],
        ["健康表", "physical_health_record", "身体健康记录"],
        ["健康表", "mental_health_record", "心理健康记录"],
        ["健康表", "social_health_record", "社交健康记录"],
        ["智能表", "risk_alert", "风险告警"],
        ["智能表", "ai_coach_log", "AI 对话日志"],
        ["智能表", "study_plan", "学习计划"],
        ["智能表", "resource_recommendation", "资源推荐"],
        ["智能表", "growth_report", "成长档案"],
    ]
    db_table = Table(db_data, colWidths=[2.5 * cm, 6.5 * cm, 8 * cm])
    db_table.setStyle(_make_table_style(font_size=9))
    story.append(db_table)

    # ============================================================
    # 五、项目进度安排
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("05", "项目进度安排"))
    story.append(Spacer(1, 8))
    story.append(Paragraph("项目总周期 8 周，按敏捷开发模式分阶段交付：", body_style))
    story.append(Spacer(1, 8))

    schedule_data = [
        ["周次", "阶段", "任务内容", "交付物"],
        ["第 1 周", "需求分析与设计", "需求分析、技术选型、数据库设计与 ER 图", "需求文档、ER 图、数据库脚本"],
        ["第 2 周", "数据层开发", "DatabaseManager、11 个 DAO 类、12 个数据模型", "数据层代码、单元测试"],
        ["第 3 周", "业务层核心开发", "数字孪生健康评估、成绩预测、知识图谱模块", "核心业务模块、算法验证"],
        ["第 4 周", "业务层进阶开发", "风险预警、AI 教练、学习计划、资源推荐", "完整业务层代码"],
        ["第 5 周", "桌面 GUI 开发", "PyQt5 主窗口、12 个功能页面、双主题 QSS", "桌面端可运行程序"],
        ["第 6 周", "Web 后端开发", "FastAPI 19 个路由、Pydantic Schema、依赖注入", "Web API 接口文档"],
        ["第 7 周", "Web 前端开发", "React 15 个页面、ECharts 图表、路由守卫、状态管理", "前端页面可访问"],
        ["第 8 周", "集成与交付", "集成测试、性能优化、PyInstaller 打包、文档编写、答辩", "EXE 安装包、完整文档"],
    ]
    schedule_table = Table(schedule_data, colWidths=[1.6 * cm, 3 * cm, 6.4 * cm, 6 * cm])
    schedule_table.setStyle(_make_table_style(font_size=8.5))
    story.append(schedule_table)

    # ============================================================
    # 六、关键技术难点与解决方案
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("06", "关键技术难点与解决方案"))
    story.append(Spacer(1, 12))

    difficulty_data = [
        ["编号", "技术难点", "问题描述", "解决方案"],
        ["6.1", "多线程数据库连接安全", "并发请求下共享单连接可能导致 500 错误", "使用 threading.local() 实现线程隔离连接"],
        ["6.2", "成绩预测数据不足", "新课程数据少时模型训练效果差", "支持线性回归与梯度提升策略切换"],
        ["6.3", "API Key 安全存储", "配置文件明文存储 API Key 存在风险", "Base64 编码存储，运行时解码"],
        ["6.4", "双界面共享业务逻辑", "桌面 GUI 与 Web 界面逻辑重复开发", "业务层独立，统一调用 Business 类接口"],
        ["6.5", "知识图谱可视化布局", "知识点多且关系复杂，布局易混乱", "NetworkX spring_layout + 掌握度着色"],
    ]
    difficulty_table = Table(difficulty_data, colWidths=[1.2 * cm, 3.3 * cm, 5.5 * cm, 7 * cm])
    difficulty_table.setStyle(_make_table_style(font_size=8.5))
    story.append(difficulty_table)

    # ============================================================
    # 七、风险评估与应对
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("07", "风险评估与应对"))
    story.append(Spacer(1, 12))

    risk_data = [
        ["编号", "风险类型", "风险描述", "应对措施"],
        ["7.1", "技术风险", "机器学习预测精度不达标", "增加梯度提升集成算法，支持交叉验证调参"],
        ["7.2", "进度风险", "双界面开发工作量大", "优先完成桌面 GUI，Web 界面并行开发"],
        ["7.3", "依赖风险", "大语言模型 API 可用性", "支持多家提供商切换，兼容自定义端点"],
        ["7.4", "数据风险", "数据库迁移失败", "分版本 SQL 脚本，幂等执行，可回滚"],
    ]
    risk_table = Table(risk_data, colWidths=[1.2 * cm, 2.5 * cm, 5 * cm, 8.3 * cm])
    risk_table.setStyle(_make_table_style(font_size=9))
    story.append(risk_table)

    # ============================================================
    # 八、测试计划
    # ============================================================
    story.append(Spacer(1, 20))
    story.append(ChapterHeader("08", "测试计划"))
    story.append(Spacer(1, 12))

    test_data = [
        ["测试类型", "测试内容", "通过标准"],
        ["单元测试", "数据库连接、数字孪生、成绩预测、知识图谱、风险预警、AI 教练", "6 个测试模块全部通过"],
        ["集成测试", "GUI Widget 与业务层联动、Web API 端到端请求", "核心流程无异常"],
        ["性能测试", "健康评估响应时间、批量导入 100 条学习记录", "响应 < 2 秒，无内存泄漏"],
        ["兼容性测试", "Windows 10/11 桌面端、Chrome/Edge 浏览器", "主流环境均可正常运行"],
    ]
    test_table = Table(test_data, colWidths=[2.5 * cm, 8.5 * cm, 6 * cm])
    test_table.setStyle(_make_table_style(font_size=9))
    story.append(test_table)

    # ============================================================
    # 九、交付物清单
    # ============================================================
    story.append(PageBreak())
    story.append(ChapterHeader("09", "交付物清单"))
    story.append(Spacer(1, 12))

    deliverable_data = [
        ["编号", "交付物", "说明"],
        ["9.1", "源代码", "四层架构完整代码（business_layer / data_layer / presentation_layer / web / frontend）"],
        ["9.2", "数据库脚本", "SQL 建表脚本（schema / v2_extend / v3_health_extend）+ 演示数据"],
        ["9.3", "桌面端程序", "PyInstaller 打包的单文件 EXE（含 logo 图标），约 143 MB"],
        ["9.4", "Web 端", "FastAPI 后端源码 + React 前端构建产物"],
        ["9.5", "文档", "README 使用说明 + 项目计划书 + 架构设计文档"],
        ["9.6", "配置文件", "config.example.json 配置模板 + build.spec 打包配置"],
    ]
    deliverable_table = Table(deliverable_data, colWidths=[1.2 * cm, 3 * cm, 12.8 * cm])
    deliverable_table.setStyle(_make_table_style(font_size=9.5))
    story.append(deliverable_table)

    # ============================================================
    # 十、团队分工与协作
    # ============================================================
    story.append(Spacer(1, 20))
    story.append(ChapterHeader("10", "团队分工与协作"))
    story.append(Spacer(1, 12))

    team_data = [
        ["角色", "职责", "主要产出"],
        ["后端开发工程师", "数据层 + 业务层 + Web API", "DatabaseManager、DAO、Business 类、FastAPI 路由"],
        ["前端开发工程师", "桌面 GUI + Web 前端界面", "PyQt5 Widget、React 页面、ECharts 图表、主题样式"],
        ["算法开发工程师", "成绩预测模型、知识图谱算法、风险预警规则", "机器学习模型、NetworkX 图谱、规则引擎"],
        ["测试运维工程师", "单元测试、打包部署、文档编写", "pytest 测试用例、PyInstaller 打包、README 文档"],
    ]
    team_table = Table(team_data, colWidths=[3.5 * cm, 5 * cm, 8.5 * cm])
    team_table.setStyle(_make_table_style(font_size=9.5))
    story.append(team_table)

    # ---------- 文末信息 ----------
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="40%", thickness=1, color=COLOR_BORDER, hAlign="CENTER"))
    story.append(Spacer(1, 10))
    story.append(Paragraph("—— 文档结束 ——", footer_style))
    story.append(Paragraph("版本 v1.0 &nbsp;|&nbsp; 2026-08-11", footer_style))

    # 构建文档
    doc.build(story, onFirstPage=lambda c, d: None, onLaterPages=_draw_header_footer)
    return output_path


if __name__ == "__main__":
    output = str(Path(__file__).resolve().parent.parent / "docs" / "项目计划书.pdf")
    result = build_pdf(output)
    print(f"PDF 生成成功：{result}")
