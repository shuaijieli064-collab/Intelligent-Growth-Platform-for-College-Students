import os
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from web.routers.health import router as health_router
from web.routers.students import router as students_router
from web.routers.courses import router as courses_router
from web.routers.config import router as config_router
from web.routers.dashboard import router as dashboard_router
from web.routers.study_records import router as study_records_router
from web.routers.scores import router as scores_router
from web.routers.health_data import router as health_data_router
from web.routers.digital_twin import router as digital_twin_router
from web.routers.grade_predict import router as grade_predict_router
from web.routers.knowledge_graph import router as knowledge_graph_router
from web.routers.ai_coach import router as ai_coach_router
from web.routers.risk_warning import router as risk_warning_router
from web.routers.study_plan import router as study_plan_router
from web.routers.resource import router as resource_router
from web.routers.focus_monitor import router as focus_monitor_router
from web.routers.growth_archive import router as growth_archive_router
from web.routers.visualization import router as visualization_router
from web.routers.auth import router as auth_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="大学生智能成长平台 API")

# CORS 允许的来源：本地开发 + 环境变量配置（Cloudflare Pages 域名）
_cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://localhost:5176",
    "http://localhost:5177",
    "http://localhost:5178",
    "http://localhost:5179",
    "http://localhost:5180",
]
# 通过环境变量添加生产环境域名（逗号分隔）
_extra_origins = os.environ.get("CORS_ALLOW_ORIGINS", "")
if _extra_origins:
    _cors_origins.extend([o.strip() for o in _extra_origins.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    
    if request.url.path != "/health":
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.2f}ms"
        )
    
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception {exc.status_code}: {exc.detail} - {request.method} {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        errors.append(f"{loc}: {msg}")
    
    error_msg = "; ".join(errors) if errors else "请求参数验证失败"
    logger.warning(f"Validation Error: {error_msg} - {request.method} {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "message": error_msg,
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled Exception: {str(exc)} - {request.method} {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误，请稍后重试",
            "data": None,
        },
    )


app.include_router(health_router)
app.include_router(students_router)
app.include_router(courses_router)
app.include_router(config_router)
app.include_router(dashboard_router)
app.include_router(study_records_router)
app.include_router(scores_router)
app.include_router(health_data_router)
app.include_router(digital_twin_router)
app.include_router(grade_predict_router)
app.include_router(knowledge_graph_router)
app.include_router(ai_coach_router)
app.include_router(risk_warning_router)
app.include_router(study_plan_router)
app.include_router(resource_router)
app.include_router(focus_monitor_router)
app.include_router(growth_archive_router)
app.include_router(visualization_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "大学生智能成长平台 API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.main:app", host="0.0.0.0", port=8000, reload=True)
