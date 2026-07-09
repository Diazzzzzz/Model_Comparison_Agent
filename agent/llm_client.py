"""DeepSeek 文本模型客户端（OpenAI 兼容接口）。

可替换：想换别的模型，只改这一个文件的 chat() 即可。
"""
import json
import re
import requests
from config import Config


class LLMError(Exception):
    pass


def chat(system: str, user: str, timeout: int = 60) -> str:
    """调 DeepSeek，返回模型输出的纯文本。"""
    url = f"{Config.DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,  # 销售工具求稳，降低发散/编造倾向
        "response_format": {"type": "json_object"},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
    if resp.status_code != 200:
        raise LLMError(f"DeepSeek 返回 {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"]


def chat_json(system: str, user: str) -> dict:
    """调模型并把返回解析成 JSON（带兜底：抠出第一个 {...}）。"""
    raw = chat(system, user)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group(0))
        raise LLMError(f"模型没返回合法 JSON：{raw[:300]}")
