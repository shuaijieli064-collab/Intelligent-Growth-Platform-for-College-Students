import ipaddress
import socket
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from web.schemas.common import ApiResponse
from web.dependencies import get_current_user, require_admin, get_admin_usernames
from data_layer.models import User
import config
from config import save_llm_config_to_json, reload_llm_config

router = APIRouter(prefix="/api/config", tags=["config"])


class LlmConfigResponse(BaseModel):
    provider: str
    api_url: str
    model: str
    api_key: str  # 仅返回脱敏掩码，不回传真实值
    can_write: bool = True  # 当前用户是否有权修改配置


class LlmConfigUpdate(BaseModel):
    provider: str
    api_key: str = ""
    api_url: Optional[str] = ""
    model: Optional[str] = ""


def _mask_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}****{key[-4:]}"


def _validate_api_url(url: str) -> None:
    """SSRF 防护：仅允许 http(s)，禁止内网/回环/链路本地等地址."""
    if not url:
        return
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="api_url 仅支持 http/https")
    host = parsed.hostname
    if not host:
        raise HTTPException(status_code=400, detail="api_url 无效")

    def _is_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
        return any([
            ip.is_private, ip.is_loopback, ip.is_link_local,
            ip.is_reserved, ip.is_multicast, ip.is_unspecified,
        ])

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        if host.lower() == "localhost":
            raise HTTPException(status_code=400, detail="api_url 不能指向本地地址")
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror:
            raise HTTPException(status_code=400, detail="api_url 域名无法解析")
        for info in infos:
            try:
                if _is_blocked(ipaddress.ip_address(info[4][0])):
                    raise HTTPException(
                        status_code=400, detail="api_url 不能指向内网地址"
                    )
            except ValueError:
                continue
    else:
        if _is_blocked(ip):
            raise HTTPException(status_code=400, detail="api_url 不能指向内网地址")


@router.get("/llm", response_model=ApiResponse[LlmConfigResponse])
def get_llm_config(current_user: User = Depends(get_current_user)):
    llm_config = config.LLM_CONFIG
    admins = get_admin_usernames()
    can_write = not admins or current_user.username in admins
    return ApiResponse(data=LlmConfigResponse(
        provider=llm_config.get("provider", ""),
        api_url=llm_config.get("api_url", ""),
        model=llm_config.get("model", ""),
        api_key=_mask_key(llm_config.get("api_key", "")),
        can_write=can_write,
    ))


@router.put("/llm", response_model=ApiResponse[LlmConfigResponse])
def update_llm_config(
    config_in: LlmConfigUpdate,
    _: User = Depends(require_admin),
):
    _validate_api_url(config_in.api_url or "")

    # 掩码或空值表示"保持现有 Key 不变"，避免掩码被当作真实 key 保存
    api_key = config_in.api_key.strip()
    if not api_key or "****" in api_key:
        api_key = config.LLM_CONFIG.get("api_key", "")

    save_llm_config_to_json(
        provider=config_in.provider,
        api_key=api_key,
        api_url=config_in.api_url or "",
        model=config_in.model or "",
    )
    new_config = reload_llm_config()
    return ApiResponse(
        data=LlmConfigResponse(
            provider=new_config.get("provider", ""),
            api_url=new_config.get("api_url", ""),
            model=new_config.get("model", ""),
            api_key=_mask_key(new_config.get("api_key", "")),
        ),
        message="配置更新成功",
    )
