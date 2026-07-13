"""预置大学通用课程与知识点数据."""
from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from data_layer.models import Course, KnowledgePoint


PRESET_COURSES = [
    {"course_code": "CS101", "course_name": "程序设计基础", "credit": 4.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
    {"course_code": "CS102", "course_name": "数据结构与算法", "credit": 4.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "CS101"},
    {"course_code": "CS201", "course_name": "面向对象程序设计", "credit": 3.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "CS101"},
    {"course_code": "CS202", "course_name": "操作系统", "credit": 3.5, "semester": "2025-秋", "is_compulsory": True, "prerequisite_code": "CS102"},
    {"course_code": "CS203", "course_name": "计算机网络", "credit": 3.5, "semester": "2025-秋", "is_compulsory": True, "prerequisite_code": "CS202"},
    {"course_code": "CS301", "course_name": "数据库原理", "credit": 3.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "CS102"},
    {"course_code": "CS302", "course_name": "人工智能导论", "credit": 3.0, "semester": "2026-春", "is_compulsory": False, "prerequisite_code": None},
    {"course_code": "SE201", "course_name": "软件工程", "credit": 3.0, "semester": "2026-春", "is_compulsory": True, "prerequisite_code": "CS201"},
    {"course_code": "MATH101", "course_name": "高等数学(上)", "credit": 5.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
    {"course_code": "MATH102", "course_name": "高等数学(下)", "credit": 5.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "MATH101"},
    {"course_code": "MATH201", "course_name": "线性代数", "credit": 3.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
    {"course_code": "MATH202", "course_name": "概率论与数理统计", "credit": 3.5, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "MATH101"},
    {"course_code": "MATH301", "course_name": "离散数学", "credit": 3.0, "semester": "2025-秋", "is_compulsory": True, "prerequisite_code": "MATH201"},
    {"course_code": "ENG101", "course_name": "大学英语(1)", "credit": 3.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
    {"course_code": "ENG102", "course_name": "大学英语(2)", "credit": 3.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "ENG101"},
    {"course_code": "PHY101", "course_name": "大学物理(上)", "credit": 4.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
    {"course_code": "PHY102", "course_name": "大学物理(下)", "credit": 4.0, "semester": "2025-春", "is_compulsory": True, "prerequisite_code": "PHY101"},
    {"course_code": "POL101", "course_name": "思想道德与法治", "credit": 3.0, "semester": "2024-秋", "is_compulsory": True, "prerequisite_code": None},
]


PRESET_KNOWLEDGE_POINTS = {
    "CS101": [
        "变量与数据类型",
        "运算符与表达式",
        "条件语句与分支",
        "循环结构",
        "函数定义与调用",
        "列表与字典",
        "文件读写",
        "程序调试基础",
    ],
    "CS102": [
        "线性表与链表",
        "栈与队列",
        "二叉树与遍历",
        "图的存储与遍历",
        "排序算法",
        "查找算法",
        "动态规划入门",
        "贪心算法",
    ],
    "CS201": [
        "类与对象",
        "封装与访问控制",
        "继承与多态",
        "抽象类与接口",
        "异常处理",
        "设计模式入门",
    ],
    "CS202": [
        "操作系统概述",
        "进程与线程",
        "内存管理",
        "文件系统",
        "设备管理",
        "死锁与同步",
    ],
    "CS203": [
        "网络体系结构",
        "物理层与数据链路层",
        "网络层与IP协议",
        "传输层与TCP/UDP",
        "应用层协议",
        "网络安全基础",
    ],
    "CS301": [
        "数据库系统概述",
        "关系模型与SQL",
        "数据库设计",
        "事务与并发控制",
        "索引与查询优化",
        "数据库安全",
    ],
    "CS302": [
        "人工智能概述",
        "机器学习基础",
        "神经网络入门",
        "监督学习",
        "无监督学习",
        "自然语言处理",
    ],
    "SE201": [
        "软件工程概述",
        "需求分析",
        "软件设计",
        "软件测试",
        "项目管理",
        "敏捷开发",
    ],
    "MATH101": [
        "函数与极限",
        "导数与微分",
        "微分中值定理",
        "不定积分",
        "定积分",
        "定积分的应用",
    ],
    "MATH102": [
        "向量代数与空间解析几何",
        "多元函数微分学",
        "重积分",
        "曲线积分与曲面积分",
        "无穷级数",
        "微分方程",
    ],
    "MATH201": [
        "行列式",
        "矩阵及其运算",
        "矩阵的初等变换",
        "向量组的线性相关性",
        "相似矩阵及二次型",
        "线性空间与线性变换",
    ],
    "MATH202": [
        "概率论的基本概念",
        "随机变量及其分布",
        "多维随机变量",
        "随机变量的数字特征",
        "大数定律与中心极限定理",
        "参数估计",
        "假设检验",
    ],
    "MATH301": [
        "命题逻辑",
        "谓词逻辑",
        "集合与关系",
        "函数",
        "图论基础",
        "代数系统",
    ],
    "ENG101": [
        "词汇与语法基础",
        "阅读理解技巧",
        "听力训练",
        "写作入门",
        "口语交流",
        "翻译基础",
    ],
    "ENG102": [
        "高级词汇",
        "学术阅读",
        "学术写作",
        "口译基础",
        "跨文化交际",
        "四级备考",
    ],
    "PHY101": [
        "质点运动学",
        "牛顿运动定律",
        "功和能",
        "动量与角动量",
        "刚体力学",
        "机械振动与波",
    ],
    "PHY102": [
        "热学基础",
        "静电场",
        "稳恒磁场",
        "电磁感应",
        "波动光学",
        "近代物理基础",
    ],
    "POL101": [
        "人生观与价值观",
        "道德修养",
        "法治观念",
        "宪法基础",
        "公民权利与义务",
        "职业道德",
    ],
}


def _get_kp_by_name_and_course(db: DatabaseManager, course_id: int, kp_name: str):
    rows = db.execute_query(
        "SELECT * FROM knowledge_point WHERE course_id = %s AND kp_name = %s",
        (course_id, kp_name),
    )
    return rows[0] if rows else None


def _has_student_course(db: DatabaseManager, student_id: int, course_id: int) -> bool:
    rows = db.execute_query(
        "SELECT id FROM student_course WHERE student_id = %s AND course_id = %s",
        (student_id, course_id),
    )
    return len(rows) > 0


def seed_default_courses(student_id: int, db: DatabaseManager) -> None:
    course_dao = CourseDAO(db)
    student_course_dao = StudentCourseDAO(db)
    knowledge_dao = KnowledgeDAO(db)

    course_id_map = {}

    for course_data in PRESET_COURSES:
        course_code = course_data["course_code"]
        existing = course_dao.get_by_code(course_code)

        if existing is None:
            prerequisite_id = None
            if course_data["prerequisite_code"]:
                prereq = course_dao.get_by_code(course_data["prerequisite_code"])
                if prereq:
                    prerequisite_id = prereq.course_id

            course = Course(
                course_code=course_code,
                course_name=course_data["course_name"],
                credit=course_data["credit"],
                semester=course_data["semester"],
                is_compulsory=course_data["is_compulsory"],
                prerequisite_course_id=prerequisite_id,
            )
            course_id = course_dao.create(course)
            course_id_map[course_code] = course_id
        else:
            course_id_map[course_code] = existing.course_id

        course_id = course_id_map[course_code]
        if not _has_student_course(db, student_id, course_id):
            student_course_dao.enroll(student_id, course_id)

    for course_code, kp_names in PRESET_KNOWLEDGE_POINTS.items():
        course_id = course_id_map.get(course_code)
        if course_id is None:
            continue

        prev_kp_id = None
        for kp_name in kp_names:
            existing_kp = _get_kp_by_name_and_course(db, course_id, kp_name)
            if existing_kp:
                kp_id = existing_kp["kp_id"]
            else:
                kp = KnowledgePoint(
                    kp_name=kp_name,
                    course_id=course_id,
                    parent_kp_id=prev_kp_id,
                    difficulty=1,
                    weight=1.0,
                )
                kp_id = knowledge_dao.create_knowledge_point(kp)

            prev_kp_id = kp_id
