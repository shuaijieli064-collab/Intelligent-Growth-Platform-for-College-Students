from fastapi import APIRouter, Depends
from typing import List

from web.dependencies import get_student_dao
from web.schemas.student import StudentResponse
from data_layer.dao.student_dao import StudentDAO

router = APIRouter(prefix="/api", tags=["test"])


@router.get("/test", response_model=List[StudentResponse])
async def test_students(student_dao: StudentDAO = Depends(get_student_dao)):
    students = student_dao.get_all()
    return students
