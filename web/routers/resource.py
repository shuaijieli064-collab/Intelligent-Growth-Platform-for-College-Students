import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import APIRouter, Depends, HTTPException

from web.schemas.resource import ResourceItem
from web.schemas.common import ApiResponse
from web.dependencies import get_db, get_course_dao, get_current_student_id
from data_layer.database import DatabaseManager
from data_layer.dao.course_dao import CourseDAO
from business_layer.resource_recommender import ResourceRecommender


router = APIRouter(prefix="/api/resource", tags=["resource"])


@router.get("/{course_id}", response_model=ApiResponse[list[ResourceItem]])
def get_resources(
    course_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
    course_dao: CourseDAO = Depends(get_course_dao),
):
    course = course_dao.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 归属校验：仅已选修该课程的学生可读取推荐资源
    enrolled = {c.course_id for c in course_dao.get_by_student(student_id)}
    if course_id not in enrolled:
        raise HTTPException(status_code=403, detail="无权访问该课程")

    recommender = ResourceRecommender(db, student_id)
    resources = recommender.recommend(course_id, course.course_name, 8)

    return ApiResponse(
        data=[
            ResourceItem(
                id=r.get("id"),
                student_id=student_id,
                kp_id=r.get("kp_id"),
                kp_name=r.get("kp_name"),
                course_id=r.get("course_id") or course_id,
                course_name=course.course_name,
                resource_type=r.get("type", ""),
                title=r.get("title", ""),
                url=r.get("url", ""),
                reason=r.get("reason", ""),
                is_completed=bool(r.get("is_completed")),
            )
            for r in resources
        ]
    )


@router.put("/{resource_id}/complete", response_model=ApiResponse[dict])
def complete_resource(
    resource_id: int,
    student_id: int = Depends(get_current_student_id),
    db: DatabaseManager = Depends(get_db),
):
    from data_layer.dao.resource_dao import ResourceDAO
    dao = ResourceDAO(db)
    item = dao.get_by_id(resource_id)
    if not item:
        raise HTTPException(status_code=404, detail="资源不存在")
    if item.get("student_id") != student_id:
        raise HTTPException(status_code=403, detail="无权操作该资源")
    dao.mark_completed(resource_id)
    return ApiResponse(data={"resource_id": resource_id}, message="标记完成成功")
