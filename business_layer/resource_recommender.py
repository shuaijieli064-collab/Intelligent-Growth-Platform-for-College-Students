"""学习资源推荐系统 - 基于薄弱知识点推荐."""
from data_layer.database import DatabaseManager
from data_layer.dao.resource_dao import ResourceDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from business_layer.knowledge_graph import KnowledgeGraph

# 预设资源库（已验证有效链接）
RESOURCE_POOL = {
    "程序": [
        ("video", "Python 入门教程 (B站)", "https://www.bilibili.com/video/BV1wD4y1o7AS"),
        ("exercise", "Python 在线练习 (菜鸟教程)", "https://www.runoob.com/python/python-exercise-examples.html"),
        ("article", "Python 官方中文教程", "https://docs.python.org/zh-cn/3/tutorial/index.html"),
        ("course", "中国大学 MOOC Python (北理工)", "https://www.icourse163.org/course/BIT-268001"),
    ],
    "数据": [
        ("video", "数据结构 (B站 青岛大学)", "https://www.bilibili.com/video/BV1nJ411V7bd"),
        ("exercise", "LeetCode 算法题库", "https://leetcode.cn/problemset/all/"),
        ("course", "数据结构 (浙大 MOOC)", "https://www.icourse163.org/course/ZJU-93001"),
    ],
    "算法": [
        ("video", "算法通关之路 (B站)", "https://www.bilibili.com/video/BV1Lv4y1e7HL"),
        ("exercise", "牛客网刷题平台", "https://www.nowcoder.com/"),
        ("course", "算法设计与分析 (Stanford)", "https://www.coursera.org/learn/algorithms-divide-conquer"),
    ],
    "数学": [
        ("video", "高等数学 (B站 宋浩)", "https://www.bilibili.com/video/BV1Eb411u7Fw"),
        ("exercise", "Khan Academy 数学", "https://www.khanacademy.org/math"),
        ("course", "高等数学 (同济 MOOC)", "https://www.icourse163.org/course/TONGJI-1001599002"),
    ],
    "语言": [
        ("video", "TED 演讲精选", "https://www.ted.com/talks"),
        ("exercise", "多邻国免费学语言", "https://www.duolingo.com/"),
        ("article", "BBC Learning English", "https://www.bbc.co.uk/learningenglish"),
    ],
    "网络": [
        ("video", "计算机网络 (B站 湖科大)", "https://www.bilibili.com/video/BV1c4411d7jb"),
        ("article", "MDN Web 文档", "https://developer.mozilla.org/zh-CN/"),
        ("course", "计算机网络 (哈工大 MOOC)", "https://www.icourse163.org/course/HIT-154005"),
    ],
    "原理": [
        ("video", "操作系统 (B站 王道)", "https://www.bilibili.com/video/BV1YE411D7nH"),
        ("course", "操作系统 (清华 MOOC)", "https://www.xuetangx.com/course/thu08091000237/19324299"),
    ],
    "面向对象": [
        ("video", "面向对象程序设计 (B站)", "https://www.bilibili.com/video/BV1Yb411W7VW"),
        ("article", "Python 面向对象教程", "https://www.liaoxuefeng.com/wiki/1016959663602400/1017495723838528"),
    ],
    "数据库": [
        ("video", "MySQL 教程 (B站 尚硅谷)", "https://www.bilibili.com/video/BV1iq4y1u7vj"),
        ("exercise", "SQL 在线练习 (SQLZoo)", "https://sqlzoo.net/"),
        ("course", "数据库系统概论 (人大 MOOC)", "https://www.icourse163.org/course/RUC-488001"),
    ],
    "linux": [
        ("video", "Linux 教程 (B站 韩顺平)", "https://www.bilibili.com/video/BV1Sv411r7vd"),
        ("article", "Linux 命令大全", "https://www.runoob.com/linux/linux-tutorial.html"),
    ],
    "概念": [
        ("article", "计算机科学导论 (MIT OCW)", "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/"),
        ("video", "计算机科学速成课 (Crash Course)", "https://www.bilibili.com/video/BV1EW411u7th"),
        ("course", "大学计算机基础 (MOOC)", "https://www.icourse163.org/course/WHU-1205729806"),
    ],
    "原理": [
        ("video", "计算机组成原理 (B站 王道)", "https://www.bilibili.com/video/BV1BE411D7ii"),
        ("article", "计算机科学自学指南 (TeachYourselfCS)", "https://teachyourselfcs.com/"),
    ],
    "方法": [
        ("article", "如何高效学习 (费曼技巧)", "https://zhuanlan.zhihu.com/p/22368895"),
        ("video", "学霸学习方法论 (B站)", "https://www.bilibili.com/video/BV1kJ411r7NX"),
    ],
    "实践": [
        ("exercise", "GitHub 项目实战", "https://github.com/topics/practice"),
        ("course", "实战编程 (freeCodeCamp)", "https://www.freecodecamp.org/chinese/learn"),
    ],
    "案例": [
        ("article", "经典编程案例分析 (菜鸟教程)", "https://www.runoob.com/design-pattern/design-pattern-tutorial.html"),
        ("video", "项目实战案例合集 (B站)", "https://www.bilibili.com/video/BV1bJ41187Kx"),
    ],
    "综合": [
        ("exercise", "综合编程题库 (洛谷)", "https://www.luogu.com.cn/"),
        ("video", "期末考试冲刺串讲 (B站)", "https://www.bilibili.com/video/BV1Ft41187Jw"),
    ],
    "回顾": [
        ("article", "CS 面试知识点汇总", "https://github.com/CyC2018/CS-Notes"),
        ("video", "期末总复习攻略 (B站)", "https://www.bilibili.com/video/BV1Yt411n7EG"),
    ],
    "web": [
        ("video", "Web 前端入门 (B站)", "https://www.bilibili.com/video/BV1g84y1qE2c"),
        ("exercise", "前端练习 (freeCodeCamp)", "https://www.freecodecamp.org/chinese/learn"),
    ],
    "_default": [
        ("video", "B站学习区", "https://www.bilibili.com/v/study"),
        ("exercise", "牛客网在线练习", "https://www.nowcoder.com/"),
        ("article", "CSDN 技术社区", "https://www.csdn.net/"),
    ],
}


