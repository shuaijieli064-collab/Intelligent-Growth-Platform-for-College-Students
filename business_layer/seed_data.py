"""预置大学通用课程与知识点数据."""
import random
from datetime import date, timedelta

from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.health_dao import HealthDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from data_layer.dao.student_dao import StudentDAO
from data_layer.dao.study_record_dao import StudyRecordDAO
from data_layer.models import (
    Course, KnowledgePoint, MentalHealthRecord,
    PhysicalHealthRecord, SocialHealthRecord, Student,
)


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


# 课程三层知识树：课程代码 -> [(章名, [(知识点名, 难度1-5, 权重), ...]), ...]
# 课程根节点由 seed 自动创建（node_type='course'），章 node_type='chapter'，叶子 node_type='kp'。
PRESET_COURSE_TREE: dict[str, list[tuple[str, list[tuple[str, int, float]]]]] = {
    "CS101": [
        ("第1章 程序设计概述", [
            ("变量与数据类型", 1, 1.0), ("运算符与表达式", 1, 1.0),
            ("输入与输出", 1, 0.9), ("编码规范与注释", 1, 0.8),
        ]),
        ("第2章 控制结构", [
            ("条件语句与分支", 1, 1.0), ("循环结构", 1, 1.0),
            ("循环控制语句", 2, 0.9), ("分支循环综合案例", 2, 0.9),
        ]),
        ("第3章 函数与模块", [
            ("函数定义与调用", 2, 1.0), ("参数传递与返回值", 2, 1.0),
            ("作用域与模块", 2, 0.9), ("递归初步", 3, 0.8),
        ]),
        ("第4章 数据与调试", [
            ("列表与字典", 2, 1.0), ("字符串处理", 2, 0.9),
            ("文件读写", 3, 1.0), ("程序调试基础", 2, 1.0),
        ]),
    ],
    "CS102": [
        ("第1章 线性结构", [
            ("线性表与链表", 2, 1.0), ("栈与队列", 2, 1.0),
            ("双端队列与应用", 2, 0.9), ("串与模式匹配", 3, 0.8),
        ]),
        ("第2章 树与堆", [
            ("二叉树与遍历", 3, 1.0), ("二叉搜索树", 3, 1.0),
            ("堆与优先队列", 3, 0.9), ("霍夫曼编码与树的应用", 3, 0.8),
        ]),
        ("第3章 图结构", [
            ("图的存储与遍历", 3, 1.0), ("最短路径算法", 4, 1.0),
            ("最小生成树", 3, 0.9), ("拓扑排序与关键路径", 4, 0.8),
        ]),
        ("第4章 算法设计与分析", [
            ("排序算法", 2, 1.0), ("查找算法", 2, 1.0),
            ("动态规划入门", 4, 1.0), ("贪心算法", 3, 1.0),
        ]),
    ],
    "CS201": [
        ("第1章 面向对象基础", [
            ("类与对象", 1, 1.0), ("封装与访问控制", 2, 1.0),
            ("构造函数与析构", 2, 0.9), ("静态成员与友元", 2, 0.9),
        ]),
        ("第2章 继承与多态", [
            ("继承与多态", 2, 1.0), ("虚函数与动态绑定", 3, 1.0),
            ("抽象类与接口", 3, 1.0), ("多态应用案例", 3, 0.9),
        ]),
        ("第3章 异常与泛型", [
            ("异常处理", 2, 1.0), ("泛型与模板编程", 3, 0.9),
            ("容器与迭代器", 3, 0.9), ("输入输出流", 2, 0.8),
        ]),
        ("第4章 设计与实践", [
            ("设计模式入门", 3, 1.0), ("单例与工厂模式", 3, 0.9),
            ("UML类图建模", 2, 0.8), ("综合项目实践", 4, 1.0),
        ]),
    ],
    "CS202": [
        ("第1章 操作系统概述", [
            ("操作系统概述", 1, 1.0), ("操作系统发展史", 1, 0.8),
            ("系统调用与接口", 2, 0.9), ("中断与运行模式", 2, 0.9),
        ]),
        ("第2章 进程管理", [
            ("进程与线程", 2, 1.0), ("进程调度算法", 3, 1.0),
            ("进程同步与通信", 3, 1.0), ("死锁与同步", 3, 1.0),
        ]),
        ("第3章 存储管理", [
            ("内存管理", 2, 1.0), ("虚拟内存", 3, 1.0),
            ("页面置换算法", 3, 0.9), ("分段与段页式", 3, 0.8),
        ]),
        ("第4章 文件与设备管理", [
            ("文件系统", 2, 1.0), ("目录结构与实现", 3, 0.9),
            ("设备管理", 2, 0.9), ("I/O控制与缓冲", 3, 0.8),
        ]),
    ],
    "CS203": [
        ("第1章 网络基础", [
            ("网络体系结构", 1, 1.0), ("网络性能指标", 1, 0.8),
            ("数据编码与传输", 2, 0.9), ("通信方式与复用", 2, 0.9),
        ]),
        ("第2章 数据链路层", [
            ("物理层与数据链路层", 2, 1.0), ("差错检测与控制", 2, 0.9),
            ("介质访问控制", 3, 0.9), ("以太网与交换机", 2, 0.9),
        ]),
        ("第3章 网络层与传输层", [
            ("网络层与IP协议", 3, 1.0), ("路由算法", 3, 1.0),
            ("传输层与TCP/UDP", 3, 1.0), ("拥塞控制与流量控制", 4, 0.9),
        ]),
        ("第4章 应用与安全", [
            ("应用层协议", 2, 1.0), ("DNS与HTTP协议", 2, 1.0),
            ("网络安全基础", 3, 1.0), ("加密与防火墙", 3, 0.9),
        ]),
    ],
    "CS301": [
        ("第1章 数据库系统概述", [
            ("数据库系统概述", 1, 1.0), ("数据模型", 1, 0.9),
            ("三级模式与两级映像", 2, 0.9), ("DBMS体系结构", 2, 0.8),
        ]),
        ("第2章 关系模型与SQL", [
            ("关系模型与SQL", 2, 1.0), ("关系代数", 3, 0.9),
            ("SQL查询进阶", 3, 1.0), ("视图与索引", 2, 0.9),
        ]),
        ("第3章 数据库设计", [
            ("数据库设计", 3, 1.0), ("E-R模型与转换", 2, 1.0),
            ("规范化理论", 3, 1.0), ("索引与查询优化", 4, 1.0),
        ]),
        ("第4章 事务与安全", [
            ("事务与并发控制", 4, 1.0), ("故障恢复技术", 3, 0.9),
            ("数据库安全", 2, 0.9), ("分布式数据库", 4, 0.8),
        ]),
    ],
    "CS302": [
        ("第1章 人工智能概述", [
            ("人工智能概述", 1, 1.0), ("AI发展历程", 1, 0.8),
            ("智能搜索算法", 3, 1.0), ("知识表示方法", 2, 0.9),
        ]),
        ("第2章 机器学习", [
            ("机器学习基础", 2, 1.0), ("特征工程", 3, 0.9),
            ("监督学习", 3, 1.0), ("无监督学习", 3, 1.0),
        ]),
        ("第3章 深度学习", [
            ("神经网络入门", 3, 1.0), ("反向传播算法", 4, 1.0),
            ("卷积神经网络", 4, 1.0), ("循环神经网络", 4, 0.9),
        ]),
        ("第4章 前沿与伦理", [
            ("自然语言处理", 3, 1.0), ("大语言模型", 4, 1.0),
            ("强化学习", 4, 0.9), ("AI伦理与安全", 2, 0.8),
        ]),
    ],
    "SE201": [
        ("第1章 软件工程基础", [
            ("软件工程概述", 1, 1.0), ("软件生命周期", 1, 0.9),
            ("过程模型", 2, 1.0), ("软件质量与度量", 2, 0.9),
        ]),
        ("第2章 需求与设计", [
            ("需求分析", 2, 1.0), ("用例建模", 2, 0.9),
            ("软件设计", 2, 1.0), ("架构设计模式", 3, 0.9),
        ]),
        ("第3章 测试与维护", [
            ("软件测试", 2, 1.0), ("测试用例设计", 3, 1.0),
            ("缺陷跟踪与管理", 2, 0.8), ("软件维护与演化", 2, 0.8),
        ]),
        ("第4章 项目与过程", [
            ("项目管理", 2, 1.0), ("敏捷开发", 2, 1.0),
            ("CI/CD与DevOps", 3, 0.9), ("团队协作与沟通", 1, 0.8),
        ]),
    ],
    "MATH101": [
        ("第1章 极限与连续", [
            ("函数与极限", 1, 1.0), ("极限运算法则", 2, 1.0),
            ("无穷小与无穷大", 2, 0.9), ("函数的连续性", 2, 1.0),
        ]),
        ("第2章 一元函数微分学", [
            ("导数与微分", 2, 1.0), ("求导法则与技巧", 2, 1.0),
            ("隐函数与参数方程求导", 3, 0.9), ("微分中值定理", 3, 1.0),
        ]),
        ("第3章 一元函数积分学", [
            ("不定积分", 2, 1.0), ("换元积分与分部积分", 3, 1.0),
            ("定积分", 3, 1.0), ("定积分的应用", 3, 1.0),
        ]),
        ("第4章 常微分方程", [
            ("微分方程基本概念", 2, 0.9), ("可分离变量方程", 2, 0.9),
            ("一阶线性微分方程", 3, 0.9), ("微分方程简单应用", 3, 0.8),
        ]),
    ],
    "MATH102": [
        ("第1章 多元函数微分学", [
            ("向量代数与空间解析几何", 2, 1.0), ("多元函数微分学", 3, 1.0),
            ("偏导数与全微分", 3, 1.0), ("多元函数极值", 3, 0.9),
        ]),
        ("第2章 多元函数积分学", [
            ("重积分", 3, 1.0), ("二重积分的计算", 3, 1.0),
            ("三重积分与应用", 4, 0.9), ("曲线积分与曲面积分", 4, 1.0),
        ]),
        ("第3章 无穷级数", [
            ("无穷级数", 3, 1.0), ("数项级数审敛法", 3, 0.9),
            ("幂级数与函数展开", 3, 0.9), ("傅里叶级数", 4, 0.8),
        ]),
        ("第4章 微分方程进阶", [
            ("微分方程", 2, 1.0), ("高阶微分方程", 3, 0.9),
            ("微分方程级数解", 4, 0.8), ("微分方程应用建模", 3, 0.8),
        ]),
    ],
    "MATH201": [
        ("第1章 行列式与矩阵", [
            ("行列式", 1, 1.0), ("矩阵及其运算", 2, 1.0),
            ("矩阵的初等变换", 2, 1.0), ("分块矩阵与特殊矩阵", 2, 0.9),
        ]),
        ("第2章 线性方程组", [
            ("向量组的线性相关性", 3, 1.0), ("线性方程组解的结构", 3, 1.0),
            ("齐次与非齐次方程组", 3, 0.9), ("线性方程组应用", 3, 0.8),
        ]),
        ("第3章 特征值与二次型", [
            ("相似矩阵及二次型", 3, 1.0), ("特征值与特征向量", 3, 1.0),
            ("矩阵对角化", 4, 0.9), ("二次型标准化", 3, 0.9),
        ]),
        ("第4章 线性空间", [
            ("线性空间与线性变换", 4, 1.0), ("内积与正交化", 3, 0.9),
            ("子空间与基", 3, 0.9), ("线性变换的矩阵表示", 4, 0.8),
        ]),
    ],
    "MATH202": [
        ("第1章 概率论基本概念", [
            ("概率论的基本概念", 1, 1.0), ("古典概型与几何概型", 1, 0.9),
            ("条件概率与独立性", 2, 1.0), ("全概率与贝叶斯公式", 3, 0.9),
        ]),
        ("第2章 随机变量", [
            ("随机变量及其分布", 2, 1.0), ("常见离散型分布", 3, 1.0),
            ("常见连续型分布", 3, 1.0), ("随机变量函数的分布", 3, 0.9),
        ]),
        ("第3章 多维随机变量与数字特征", [
            ("多维随机变量", 3, 1.0), ("边缘分布与独立性", 3, 0.9),
            ("随机变量的数字特征", 3, 1.0), ("协方差与相关系数", 3, 0.9),
        ]),
        ("第4章 极限定理与统计推断", [
            ("大数定律与中心极限定理", 4, 1.0), ("抽样分布与统计量", 3, 0.9),
            ("参数估计", 3, 1.0), ("假设检验", 3, 1.0),
        ]),
    ],
    "MATH301": [
        ("第1章 数理逻辑", [
            ("命题逻辑", 1, 1.0), ("谓词逻辑", 2, 1.0),
            ("逻辑等价与范式", 3, 0.9), ("推理理论与证明", 3, 0.9),
        ]),
        ("第2章 集合与关系", [
            ("集合与关系", 1, 1.0), ("函数", 2, 1.0),
            ("等价关系与偏序", 3, 0.9), ("关系的闭包与运算", 3, 0.8),
        ]),
        ("第3章 图论", [
            ("图论基础", 2, 1.0), ("图的连通性", 3, 1.0),
            ("树与生成树", 3, 1.0), ("欧拉图与哈密顿图", 3, 0.9),
        ]),
        ("第4章 代数系统", [
            ("代数系统", 2, 1.0), ("群论初步", 3, 0.9),
            ("环与域", 4, 0.8), ("格与布尔代数", 3, 0.9),
        ]),
    ],
    "ENG101": [
        ("第1章 语言基础", [
            ("词汇与语法基础", 1, 1.0), ("时态与语态", 2, 1.0),
            ("句子成分与结构", 2, 0.9), ("构词法与词汇扩展", 1, 0.9),
        ]),
        ("第2章 听说训练", [
            ("听力训练", 2, 1.0), ("口语交流", 2, 1.0),
            ("语音语调基础", 1, 0.9), ("日常情景对话", 2, 0.9),
        ]),
        ("第3章 阅读与翻译", [
            ("阅读理解技巧", 2, 1.0), ("略读与查读策略", 2, 0.9),
            ("翻译基础", 3, 1.0), ("英汉语言对比", 2, 0.8),
        ]),
        ("第4章 写作入门", [
            ("写作入门", 2, 1.0), ("主题段落写作", 2, 1.0),
            ("应用文写作", 2, 0.9), ("常用句式积累", 1, 0.8),
        ]),
    ],
    "ENG102": [
        ("第1章 高级词汇", [
            ("高级词汇", 2, 1.0), ("词根与词缀", 2, 0.9),
            ("近义词辨析", 3, 0.9), ("学术高频词汇", 2, 0.9),
        ]),
        ("第2章 学术读写", [
            ("学术阅读", 3, 1.0), ("学术写作", 3, 1.0),
            ("文献摘要写作", 3, 0.9), ("引用与参考文献", 2, 0.8),
        ]),
        ("第3章 口译与跨文化", [
            ("口译基础", 4, 1.0), ("跨文化交际", 2, 1.0),
            ("视听说训练", 2, 0.9), ("小组展示与演讲", 2, 0.9),
        ]),
        ("第4章 备考与应试", [
            ("四级备考", 3, 1.0), ("阅读理解策略", 2, 0.9),
            ("写作模板与技巧", 2, 0.9), ("历年真题演练", 3, 0.9),
        ]),
    ],
    "PHY101": [
        ("第1章 力学基础", [
            ("质点运动学", 2, 1.0), ("牛顿运动定律", 2, 1.0),
            ("曲线运动与抛体", 3, 0.9), ("圆周运动", 2, 0.9),
        ]),
        ("第2章 动量与能量", [
            ("功和能", 2, 1.0), ("动量与角动量", 3, 1.0),
            ("机械能守恒定律", 3, 1.0), ("碰撞与守恒定律", 3, 0.9),
        ]),
        ("第3章 刚体与振动", [
            ("刚体力学", 4, 1.0), ("刚体定轴转动", 3, 0.9),
            ("简谐振动", 3, 1.0), ("机械振动与波", 3, 1.0),
        ]),
        ("第4章 流体与相对论", [
            ("流体静力学", 3, 0.9), ("流体运动与伯努利", 4, 0.8),
            ("声波与多普勒效应", 3, 0.8), ("狭义相对论基础", 4, 0.8),
        ]),
    ],
    "PHY102": [
        ("第1章 热学", [
            ("热学基础", 2, 1.0), ("气体动理论", 3, 1.0),
            ("热力学第一定律", 3, 1.0), ("循环过程与熵", 4, 0.9),
        ]),
        ("第2章 电磁场", [
            ("静电场", 2, 1.0), ("电介质与电容", 3, 0.9),
            ("稳恒磁场", 3, 1.0), ("磁介质与磁场能量", 3, 0.8),
        ]),
        ("第3章 电磁感应与电路", [
            ("电磁感应", 3, 1.0), ("麦克斯韦方程组", 4, 0.9),
            ("交流电路", 3, 0.9), ("RC与RL暂态过程", 4, 0.8),
        ]),
        ("第4章 光学与近代物理", [
            ("波动光学", 3, 1.0), ("光的干涉与衍射", 3, 0.9),
            ("光的偏振", 3, 0.8), ("近代物理基础", 3, 1.0),
        ]),
    ],
    "POL101": [
        ("第1章 人生观与理想信念", [
            ("人生观与价值观", 1, 1.0), ("人生目的与人生态度", 1, 0.9),
            ("理想信念", 2, 1.0), ("时代精神与中国精神", 2, 0.9),
        ]),
        ("第2章 道德修养", [
            ("道德修养", 1, 1.0), ("社会公德", 2, 0.9),
            ("职业道德", 2, 1.0), ("家庭美德与个人品德", 2, 0.9),
        ]),
        ("第3章 法治观念", [
            ("法治观念", 2, 1.0), ("宪法基础", 2, 1.0),
            ("中国特色社会主义法律体系", 2, 0.9), ("法治思维与法治方式", 3, 0.9),
        ]),
        ("第4章 权利与义务", [
            ("公民权利与义务", 2, 1.0), ("民事法律制度", 3, 0.9),
            ("行政与诉讼救济", 3, 0.8), ("依法行使权利", 2, 0.9),
        ]),
    ],
}

