"""每辆车的"多色车图 + 热区坐标"资产存储（内部管理页 /admin 写入，H5 读取）。

结构：
{ 车名: {
    "hotspots": {"front":[x%,y%], ...},          # 一套，所有颜色通用（同角度）
    "colors":   [{"name":"曜石黑","hex":"#1c1c1c","image":"/static/cars/xxx.png"}, ...]
} }

存成本地 JSON（data/car_assets.json）。运营数据，非代码——
1.0 用文件顶着，将来接真实素材库/数据库时替换这一层即可。
"""
import json
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE = os.path.join(_BASE, "data", "car_assets.json")


def _load() -> dict:
    if os.path.exists(_STORE):
        try:
            with open(_STORE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _normalize(a: dict) -> dict:
    """兼容旧格式（单张 image）→ 统一成 colors 列表。"""
    if "colors" not in a:
        img = a.get("image", "")
        a = {"hotspots": a.get("hotspots", {}),
             "colors": ([{"name": "默认", "hex": "#888888", "image": img}] if img else [])}
    a.setdefault("hotspots", {})
    a.setdefault("colors", [])
    return a


def all_assets() -> dict:
    return {k: _normalize(v) for k, v in _load().items()}


def get_asset(car_name: str):
    a = _load().get(car_name)
    return _normalize(a) if a else None


def save_asset(car_name: str, colors: list, hotspots: dict):
    data = _load()
    data[car_name] = {"hotspots": hotspots or {}, "colors": colors or []}
    os.makedirs(os.path.dirname(_STORE), exist_ok=True)
    with open(_STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data[car_name]
