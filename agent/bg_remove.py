"""自动抠图（去背景）。

用 rembg 的本地模型，无需联网 key。首次使用会自动下载模型（约 170MB），
之后离线可用。若没装 rembg 或抠图失败，原样返回图片字节，不影响流程。
"""


def available() -> bool:
    try:
        import rembg  # noqa: F401
        return True
    except Exception:
        return False


def remove_bg(data: bytes) -> tuple:
    """输入图片字节 → 返回 (处理后字节, 是否成功抠图)。
    成功时返回带透明背景的 PNG 字节。"""
    try:
        from rembg import remove
        out = remove(data)
        return out, True
    except Exception as e:
        print(f"[抠图] 跳过，用原图（原因：{e}）")
        return data, False
