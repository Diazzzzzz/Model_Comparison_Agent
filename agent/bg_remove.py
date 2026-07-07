"""自动抠图（去背景）。

用 rembg 本地模型，无需联网 key。首次使用某模型会自动下载（一次性）。
模型和边缘优化可在 .env 里调：
  REMBG_MODEL   默认 isnet-general-use（比老的 u2net 边缘干净很多）
                想要更强可设 birefnet-general（效果最好但模型大、慢）
  REMBG_ALPHA   设 1 开启 alpha matting（边缘更细腻，但更慢，偶有毛边）
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


def remove_bg(data: bytes) -> tuple:
    """输入图片字节 → 返回 (处理后字节, 是否成功抠图)。成功时是透明 PNG。"""
    try:
        from rembg import remove
        kw = {"session": _get_session()}
        if os.getenv("REMBG_ALPHA", "0") == "1":
            kw.update(alpha_matting=True,
                      alpha_matting_foreground_threshold=240,
                      alpha_matting_background_threshold=15,
                      alpha_matting_erode_size=11)
        return remove(data, **kw), True
    except Exception as e:
        print(f"[抠图] 跳过，用原图（原因：{e}）")
        return data, False
