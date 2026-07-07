"""自动抠图（去背景）。可切换两种抠图来源：

  CUTOUT_PROVIDER=local  本地 rembg 模型（免费，CPU，稍慢）
  CUTOUT_PROVIDER=volc   火山视觉智能（GPU，质量高、快；需 VOLC_AK / VOLC_SK）

火山走 CarSegment（车辆分割），返回 4 通道透明前景图。
火山失败会自动回退到本地 rembg，尽量不让流程断。
本地相关调节：REMBG_MODEL / REMBG_ALPHA（见 .env.example）。
"""
import base64
import os
from config import Config

_session = None


# ---------------- 本地 rembg ----------------
def _get_session():
    global _session
    if _session is None:
        from rembg import new_session
        _session = new_session(os.getenv("REMBG_MODEL", "isnet-general-use"))
    return _session


def _maybe_downscale(data: bytes, max_side: int = 1400) -> bytes:
    try:
        import io
        from PIL import Image
        im = Image.open(io.BytesIO(data))
        if max(im.size) <= max_side:
            return data
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, "PNG")
        return buf.getvalue()
    except Exception:
        return data


def _local_cutout(data: bytes) -> tuple:
    try:
        from rembg import remove
        data = _maybe_downscale(data)
        kw = {"session": _get_session()}
        if os.getenv("REMBG_ALPHA", "0") == "1":
            kw.update(alpha_matting=True, alpha_matting_foreground_threshold=240,
                      alpha_matting_background_threshold=15, alpha_matting_erode_size=11)
        return remove(data, **kw), True
    except Exception as e:
        print(f"[抠图] 本地 rembg 跳过，用原图（原因：{e}）")
        return data, False


# ---------------- 火山视觉智能 ----------------
def _find_foreground_b64(res: dict):
    """从火山返回里找出那张前景图的 base64。"""
    data = res.get("data") or {}
    for k in ("foreground_image", "image", "binary_data_base64", "foreground", "image_base64"):
        v = data.get(k)
        if isinstance(v, list) and v:
            v = v[0]
        if isinstance(v, str) and len(v) > 200:
            return v
    for v in data.values():                       # 兜底：扫一个明显是 base64 的长字符串
        if isinstance(v, str) and len(v) > 2000:
            return v
    return None


def _volc_cutout(data: bytes) -> tuple:
    try:
        from volcengine.visual.VisualService import VisualService
        vs = VisualService()
        vs.set_ak(Config.VOLC_AK)
        vs.set_sk(Config.VOLC_SK)
        form = {
            "image_base64": base64.b64encode(_maybe_downscale(data)).decode(),
            "return_foreground_image": "1",
        }
        res = getattr(vs, Config.VOLC_SEG_ACTION)(form)
        if str(res.get("code")) not in ("10000", "0"):
            print(f"[抠图] 火山返回异常：code={res.get('code')} msg={res.get('message')}")
            return data, False
        b64 = _find_foreground_b64(res)
        if not b64:
            print(f"[抠图] 火山没找到前景图字段，data keys={list((res.get('data') or {}).keys())}")
            return data, False
        return base64.b64decode(b64), True
    except Exception as e:
        print(f"[抠图] 火山调用异常：{e}")
        return data, False


# ---------------- 对外统一入口 ----------------
def available() -> bool:
    if Config.CUTOUT_PROVIDER == "volc":
        return bool(Config.VOLC_AK and Config.VOLC_SK)
    try:
        import rembg  # noqa: F401
        return True
    except Exception:
        return False


def remove_bg(data: bytes) -> tuple:
    """输入图片字节 → 返回 (处理后字节, 是否成功抠图)。成功时是透明 PNG。"""
    if Config.CUTOUT_PROVIDER == "volc" and Config.VOLC_AK and Config.VOLC_SK:
        out, ok = _volc_cutout(data)
        if ok:
            return out, True
        print("[抠图] 火山失败，回退本地 rembg")
    return _local_cutout(data)