# 课程名 -> 课程代码（GUI/脚本按名称对齐同一份树）
COURSE_NAME_TO_CODE: dict[str, str] = {
    c["course_name"]: c["course_code"] for c in PRESET_COURSES
}



def _get_kp_by_name_and_course(db: DatabaseManager, course_id: int, kp_name: str):
    rows = db.execute_query(
        "SELECT * FROM knowledge_point WHERE course_id = %s AND kp_name = %s "
        "AND created_by IS NULL",
        (course_id, kp_name),
    )
    return rows[0] if rows else None


def _has_student_course(db: DatabaseManager, student_id: int, course_id: int) -> bool:
    rows = db.execute_query(
        "SELECT id FROM student_course WHERE student_id = %s AND course_id = %s",
        (student_id, course_id),
    )
    return len(rows) > 0


def _ensure_node_type_column(db: DatabaseManager) -> None:
    """幂等：为 knowledge_point 增加 node_type 列（v6 迁移的 Python 侧兜底）."""
    try:
        if getattr(db, "_db_type", "mysql") == "postgres":
            rows = db.execute_query(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name = 'knowledge_point' AND column_name = 'node_type' LIMIT 1"
            )
            if not rows:
                db.execute_update(
                    "ALTER TABLE knowledge_point ADD COLUMN node_type "
                    "VARCHAR(10) NOT NULL DEFAULT 'kp'"
                )
            return
        rows = db.execute_query(
            "SELECT COUNT(*) AS cnt FROM information_schema.COLUMNS "
            "WHERE TABLE_SCHEMA = DATABASE() "
            "AND TABLE_NAME = 'knowledge_point' AND COLUMN_NAME = 'node_type'"
        )
        if rows and int(rows[0]["cnt"]) == 0:
            db.execute_update(
                "ALTER TABLE knowledge_point ADD COLUMN node_type "
                "ENUM('course','chapter','kp') NOT NULL DEFAULT 'kp' "
                "COMMENT '节点类型: course/chapter/kp'"
            )
    except Exception:
        # 无 ALTER 权限或列已存在等场景不阻断启动
        pass


