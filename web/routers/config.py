from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from web.schemas.common import ApiResponse
from config import LLM_CONFIG, save_llm_config_to_json, reload_llm_config

router = APIRouter(prefix="/api/config", tags=["config"])


class LlmConfigResponse(BaseModel):
    provider: str
    api_url: str
    model: str


class LlmConfigUpdate(BaseModel):
    provider: str
    api_key: str
    api_url: Optional[str] = ""
    model: Optional[str] = ""


@router.get("/llm", response_model=ApiResponse[LlmConfigResponse])
def get_llm_config():
    return ApiResponse(data=LlmConfigResponse(
        provider=LLM_CONFIG.get("provider", ""),
        api_url=LLM_CONFIG.get("api_url", ""),
        model=LLM_CONFIG.get("model", ""),
    ))


@router.put("/llm", response_model=ApiResponse[LlmConfigResponse])
def update_llm_config(config_in: LlmConfigUpdate):
    save_llm_config_to_json(
        provider=config_in.provider,
        api_key=config_in.api_key,
        api_url=config_in.api_url or "",
        model=config_in.model or "",
    )
    new_config = reload_llm_config()
    return ApiResponse(
        data=LlmConfigResponse(
            provider=new_config.get("provider", ""),
            api_url=new_config.get("api_url", ""),
            model=new_config.get("model", ""),
        ),
        message="配置更新成功",
    )