class ResourceRecommender:
    def __init__(self, db: DatabaseManager, student_id: int) -> None:
        self._db = db
        self._student_id = student_id
        self._dao = ResourceDAO(db)
        self._knowledge_dao = KnowledgeDAO(db)
        self._kg = KnowledgeGraph(db)

    def recommend(self, course_id: int, course_name: str = "", top_n: int = 6) -> list[dict]:
        # 仅去重当前课程已有未完成推荐（不同课程各自独立）
        existing = self._dao.get_uncompleted(self._student_id, course_id)
        seen_titles = {e["title"] for e in existing}

        self._kg.build_graph(course_id)
        weak = self._kg.get_weak_nodes(self._student_id)

        results: list[dict] = []

        # 有薄弱点 → 先按 KP 名匹配，再按课程名加权
        if weak:
            for w in weak[:top_n]:
                kp_name = w.get("kp_name", "")
                matched = self._match_resources(kp_name, course_name)
                for rtype, title, url in matched[:2]:
                    if title in seen_titles:
                        continue
                    rid = self._dao.create(
                        self._student_id, w["kp_id"], rtype, title, url,
                        f"薄弱知识点「{kp_name}」掌握度 {w['mastery']}%，建议加强学习",
                    )
                    seen_titles.add(title)
                    results.append({
                        "id": rid, "kp_name": kp_name,
                        "type": rtype, "title": title, "url": url,
                        "reason": f"掌握度仅 {w['mastery']}%",
                    })
                    if len(results) >= top_n:
                        break
                if len(results) >= top_n:
                    break

        # 不够 → 用课程名相关资源补足
        if len(results) < top_n:
            course_matched = self._match_resources(course_name, "")
            for rtype, title, url in course_matched[:top_n - len(results)]:
                if title in seen_titles:
                    continue
                rid = self._dao.create(
                    self._student_id, None, rtype, title, url,
                    f"课程「{course_name}」推荐学习资源",
                )
                seen_titles.add(title)
                results.append({
                    "id": rid, "kp_name": course_name,
                    "type": rtype, "title": title, "url": url,
                    "reason": f"课程推荐",
                })

        # 不够 → 其他分类各取1条
        if len(results) < top_n:
            for keyword, resources in RESOURCE_POOL.items():
                if keyword == "_default":
                    continue
                if len(results) >= top_n:
                    break
                for rtype, title, url in resources[:1]:
                    if title in seen_titles:
                        continue
                    rid = self._dao.create(
                        self._student_id, None, rtype, title, url,
                        f"扩展学习推荐 — {keyword}",
                    )
                    seen_titles.add(title)
                    results.append({
                        "id": rid, "kp_name": keyword,
                        "type": rtype, "title": title, "url": url,
                        "reason": "扩展推荐",
                    })
                    break

        # 还不够 → 默认兜底
        if len(results) < top_n:
            for rtype, title, url in RESOURCE_POOL["_default"]:
                if title in seen_titles:
                    continue
                if len(results) >= top_n:
                    break
                rid = self._dao.create(
                    self._student_id, None, rtype, title, url, "通用学习资源推荐",
                )
                seen_titles.add(title)
                results.append({
                    "id": rid, "kp_name": "综合", "type": rtype,
                    "title": title, "url": url, "reason": "通用学习资源",
                })

        return results

    @staticmethod
    def _match_resources(kp_name: str, course_name: str = "") -> list[tuple]:
        """Match by KP name and course name keywords, longest match wins."""
        text = (kp_name + " " + course_name).lower()
        scored = []
        for keyword, resources in RESOURCE_POOL.items():
            if keyword == "_default":
                continue
            kw_lower = keyword.lower()
            if kw_lower in text:
                # Course name match gets bonus (more relevant)
                score = len(keyword)
                if kw_lower in course_name.lower():
                    score += 20
                scored.append((score, resources))
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored:
            return scored[0][1]
        return RESOURCE_POOL["_default"]

    def get_recommendations(self) -> list[dict]:
        return self._dao.get_by_student(self._student_id)

    def mark_done(self, rec_id: int) -> bool:
        return self._dao.mark_completed(rec_id)