def _get_structure_node(db: DatabaseManager, course_id: int,
                        node_type: str, kp_name: str):
    rows = db.execute_query(
        "SELECT * FROM knowledge_point WHERE course_id = %s "
        "AND node_type = %s AND kp_name = %s",
        (course_id, node_type, kp_name),
    )
    return rows[0] if rows else None


def ensure_course_hierarchy(db: DatabaseManager, course_id: int,
                            course_code: str, course_name: str) -> None:
    """确保 课程根→章→知识点 三层结构存在（幂等；已存在 kp_id 不变，掌握度不丢）."""
    kp_dao = KnowledgeDAO(db)

    root = _get_structure_node(db, course_id, "course", course_name)
    if root is None:
        root_id = kp_dao.create_knowledge_point(KnowledgePoint(
            kp_name=course_name, course_id=course_id, parent_kp_id=None,
            difficulty=1, weight=1.0, node_type="course",
        ))
    else:
        root_id = root["kp_id"]

    chapters = PRESET_COURSE_TREE.get(course_code, [])
    for chapter_name, leaves in chapters:
        chapter = _get_structure_node(db, course_id, "chapter", chapter_name)
        if chapter is None:
            chapter_id = kp_dao.create_knowledge_point(KnowledgePoint(
                kp_name=chapter_name, course_id=course_id, parent_kp_id=root_id,
                difficulty=2, weight=1.0, node_type="chapter",
            ))
        else:
            chapter_id = chapter["kp_id"]
            if chapter["parent_kp_id"] != root_id:
                kp_dao.update_parent_kp(chapter_id, root_id)

        for kp_name, difficulty, weight in leaves:
            existing = _get_kp_by_name_and_course(db, course_id, kp_name)
            if existing is not None:
                # 预置旧节点：重新挂到对应章下（kp_id 不变 -> 掌握度保留）
                db.execute_update(
                    "UPDATE knowledge_point SET parent_kp_id = %s, node_type = 'kp', "
                    "difficulty = %s, weight = %s WHERE kp_id = %s",
                    (chapter_id, difficulty, weight, existing["kp_id"]),
                )
            else:
                kp_dao.create_knowledge_point(KnowledgePoint(
                    kp_name=kp_name, course_id=course_id, parent_kp_id=chapter_id,
                    difficulty=difficulty, weight=weight, node_type="kp",
                ))

    # 不在新树中的预置遗留节点（链头）挂到课程根，避免游离
    db.execute_update(
        "UPDATE knowledge_point SET parent_kp_id = %s WHERE course_id = %s "
        "AND created_by IS NULL AND parent_kp_id IS NULL AND node_type = 'kp'",
        (root_id, course_id),
    )


