"""火山方舟 豆包·文生图 Seedream 客户端（生成 H5 场景背景图）。

可选：没配 ARK_API_KEY 时，generate_scene() 返回 None，
H5 会自动用内置的 SVG 场景背景兜底（不是灰占位，是带氛围的矢量背景）。
"""
import requests
from config import Config


def generate_scene(prompt_en: str, timeout: int = 90):
    """按英文提示词生成一张场景背景图，返回图片 URL；失败或没 key 返回 None。"""
    if not Config.image_enabled():
        return None
    url = f"{Config.ARK_BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {Config.ARK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.ARK_IMAGE_MODEL,
        "prompt": f"{prompt_en}, cinematic, wide banner, no car, no text",
        "size": "1024x576",
        "response_format": "url",
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return None
        return resp.json()["data"][0]["url"]
    except Exception:
        return None
