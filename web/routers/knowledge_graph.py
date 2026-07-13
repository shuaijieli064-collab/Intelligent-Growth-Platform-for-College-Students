import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.knowledge_graph import (
    KnowledgeGraphResponse,
    KnowledgeNode,
    KnowledgeEdge,
    WeakNode,
    LearningPathNode,
    CreateKnowledgePointRequest,
    UpdatePrerequisiteRequest,
    KnowledgePointResponse,
)
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_course_dao, get_student_course_dao, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO, StudentCourseDAO
from data_layer.dao.knowledge_dao import KnowledgeDAO
from data_layer.models import KnowledgePoint
from business_layer.knowledge_graph import KnowledgeGraph


router = APIRouter(prefix="/api/knowledge-graph", tags=["knowledge-graph"])


def verify_kp_belongs_to_student(
    kp_id: int,
    student_id: int,
    db: DatabaseManager,
) -> dict:
    kp_dao = KnowledgeDAO(db)
    kp = kp_dao.get_kp_by_id(kp_id)
    if kp is None:
        raise HTTPException(status_code=404, detail="知识点不存在")
    sc_dao = StudentCourseDAO(db)
    student_courses = CourseDAO(db).get_by_student(student_id)
    student_course_ids = [c.course_id for c in student_courses]
    if kp["course_id"] not in student_course_ids:
        raise HTTPException(status_code=403, detail="无权操作该知识点")
    return kp


@router.get("/{course_id}", response_model=ApiResponse[KnowledgeGraphResponse])
def get_knowledge_graph(
    course_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    kg = KnowledgeGraph(db)
    kg.build_graph(course_id)
    colors = kg.mark_mastery(student_id)

    all_mastery = KnowledgeDAO(db).get_mastery_for_course(student_id, course_id)
    mastery_map = {m["kp_id"]: m["mastery_level"] for m in all_mastery}

    node_labels = kg.get_node_labels()
    nodes, edges = kg.get_graph_data()

    node_list = [
        KnowledgeNode(
            kp_id=n,
            kp_name=node_labels.get(n, f"KP-{n}"),
            mastery_level=mastery_map.get(n, 0),
            mastery_status=colors.get(n, "weak"),
        )
        for n in nodes
    ]

    edge_list = [
        KnowledgeEdge(source=e[0], target=e[1])
        for e in edges
    ]

    return ApiResponse(
        data=KnowledgeGraphResponse(nodes=node_list, edges=edge_list)
    )


@router.get("/{course_id}/weak-nodes", response_model=ApiResponse[list[WeakNode]])
def get_weak_nodes(
    course_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    kg = KnowledgeGraph(db)
    kg.build_graph(course_id)
    weak = kg.get_weak_nodes(student_id)

    return ApiResponse(
        data=[
            WeakNode(kp_id=w["kp_id"], kp_name=w["kp_name"], mastery=w["mastery"])
            for w in weak
        ]
    )


@router.get("/{course_id}/learning-path/{kp_id}", response_model=ApiResponse[list[LearningPathNode]])
def get_learning_path(
    course_id: int,
    kp_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    kg = KnowledgeGraph(db)
    kg.build_graph(course_id)

    chain = kg.get_prerequisite_chain(kp_id)
    chain.append(kp_id)

    all_mastery = KnowledgeDAO(db).get_mastery_for_course(student_id, course_id)
    mastery_map = {m["kp_id"]: m["mastery_level"] for m in all_mastery}
    node_labels = kg.get_node_labels()

    path = [
        LearningPathNode(
            kp_id=nid,
            kp_name=node_labels.get(nid, f"KP-{nid}"),
            mastery=mastery_map.get(nid, 0),
            order=i,
        )
        for i, nid in enumerate(chain)
    ]

    return ApiResponse(data=path)


@router.post("/{course_id}/nodes", response_model=ApiResponse[KnowledgePointResponse])
def create_knowledge_point(
    course_id: int,
    request: CreateKnowledgePointRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    course_dao = CourseDAO(db)
    student_courses = course_dao.get_by_student(student_id)
    student_course_ids = [c.course_id for c in student_courses]
    if course_id not in student_course_ids:
        raise HTTPException(status_code=403, detail="无权操作该课程")

    kp_dao = KnowledgeDAO(db)
    kp = KnowledgePoint(
        kp_name=request.kp_name,
        course_id=course_id,
        parent_kp_id=request.prerequisite_kp_id,
        difficulty=request.difficulty if request.difficulty is not None else 1,
        weight=request.weight if request.weight is not None else 1.0,
    )
    kp_id = kp_dao.create_knowledge_point(kp)

    created_kp = kp_dao.get_kp_by_id(kp_id)
    return ApiResponse(
        data=KnowledgePointResponse(
            kp_id=created_kp["kp_id"],
            kp_name=created_kp["kp_name"],
            course_id=created_kp["course_id"],
            parent_kp_id=created_kp["parent_kp_id"],
            difficulty=created_kp["difficulty"],
            weight=created_kp["weight"],
        )
    )


@router.delete("/nodes/{kp_id}", response_model=ApiResponse[dict])
def delete_knowledge_point(
    kp_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    verify_kp_belongs_to_student(kp_id, student_id, db)
    kp_dao = KnowledgeDAO(db)
    success = kp_dao.delete_knowledge_point(kp_id)
    if not success:
        raise HTTPException(status_code=404, detail="知识点删除失败")
    return ApiResponse(data={"success": True}, message="删除成功")


@router.put("/nodes/{kp_id}/prerequisite", response_model=ApiResponse[dict])
def update_prerequisite(
    kp_id: int,
    request: UpdatePrerequisiteRequest,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    kp = verify_kp_belongs_to_student(kp_id, student_id, db)
    prereq_kp = verify_kp_belongs_to_student(request.prerequisite_kp_id, student_id, db)
    if kp["course_id"] != prereq_kp["course_id"]:
        raise HTTPException(status_code=400, detail="先修知识点必须属于同一课程")

    kp_dao = KnowledgeDAO(db)
    success = kp_dao.update_parent_kp(kp_id, request.prerequisite_kp_id)
    if not success:
        raise HTTPException(status_code=400, detail="设置先修关系失败")
    return ApiResponse(data={"success": True}, message="先修关系设置成功")


@router.delete("/nodes/{kp_id}/prerequisite", response_model=ApiResponse[dict])
def remove_prerequisite(
    kp_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    verify_kp_belongs_to_student(kp_id, student_id, db)
    kp_dao = KnowledgeDAO(db)
    success = kp_dao.remove_parent_kp(kp_id)
    if not success:
        raise HTTPException(status_code=400, detail="移除先修关系失败")
    return ApiResponse(data={"success": True}, message="先修关系移除成功")