def ensure_preset_hierarchy(db: DatabaseManager) -> None:
    """启动时调用：补 node_type 列 + 为库内已存在的预置课程重建知识层级."""
    _ensure_node_type_column(db)
    course_dao = CourseDAO(db)
    for course_data in PRESET_COURSES:
        course = course_dao.get_by_name(course_data["course_name"])
        if course is None:
            course = course_dao.get_by_code(course_data["course_code"])
            if course is None or course.course_name != course_data["course_name"]:
                continue
        ensure_course_hierarchy(
            db, course.course_id,
            course_data["course_code"], course_data["course_name"],
        )


def seed_default_courses(student_id: int, db: DatabaseManager) -> None:
    course_dao = CourseDAO(db)
    student_course_dao = StudentCourseDAO(db)

    course_id_map = {}

    for course_data in PRESET_COURSES:
        course_code = course_data["course_code"]
        course_name = course_data["course_name"]

        # 查重策略：课程名是业务唯一标识，优先按名称复用已有课程，
        # 避免历史课程代码错位导致创建出同名重复课程。
        existing_by_name = course_dao.get_by_name(course_name)
        existing_by_code = course_dao.get_by_code(course_code)

        if existing_by_name is not None:
            course_id = existing_by_name.course_id
        elif existing_by_code is not None and existing_by_code.course_name == course_name:
            course_id = existing_by_code.course_id
        else:
            prerequisite_id = None
            if course_data["prerequisite_code"]:
                prereq = course_dao.get_by_name(
                    next(
                        (
                            p["course_name"]
                            for p in PRESET_COURSES
                            if p["course_code"] == course_data["prerequisite_code"]
                        ),
                        course_data["prerequisite_code"],
                    )
                )
                if prereq is None:
                    prereq = course_dao.get_by_code(course_data["prerequisite_code"])
                if prereq:
                    prerequisite_id = prereq.course_id

            # course_code 有唯一约束：若代码已被其他课程占用，生成唯一代码
            final_code = course_code
            suffix = 2
            while course_dao.get_by_code(final_code) is not None:
                final_code = f"{course_code}_{suffix}"
                suffix += 1

            course = Course(
                course_code=final_code,
                course_name=course_data["course_name"],
                credit=course_data["credit"],
                semester=course_data["semester"],
                is_compulsory=course_data["is_compulsory"],
                prerequisite_course_id=prerequisite_id,
            )
            course_id = course_dao.create(course)

        course_id_map[course_code] = course_id
        if not _has_student_course(db, student_id, course_id):
            student_course_dao.enroll(student_id, course_id)

    _ensure_node_type_column(db)
    for course_data in PRESET_COURSES:
        course_id = course_id_map.get(course_data["course_code"])
        if course_id is None:
            continue
        ensure_course_hierarchy(
            db, course_id,
            course_data["course_code"], course_data["course_name"],
        )


