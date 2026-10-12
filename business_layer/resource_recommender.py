"""学习资源推荐系统 - 课程专属资源 + 学科域关键词匹配."""
from data_layer.database import DatabaseManager
from data_layer.dao.resource_dao import ResourceDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from data_layer.dao.course_dao import CourseDAO
from business_layer.knowledge_graph import KnowledgeGraph

# ============================================================
# 课程专属资源库（按课程代码精确映射，确保资源与课程对应）
# ============================================================
COURSE_RESOURCES: dict[str, list[tuple]] = {
    "CS101": [  # 程序设计基础
        ("video", "Python 入门教程 (B站 小甲鱼)", "https://www.bilibili.com/video/BV1wD4y1o7AS"),
        ("exercise", "Python 在线练习 (菜鸟教程)", "https://www.runoob.com/python/python-exercise-examples.html"),
        ("article", "Python 官方中文教程", "https://docs.python.org/zh-cn/3/tutorial/index.html"),
        ("course", "中国大学 MOOC Python (北理工)", "https://www.icourse163.org/course/BIT-268001"),
    ],
    "CS102": [  # 数据结构与算法
        ("video", "数据结构 (B站 青岛大学)", "https://www.bilibili.com/video/BV1nJ411V7bd"),
        ("exercise", "LeetCode 算法题库", "https://leetcode.cn/problemset/all/"),
        ("article", "Hello 算法 (图解数据结构)", "https://www.hello-algo.com/"),
        ("course", "数据结构 (浙大 MOOC)", "https://www.icourse163.org/course/ZJU-93001"),
    ],
    "CS201": [  # 面向对象程序设计
        ("video", "面向对象程序设计 (B站)", "https://www.bilibili.com/video/BV1Yb411W7VW"),
        ("article", "Python 面向对象教程 (廖雪峰)", "https://www.liaoxuefeng.com/wiki/1016959663602400/1017495723838528"),
        ("exercise", "Python 面向对象练习题 (牛客网)", "https://www.nowcoder.com/"),
        ("course", "Python 面向对象 (MOOC)", "https://www.icourse163.org/course/BIT-1001871001"),
    ],
    "CS202": [  # 操作系统
        ("video", "操作系统 (B站 王道)", "https://www.bilibili.com/video/BV1YE411D7nH"),
        ("course", "操作系统 (清华 MOOC)", "https://www.xuetangx.com/course/thu08091000237/19324299"),
        ("article", "MIT 6.S081 操作系统课程", "https://pdos.csail.mit.edu/6.S081/2023/"),
    ],
    "CS301": [  # 数据库原理
        ("video", "MySQL 教程 (B站 尚硅谷)", "https://www.bilibili.com/video/BV1iq4y1u7vj"),
        ("exercise", "SQL 在线练习 (SQLZoo)", "https://sqlzoo.net/"),
        ("article", "SQL 教程 (菜鸟教程)", "https://www.runoob.com/sql/sql-tutorial.html"),
        ("course", "数据库系统概论 (人大 MOOC)", "https://www.icourse163.org/course/RUC-488001"),
    ],
    "CS302": [  # 人工智能导论
        ("video", "吴恩达机器学习 (B站)", "https://www.bilibili.com/video/BV1B4411H76f"),
        ("article", "机器学习速查表", "https://github.com/afshinea/stanford-cs-229-machine-learning"),
        ("exercise", "Kaggle 入门竞赛", "https://www.kaggle.com/competitions"),
        ("course", "人工智能导论 (MOOC)", "https://www.icourse163.org/course/HUST-1003382008"),
    ],
    "MATH101": [  # 高等数学(上)
        ("video", "高等数学 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
        ("exercise", "微积分练习 (Khan Academy)", "https://www.khanacademy.org/math/calculus-1"),
        ("course", "高等数学 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001599002"),
        ("article", "高等数学解题方法汇总", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
    ],
    "MATH102": [  # 高等数学(下)
        ("video", "高等数学下 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
        ("exercise", "微积分练习 (Khan Academy)", "https://www.khanacademy.org/math/multivariable-calculus"),
        ("course", "高等数学 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001599002"),
    ],
    "MATH201": [  # 线性代数
        ("video", "线性代数 (B站 宋浩)", "https://www.bilibili.com/video/BV1aW411Q7x1"),
        ("video", "线性代数的本质 (3Blue1Brown)", "https://www.bilibili.com/video/BV1ys411472E"),
        ("article", "MIT 线性代数笔记", "https://github.com/zhanwenchen/Linear-Algebra-Notes"),
        ("course", "线性代数 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001904005"),
    ],
    "ENG101": [  # 大学英语(1)
        ("video", "英语基础语法 (B站)", "https://www.bilibili.com/video/BV1d4411y7ey"),
        ("article", "BBC Learning English", "https://www.bbc.co.uk/learningenglish"),
        ("exercise", "多邻国免费学英语", "https://www.duolingo.com/"),
        ("video", "TED 演讲精选", "https://www.ted.com/talks"),
        ("course", "大学英语 (MOOC)", "https://www.icourse163.org/course/NENU-1002847002"),
    ],
    "CS203": [  # 计算机网络
        ("video", "计算机网络 (B站 湖科大)", "https://www.bilibili.com/video/BV1c4411d7jb"),
        ("article", "MDN Web 开发文档", "https://developer.mozilla.org/zh-CN/"),
        ("course", "计算机网络 (哈工大 MOOC)", "https://www.icourse163.org/course/HIT-154005"),
        ("exercise", "网络协议抓包练习 (Wireshark 教程)", "https://www.wireshark.org/docs/wsug_html_chunked/"),
    ],
    "SE201": [  # 软件工程
        ("video", "软件工程导论 (MOOC)", "https://www.icourse163.org/course/ZJU-1002984036"),
        ("article", "Git 官方中文文档", "https://git-scm.com/book/zh/v2"),
        ("exercise", "GitHub 项目实战", "https://github.com/topics/practice"),
        ("course", "软件工程 (清华 MOOC)", "https://www.xuetangx.com/course/THU07101000601/"),
    ],
    "MATH202": [  # 概率论与数理统计
        ("video", "概率论与数理统计 (B站 宋浩)", "https://www.bilibili.com/video/BV1ot411y7mU"),
        ("article", "概率论笔记 (Khan Academy)", "https://www.khanacademy.org/math/statistics-probability"),
        ("course", "概率论与数理统计 (MOOC)", "https://www.icourse163.org/course/TONGJI-1001579002"),
    ],
    "MATH301": [  # 离散数学
        ("video", "离散数学 (B站)", "https://www.bilibili.com/video/BV1EW411u7th"),
        ("course", "离散数学 (哈工大 MOOC)", "https://www.icourse163.org/course/HIT-1001566001"),
        ("article", "离散数学讲义", "https://www.bilibili.com/video/BV1EW411u7th"),
    ],
    "ENG102": [  # 大学英语(2)
        ("article", "BBC Learning English", "https://www.bbc.co.uk/learningenglish"),
        ("video", "TED 演讲精选", "https://www.ted.com/talks"),
        ("exercise", "多邻国免费学英语", "https://www.duolingo.com/"),
        ("course", "大学英语 (MOOC)", "https://www.icourse163.org/course/NENU-1002847002"),
    ],
    "PHY101": [  # 大学物理(上)
        ("video", "大学物理 (B站)", "https://www.bilibili.com/video/BV1Ls411d7f5"),
        ("article", "力学基础 (Khan Academy)", "https://www.khanacademy.org/science/physics"),
        ("course", "大学物理 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001907003"),
    ],
    "PHY102": [  # 大学物理(下)
        ("video", "电磁学 (B站)", "https://www.bilibili.com/video/BV1Ls411d7f5"),
        ("article", "电磁学基础 (Khan Academy)", "https://www.khanacademy.org/science/physics"),
        ("course", "大学物理 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001907003"),
    ],
    "POL101": [  # 思想道德与法治
        ("video", "思想道德与法治 (MOOC)", "https://www.icourse163.org/course/NENU-1002847003"),
        ("article", "宪法与法治基础", "https://www.gov.cn/"),
        ("course", "思想道德与法治 (学习强国)", "https://www.xuexi.cn/"),
    ],
}

# 课程中文名 → 课程代码 映射（课程名是业务唯一标识，用于兼容历史课程代码错位）
COURSE_NAME_ALIASES: dict[str, str] = {
    "程序设计基础": "CS101", "数据结构与算法": "CS102",
    "面向对象程序设计": "CS201", "数据库原理": "CS301",
    "人工智能导论": "CS302", "高等数学(上)": "MATH101",
    "线性代数": "MATH201", "大学英语(4)": "ENG101",
    "计算机网络": "CS203", "软件工程": "SE201",
    "概率论与数理统计": "MATH202", "离散数学": "MATH301",
    "大学英语(2)": "ENG102", "大学物理(上)": "PHY101",
    "大学物理(下)": "PHY102", "思想道德与法治": "POL101",
    "操作系统": "CS202", "高等数学(下)": "MATH102",
    "大学英语(1)": "ENG101",
}

# ============================================================
# 知识点关键词资源库（按学科域分组，避免跨学科错配）
#   匹配规则：根据课程代码前缀确定学科域，只在该域内匹配关键词
# ============================================================
KP_KEYWORD_RESOURCES: dict[str, dict[str, list[tuple]]] = {
    # 编程类（CS/SE 课程）
    "programming": {
        "变量与数据类型": [
            ("article", "Python 变量与数据类型", "https://docs.python.org/zh-cn/3/tutorial/introduction.html"),
            ("exercise", "变量练习 (Codecademy)", "https://www.codecademy.com/learn/learn-python-3"),
        ],
        "函数定义": [
            ("video", "Python 函数详解 (B站)", "https://www.bilibili.com/video/BV1wD4y1o7AS"),
            ("exercise", "函数练习 (菜鸟教程)", "https://www.runoob.com/python3/python3-functions.html"),
        ],
        "链表": [
            ("video", "链表详解 (B站)", "https://www.bilibili.com/video/BV1nJ411V7bd"),
            ("exercise", "链表刷题 (LeetCode)", "https://leetcode.cn/tag/linked-list/"),
        ],
        "二叉树": [
            ("video", "二叉树遍历 (B站)", "https://www.bilibili.com/video/BV1nJ411V7bd"),
            ("exercise", "二叉树刷题 (LeetCode)", "https://leetcode.cn/tag/binary-tree/"),
        ],
        "排序": [
            ("video", "十大排序算法 (B站)", "https://www.bilibili.com/video/BV1Lv4y1e7HL"),
            ("exercise", "排序刷题 (牛客网)", "https://www.nowcoder.com/"),
        ],
        "SQL": [
            ("exercise", "SQLZoo 在线练习", "https://sqlzoo.net/"),
            ("video", "SQL 教程 (B站)", "https://www.bilibili.com/video/BV1iq4y1u7vj"),
        ],
        "事务": [
            ("article", "数据库事务详解", "https://www.runoob.com/sql/sql-tutorial.html"),
            ("video", "事务与并发控制 (B站)", "https://www.bilibili.com/video/BV1iq4y1u7vj"),
        ],
        "神经网络": [
            ("video", "神经网络入门 (B站 3Blue1Brown)", "https://www.bilibili.com/video/BV1bx411M7Zn"),
            ("article", "PyTorch 官方教程", "https://pytorch.org/tutorials/"),
        ],
        "机器学习": [
            ("video", "吴恩达机器学习 (B站)", "https://www.bilibili.com/video/BV1B4411H76f"),
            ("article", "scikit-learn 官方文档", "https://scikit-learn.org/stable/"),
        ],
        "网络体系": [
            ("article", "MDN Web 文档", "https://developer.mozilla.org/zh-CN/"),
        ],
        "进程": [
            ("video", "进程与线程 (B站 王道)", "https://www.bilibili.com/video/BV1YE411D7nH"),
            ("article", "操作系统概念笔记", "https://github.com/CyC2018/CS-Notes"),
        ],
        "内存": [
            ("video", "内存管理 (B站 王道)", "https://www.bilibili.com/video/BV1YE411D7nH"),
            ("article", "虚拟内存详解", "https://github.com/CyC2018/CS-Notes"),
        ],
    },
    # 数学类（MATH 课程）
    "math": {
        "极限": [
            ("video", "极限与连续 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
            ("exercise", "极限练习 (Khan Academy)", "https://www.khanacademy.org/math/calculus-1"),
        ],
        "导数": [
            ("video", "导数与微分 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
            ("exercise", "导数练习 (Khan Academy)", "https://www.khanacademy.org/math/calculus-1"),
        ],
        "微分": [
            ("video", "导数与微分 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
            ("exercise", "微分练习 (Khan Academy)", "https://www.khanacademy.org/math/calculus-1"),
        ],
        "积分": [
            ("video", "不定积分与定积分 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
            ("exercise", "积分练习 (Khan Academy)", "https://www.khanacademy.org/math/calculus-1"),
        ],
        "级数": [
            ("video", "无穷级数 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
        ],
        "微分方程": [
            ("video", "微分方程 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
        ],
        "矩阵": [
            ("video", "矩阵运算 (B站 宋浩)", "https://www.bilibili.com/video/BV1aW411Q7x1"),
            ("article", "线性代数笔记 (3Blue1Brown)", "https://www.bilibili.com/video/BV1ys411472E"),
        ],
        "行列式": [
            ("video", "行列式 (B站 宋浩)", "https://www.bilibili.com/video/BV1aW411Q7x1"),
            ("exercise", "行列式练习", "https://www.khanacademy.org/math/linear-algebra"),
        ],
        "概率": [
            ("video", "概率论基础 (B站 宋浩)", "https://www.bilibili.com/video/BV1ot411y7mU"),
            ("article", "概率与统计 (Khan Academy)", "https://www.khanacademy.org/math/statistics-probability"),
        ],
        "中心极限": [
            ("video", "大数定律与中心极限定理 (B站 宋浩)", "https://www.bilibili.com/video/BV1ot411y7mU"),
        ],
        "图论": [
            ("video", "图论基础 (B站)", "https://www.bilibili.com/video/BV1nJ411V7bd"),
            ("exercise", "图论刷题 (LeetCode)", "https://leetcode.cn/tag/graph/"),
        ],
        "逻辑": [
            ("video", "命题逻辑与谓词逻辑 (B站)", "https://www.bilibili.com/video/BV1EW411u7th"),
            ("article", "离散数学逻辑讲义", "https://www.bilibili.com/video/BV1EW411u7th"),
        ],
    },
    # 英语类（ENG 课程）
    "english": {
        "词汇": [
            ("article", "高频词汇记忆法", "https://www.bbc.co.uk/learningenglish"),
            ("exercise", "单词练习 (多邻国)", "https://www.duolingo.com/"),
        ],
        "阅读": [
            ("article", "BBC 英语阅读", "https://www.bbc.co.uk/learningenglish"),
            ("video", "TED 演讲", "https://www.ted.com/talks"),
        ],
        "听力": [
            ("video", "BBC 听力训练", "https://www.bbc.co.uk/learningenglish"),
            ("exercise", "VOA 慢速英语", "https://learningenglish.voanews.com/"),
        ],
        "写作": [
            ("article", "学术写作指南 (Purdue OWL)", "https://owl.purdue.edu/"),
            ("exercise", "写作练习 (Quill)", "https://www.quill.org/"),
        ],
    },
    # 物理类（PHY 课程）
    "physics": {
        "力学": [
            ("video", "质点运动学 (B站)", "https://www.bilibili.com/video/BV1Ls411d7f5"),
            ("article", "牛顿定律 (Khan Academy)", "https://www.khanacademy.org/science/physics"),
        ],
        "电磁": [
            ("video", "静电场与磁场 (B站)", "https://www.bilibili.com/video/BV1Ls411d7f5"),
            ("article", "电磁感应 (Khan Academy)", "https://www.khanacademy.org/science/physics"),
        ],
    },
    # 思政类（POL 课程）
    "social": {
        "道德": [
            ("article", "人生观与价值观", "https://www.gov.cn/"),
            ("video", "思想道德与法治 (MOOC)", "https://www.icourse163.org/course/NENU-1002847003"),
        ],
        "法治": [
            ("article", "宪法与法治基础", "https://www.gov.cn/"),
        ],
    },
}

# 课程代码前缀 → 学科域
COURSE_DOMAIN: list[tuple[str, str]] = [
    ("MATH", "math"), ("PHY", "physics"), ("ENG", "english"),
    ("POL", "social"), ("CS", "programming"), ("SE", "programming"),
]

# 通用兜底资源
DEFAULT_RESOURCES: list[tuple] = [
    ("video", "B站学习区", "https://www.bilibili.com/v/study"),
    ("exercise", "牛客网在线练习", "https://www.nowcoder.com/"),
    ("article", "CSDN 技术社区", "https://www.csdn.net/"),
]


class ResourceRecommender:
    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = ResourceDAO(db)
        self._knowledge_dao = KnowledgeDAO(db)
        self._course_dao = CourseDAO(db)
        self._kg = KnowledgeGraph(db)

    @staticmethod
    def _course_domain(course_code: str) -> str:
        """根据课程代码前缀判断学科域."""
        for prefix, domain in COURSE_DOMAIN:
            if course_code.upper().startswith(prefix):
                return domain
        return "programming"

    def recommend(self, course_id: int, course_name: str = "", top_n: int = 8) -> list[dict]:
        # 1. 已有未完成推荐直接复用（按课程隔离）
        existing = self._dao.get_uncompleted(self._student_id, course_id)
        results = [self._to_item(r) for r in existing]

        if len(results) >= top_n:
            return results[:top_n]

        seen_titles = {e["title"] for e in existing}
        course = self._course_dao.get_by_id(course_id)
        course_code = course.course_code if course else ""
        course_name = course.course_name if course else course_name
        domain = self._course_domain(course_code)

        # 2. 课程专属资源（优先按课程名匹配以兼容历史代码错位，否则按课程代码精确匹配）
        alias_code = COURSE_NAME_ALIASES.get(course_name)
        pool = COURSE_RESOURCES.get(alias_code) if alias_code else None
        if pool is None:
            pool = COURSE_RESOURCES.get(course_code)

        if pool:
            for rtype, title, url in pool:
                if len(results) >= top_n:
                    break
                if title in seen_titles:
                    continue
                rid = self._dao.create(
                    self._student_id, None, course_id, rtype, title, url,
                    f"「{course_name}」专属推荐资源，助力课程学习",
                )
                seen_titles.add(title)
                results.append(self._to_item(self._dao.get_by_id(rid)))

        # 3. 薄弱知识点匹配（限定本课程知识点 + 本学科域资源）
        if len(results) < top_n:
            self._kg.build_graph(course_id, self._student_id)
            weak = self._kg.get_weak_nodes(self._student_id)
            for w in weak:
                if len(results) >= top_n:
                    break
                kp_name = w.get("kp_name", "")
                matched = self._match_kp_resources(kp_name, domain)
                for rtype, title, url in matched:
                    if len(results) >= top_n:
                        break
                    if title in seen_titles:
                        continue
                    rid = self._dao.create(
                        self._student_id, w["kp_id"], course_id, rtype, title, url,
                        f"薄弱知识点「{kp_name}」掌握度 {w['mastery']}%，建议加强学习",
                    )
                    seen_titles.add(title)
                    results.append(self._to_item(self._dao.get_by_id(rid)))

        # 4. 兜底通用资源
        if len(results) < top_n:
            for rtype, title, url in DEFAULT_RESOURCES:
                if len(results) >= top_n:
                    break
                if title in seen_titles:
                    continue
                rid = self._dao.create(
                    self._student_id, None, course_id, rtype, title, url,
                    f"「{course_name}」通用学习资源",
                )
                seen_titles.add(title)
                results.append(self._to_item(self._dao.get_by_id(rid)))

        return results[:top_n]

    @staticmethod
    def _match_kp_resources(kp_name: str, domain: str) -> list[tuple]:
        """按知识点名称关键词匹配（仅限本学科域资源），最长关键词优先."""
        text = kp_name.lower()
        domain_pool = KP_KEYWORD_RESOURCES.get(domain, {})
        scored = []
        for keyword, resources in domain_pool.items():
            if keyword.lower() in text:
                scored.append((len(keyword), resources))
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored:
            return scored[0][1]
        return []

    @staticmethod
    def _to_item(r: dict) -> dict:
        return {
            "id": r.get("id"),
            "kp_id": r.get("kp_id"),
            "kp_name": r.get("kp_name"),
            "course_id": r.get("course_id"),
            "type": r.get("resource_type"),
            "title": r.get("title"),
            "url": r.get("url"),
            "reason": r.get("reason"),
            "is_completed": bool(r.get("is_completed")),
        }

    def get_recommendations(self) -> list[dict]:
        return self._dao.get_by_student(self._student_id)

    def mark_done(self, rec_id: int) -> bool:
        return self._dao.mark_completed(rec_id)
