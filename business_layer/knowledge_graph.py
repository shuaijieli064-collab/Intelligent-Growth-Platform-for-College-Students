"""知识图谱模块 - 基于 NetworkX 的课程知识图谱构建与分析."""
import networkx as nx

from data_layer.database import DatabaseManager
from data_layer.dao.knowledge_dao import KnowledgeDAO


class KnowledgeGraph:
    def __init__(self, db: DatabaseManager) -> None:
        self._dao = KnowledgeDAO(db)
        self.graph: nx.DiGraph = nx.DiGraph()
        self._node_labels: dict[int, str] = {}
        self._node_types: dict[int, str] = {}
        self._course_id: int = 0

    def build_graph(self, course_id: int, student_id: int | None = None) -> None:
        self._course_id = course_id
        self.graph = nx.DiGraph()
        self._node_labels.clear()
        self._node_types.clear()

        nodes = self._dao.get_knowledge_points(course_id, student_id)
        for n in nodes:
            self.graph.add_node(n["kp_id"])
            self._node_labels[n["kp_id"]] = n["kp_name"]
            self._node_types[n["kp_id"]] = n.get("node_type", "kp")

        edges = self._dao.get_edges(course_id, student_id)
        self.graph.add_edges_from(edges)

    def is_structure_node(self, kp_id: int) -> bool:
        """课程根/章等结构节点（无掌握度行，不参与薄弱统计）."""
        return self._node_types.get(kp_id, "kp") != "kp"

    def mark_mastery(self, student_id: int) -> dict[int, str]:
        mastery_data = self._dao.get_mastery_for_course(student_id, self._course_id)
        mastery_map = {m["kp_id"]: m["mastery_level"] for m in mastery_data}

        colors: dict[int, str] = {}
        for node in self.graph.nodes():
            if self.is_structure_node(node):
                colors[node] = "structure"
                continue
            level = mastery_map.get(node, 0)
            if level >= 80:
                colors[node] = "mastered"
            elif level >= 50:
                colors[node] = "in_progress"
            else:
                colors[node] = "weak"
        return colors

    def get_weak_nodes(self, student_id: int) -> list[dict]:
        colors = self.mark_mastery(student_id)
        # 一次性查询所有掌握度，避免 N+1 问题
        all_mastery = self._dao.get_mastery_for_course(student_id, self._course_id)
        mastery_map = {m["kp_id"]: m["mastery_level"] for m in all_mastery}

        weak = [
            {"kp_id": node, "kp_name": self._node_labels.get(node, ""),
             "mastery": mastery_map.get(node, 0)}
            for node in self.graph.nodes()
            if colors.get(node) == "weak" and not self.is_structure_node(node)
        ]

        if not weak:
            return weak
        try:
            order = list(nx.topological_sort(self.graph))
            weak.sort(key=lambda x: order.index(x["kp_id"]) if x["kp_id"] in order else 999)
        except nx.NetworkXUnfeasible:
            pass
        return weak

    def get_prerequisite_chain(self, target_kp_id: int) -> list[int]:
        chain = []
        for node in nx.ancestors(self.graph, target_kp_id):
            chain.append(node)
        try:
            order = list(nx.topological_sort(self.graph))
            chain.sort(key=lambda x: order.index(x) if x in order else 999)
        except nx.NetworkXUnfeasible:
            pass
        return chain

    def suggest_study_order(self, student_id: int) -> list[str]:
        weak = self.get_weak_nodes(student_id)
        if not weak:
            return []
        weak_ids = {w["kp_id"] for w in weak}
        subgraph = self.graph.subgraph(
            weak_ids | {a for w in weak_ids for a in nx.ancestors(self.graph, w)}
        )
        try:
            order = list(nx.topological_sort(subgraph))
            return [self._node_labels.get(nid, f"KP-{nid}") for nid in order
                    if nid in weak_ids]
        except nx.NetworkXUnfeasible:
            return [w["kp_name"] for w in weak]

    def get_centrality(self) -> dict[str, float]:
        if len(self.graph) == 0:
            return {}
        bc = nx.betweenness_centrality(self.graph)
        return {self._node_labels.get(k, f"KP-{k}"): round(v, 4)
                for k, v in sorted(bc.items(), key=lambda x: -x[1])}

    def get_graph_data(self) -> tuple[list, list]:
        return list(self.graph.nodes()), list(self.graph.edges())

    def get_node_labels(self) -> dict[int, str]:
        return dict(self._node_labels)

    def get_node_positions(self) -> dict[int, tuple[float, float]]:
        if len(self.graph) == 0:
            return {}
        try:
            return nx.spring_layout(self.graph, seed=42)
        except Exception:
            return nx.circular_layout(self.graph)
