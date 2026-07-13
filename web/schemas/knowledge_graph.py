from typing import Optional
from pydantic import BaseModel


class KnowledgeNode(BaseModel):
    kp_id: int
    kp_name: str
    mastery_level: float = 0
    mastery_status: str = "weak"


class KnowledgeEdge(BaseModel):
    source: int
    target: int


class KnowledgeGraphResponse(BaseModel):
    nodes: list[KnowledgeNode]
    edges: list[KnowledgeEdge]


class WeakNode(BaseModel):
    kp_id: int
    kp_name: str
    mastery: float


class LearningPathNode(BaseModel):
    kp_id: int
    kp_name: str
    mastery: float
    order: int


class CreateKnowledgePointRequest(BaseModel):
    kp_name: str
    difficulty: Optional[int] = 1
    weight: Optional[float] = 1.0
    prerequisite_kp_id: Optional[int] = None


class UpdatePrerequisiteRequest(BaseModel):
    prerequisite_kp_id: int


class KnowledgePointResponse(BaseModel):
    kp_id: int
    kp_name: str
    course_id: int
    parent_kp_id: Optional[int] = None
    difficulty: int
    weight: float
