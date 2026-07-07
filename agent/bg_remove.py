"""自动抠图（去背景）。本地 rembg 模型，无需联网 key。

首次使用某模型会自动下载（一次性）。可在 .env 调：
  REMBG_MODEL   默认 isnet-general-use；想要最好效果设 birefnet-general（模型大、慢）
  REMBG_ALPHA   设 1 开启 alpha matting（边缘更细，但更慢）
大图会先缩到 1400px 再抠，提速；H5 显示够用。
没装 rembg 或抠图失败时，原样返回图片字节，不影响流程。
"""
import os

_session = None


def available() -> bool:
    try:
        import rembg  # noqa: F401
        return True
    except Exception:
        return False


def _get_session():
    global _session
    if _session is None:
        from rembg import new_session
        _session = new_session(os.getenv("REMBG_MODEL", "isnet-general-use"))
    return _session


def _maybe_downscale(data: bytes, max_side: int = 1400) -> bytes:
    """大图先缩到 max_side 再抠，显著提速。失败则原样返回。"""
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



def remove_bg(data: bytes) -> tuple:
    """输入图片字节 → 返回 (处理后字节, 是否成功抠图)。成功时是透明 PNG。"""
    try:
        from rembg import remove
        data = _maybe_downscale(data)
        kw = {"session": _get_session()}
        if os.getenv("REMBG_ALPHA", "0") == "1":
            kw.update(alpha_matting=True, alpha_matting_foreground_threshold=240,
                      alpha_matting_background_threshold=15, alpha_matting_erode_size=11)
        return remove(data, **kw), True
    except Exception as e:
        print(f"[抠图] 跳过，用原图（原因：{e}）")
        return data, False
