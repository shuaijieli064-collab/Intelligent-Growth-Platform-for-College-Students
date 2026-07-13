"""通用 LLM API 客户端 - 兼容 OpenAI 接口格式."""
import json
import requests


class LLMClient:
    def __init__(self, api_key: str, api_url: str, model: str = "glm-4-flash") -> None:
        self._api_key = api_key
        self._api_url = api_url
        self._model = model

    def chat_completion(self, messages: list[dict],
                        temperature: float = 0.7,
                        max_tokens: int = 1024) -> dict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        resp = requests.post(
            self._api_url, headers=headers, json=payload, timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return {"content": content, "tokens_used": tokens}

    def test_connection(self) -> bool:
        try:
            self.chat_completion(
                [{"role": "user", "content": "Hello"}], max_tokens=10,
            )
            return True
        except Exception:
            return False