# ============================================================
# 三期：新用户演示数据种子（注册时调用，幂等）
# ============================================================

def _seed_student_profile(db: DatabaseManager, student_id: int,
                          rng: random.Random) -> None:
    """补全个人信息默认值（年级按入学年推算，专业默认计算机）."""
    dao = StudentDAO(db)
    student = dao.get_by_id(student_id)
    if student is None:
        return
    changed = False
    if not student.major:
        student.major = "计算机科学与技术"
        changed = True
    if not student.grade_level:
        year_diff = date.today().year - student.enrollment_year
        levels = ["大一", "大二", "大三", "大四"]
        student.grade_level = levels[min(max(year_diff, 0), 3)]
        changed = True
    if changed:
        dao.update(student)


def _seed_course_scores(db: DatabaseManager, student_id: int,
                        rng: random.Random) -> None:
    """为已选课程填入 82-92 的健康成绩（仅填空，不覆盖已有成绩）."""
    rows = db.execute_query(
        "SELECT sc.course_id, sc.usual_score, sc.midterm_score, sc.final_score "
        "FROM student_course sc WHERE sc.student_id = %s", (student_id,)
    )
    for r in rows:
        if r.get("final_score") is not None:
            continue
        base = rng.uniform(82, 92)
        db.execute_update(
            "UPDATE student_course SET usual_score=%s, midterm_score=%s, "
            "final_score=%s WHERE student_id=%s AND course_id=%s",
            (round(base + rng.uniform(-3, 3), 1),
             round(base + rng.uniform(-4, 4), 1),
             round(base, 1), student_id, r["course_id"]),
        )


