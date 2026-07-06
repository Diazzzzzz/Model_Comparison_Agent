"""火山方舟 豆包·文生图 Seedream 客户端（生成 H5 场景背景图）。

generate_scene() 返回一个 dict：{url, status, detail}
  status: ok / no_key / forced_mock / error
这样上层能把"火山到底成没成功、为啥失败"显示给用户看，而不是静默兜底。
"""
import requests
from config import Config


def generate_scene(prompt_en: str, timeout: int = 90) -> dict:
    """按英文提示词生成场景背景图。返回 {url, status, detail}。"""
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
        "prompt": f"{prompt_en}, cinematic, wide banner, no car, no text",
        "size": "2048x2048",  # Seedream 2K，4.19M像素，远超最小要求
        "response_format": "url",
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        if resp.status_code != 200:
            return _log({"url": None, "status": "error",
                         "detail": f"火山返回 HTTP {resp.status_code}：{resp.text[:200]}"})
        img_url = resp.json()["data"][0]["url"]
        return _log({"url": img_url, "status": "ok",
                     "detail": f"火山生成成功（模型 {Config.ARK_IMAGE_MODEL}）"})
    except Exception as e:
        return _log({"url": None, "status": "error", "detail": f"火山调用异常：{e}"})


def _log(result: dict) -> dict:
    """同时打印到终端，方便本地排查。"""
    print(f"[火山图像] status={result['status']} | {result['detail']}")
    return result
