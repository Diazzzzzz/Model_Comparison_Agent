"""火山方舟 豆包·文生图 Seedream 客户端（生成 H5 场景背景图）。

generate_scene() 返回 {url, status, detail}
  status: ok / no_key / forced_mock / error
成功时把图片下载到本地 static/generated/ 再返回本地路径，
避免浏览器加载火山临时链接失败（表现为背景一片灰）。
"""
import os
import uuid
import requests
from config import Config

# 项目根目录（不依赖运行时 CWD）
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GEN_DIR = os.path.join(_BASE, "static", "generated")


def _build_prompt(scene: str) -> str:
    """把场景描述包装成一条具体、出片的车广告背景提示词。"""
    scene = (scene or "a scenic open road at golden hour").strip()
    return (
        f"{scene}. Professional automotive advertisement background plate, "
        f"empty scene with no vehicles, cinematic natural lighting, golden hour, "
        f"rich vivid colors, deep depth of field, ultra detailed, photorealistic, 4k"
    )


def generate_scene(prompt_en: str, timeout: int = 90) -> dict:
    if not Config.ARK_API_KEY:
        return _log({"url": None, "status": "no_key",
                     "detail": "未配置火山 ARK_API_KEY，H5 用内置渐变背景"})
    if Config.FORCE_MOCK:
        return _log({"url": None, "status": "forced_mock",
                     "detail": "FORCE_MOCK=1 已强制关闭真实图像生成"})

    url = f"{Config.ARK_BASE_URL}/images/generations"
    headers = {
        "Authorization": f"Bearer {Config.ARK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": Config.ARK_IMAGE_MODEL,
        "prompt": _build_prompt(prompt_en),
        "size": "2048x2048",  # Seedream 2K，满足最小像素要求
        "response_format": "url",
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return _log({"url": None, "status": "error",
                         "detail": f"火山返回 HTTP {resp.status_code}：{resp.text[:200]}"})
        remote_url = resp.json()["data"][0]["url"]
        local = _download(remote_url)
        if local:
            return _log({"url": local, "status": "ok",
                         "detail": f"火山生成成功并已本地缓存（模型 {Config.ARK_IMAGE_MODEL}）"})
        # 下载失败就退回用远程链接（至少还有机会显示）
        return _log({"url": remote_url, "status": "ok",
                     "detail": "火山生成成功（远程链接，本地缓存失败）"})
    except Exception as e:
        return _log({"url": None, "status": "error", "detail": f"火山调用异常：{e}"})


def _download(remote_url: str):
    """把火山返回的图片下载到 static/generated/，返回可访问的本地路径。"""
    try:
        r = requests.get(remote_url, timeout=60)
        if r.status_code != 200:
            return None
        os.makedirs(_GEN_DIR, exist_ok=True)
        fname = f"scene_{uuid.uuid4().hex[:12]}.png"
        with open(os.path.join(_GEN_DIR, fname), "wb") as f:
            f.write(r.content)
        return f"/static/generated/{fname}"
    except Exception:
        return None


def _log(result: dict) -> dict:
    print(f"[火山图像] status={result['status']} | {result['detail']}")
    return result