def _seed_study_records(db: DatabaseManager, student_id: int,
                        rng: random.Random) -> None:
    """近 14 天学习记录：日均 2-5h、专注 60-85、任务 2-4（避开全部告警阈值）."""
    existing = db.execute_query(
        "SELECT COUNT(*) AS cnt FROM study_record WHERE student_id = %s",
        (student_id,),
    )
    if existing and int(existing[0]["cnt"]) > 0:
        return
    dao = StudyRecordDAO(db)
    course_ids = [r["course_id"] for r in db.execute_query(
        "SELECT course_id FROM student_course WHERE student_id = %s",
        (student_id,),
    )]
    today = date.today()
    for i in range(14, 0, -1):
        d = today - timedelta(days=i)
        hours = round(rng.uniform(2.2, 4.8), 1)
        dao.add_record(
            student_id=student_id, study_date=d, study_hours=hours,
            course_id=rng.choice(course_ids) if course_ids else None,
            task_completed=rng.randint(2, 4),
            focus_score=rng.randint(60, 85),
        )


def _seed_health_records(db: DatabaseManager, student_id: int,
                         rng: random.Random) -> None:
    """近 14 天身体/心理/社交记录（健康值落在 LOW 风险区间）."""
    health_dao = HealthDAO(db)
    existing = health_dao.get_physical_records(student_id, days=14)
    if existing:
        return
    today = date.today()
    exercise_types = ["跑步", "篮球", "健身", "游泳", "骑行"]
    activity_types = ["社团活动", "小组讨论", "朋友聚餐", "志愿服务"]
    for i in range(14, 0, -1):
        d = today - timedelta(days=i)
        health_dao.save_physical_record(PhysicalHealthRecord(
            student_id=student_id, record_date=d,
            exercise_type=rng.choice(exercise_types),
            exercise_duration=rng.randint(30, 70),
            sleep_hours=round(rng.uniform(6.5, 8.5), 1),
            steps=rng.randint(5000, 11000),
        ))
        health_dao.save_mental_record(MentalHealthRecord(
            student_id=student_id, record_date=d,
            mood_score=rng.randint(7, 9),
            stress_level=rng.randint(1, 2),
            anxiety_level=rng.randint(1, 2),
        ))
        health_dao.save_social_record(SocialHealthRecord(
            student_id=student_id, record_date=d,
            activity_type=rng.choice(activity_types),
            duration_minutes=rng.randint(60, 150),
            interaction_count=rng.randint(5, 12),
        ))


def _seed_knowledge_mastery(db: DatabaseManager, student_id: int,
                            rng: random.Random) -> None:
    """预置叶子知识点掌握度：整体 ~85%，留 2-3 个 <50% 薄弱点."""
    existing = db.execute_query(
        "SELECT COUNT(*) AS cnt FROM knowledge_mastery WHERE student_id = %s",
        (student_id,),
    )
    if existing and int(existing[0]["cnt"]) > 0:
        return
    rows = db.execute_query(
        "SELECT kp.kp_id FROM knowledge_point kp "
        "JOIN student_course sc ON kp.course_id = sc.course_id "
        "WHERE sc.student_id = %s AND kp.node_type = 'kp' AND kp.created_by IS NULL",
        (student_id,),
    )
    kp_ids = [r["kp_id"] for r in rows]
    if not kp_ids:
        return
    weak = set(rng.sample(kp_ids, min(3, len(kp_ids))))
    dao = KnowledgeDAO(db)
    for kp_id in kp_ids:
        level = rng.uniform(30, 45) if kp_id in weak else rng.uniform(78, 95)
        dao.update_mastery(student_id, kp_id, round(level, 1))


def _seed_health_snapshot(db: DatabaseManager, student_id: int,
                          rng: random.Random) -> None:
    """回填近 14 天健康评估快照（LOW 风险，支撑可视化趋势图）."""
    health_dao = HealthDAO(db)
    existing = health_dao.get_history(student_id)
    if existing:
        return
    from business_layer.digital_twin import DigitalTwin
    from data_layer.models import HealthAssessment
    result = DigitalTwin(student_id, db).assess_overall()
    today = date.today()
    for i in range(14, 0, -1):
        jitter = rng.uniform(-2, 2)
        overall = min(100, max(0, result.overall + jitter))
        health_dao.save_assessment(HealthAssessment(
            student_id=student_id,
            assessment_date=today - timedelta(days=i),
            academic_score=min(100, max(0, result.academic + jitter)),
            physical_score=min(100, max(0, result.physical + jitter)),
            mental_score=min(100, max(0, result.mental + jitter)),
            social_score=min(100, max(0, result.social + jitter)),
            overall_health=overall,
            risk_level="LOW" if overall >= 80 else "MEDIUM",
        ))


def seed_demo_data(student_id: int, db: DatabaseManager) -> None:
    """新注册用户演示数据（幂等：已有数据的项跳过，不覆盖用户真实数据）."""
    rng = random.Random(student_id)
    try:
        _seed_student_profile(db, student_id, rng)
        _seed_course_scores(db, student_id, rng)
        _seed_study_records(db, student_id, rng)
        _seed_health_records(db, student_id, rng)
        _seed_knowledge_mastery(db, student_id, rng)
        _seed_health_snapshot(db, student_id, rng)
    except Exception:
        # 种子失败不阻断注册主流程
        pass

