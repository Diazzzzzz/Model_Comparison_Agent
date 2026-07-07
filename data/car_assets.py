"""每辆车的"图片 + 热区坐标"资产存储（内部管理页 /admin 写入，H5 读取）。

结构：{ 车名: {"image": "/static/cars/xxx.png", "hotspots": {"front":[x%,y%], ...}} }
存成本地 JSON（data/car_assets.json）。这是运营数据，不是代码——
1.0 用文件顶着，将来接你们真实素材库/数据库时替换这一层即可。
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


def all_assets() -> dict:
    return _load()


def get_asset(car_name: str):
    """返回该车的 {image, hotspots}，没有则 None。"""
    return _load().get(car_name)


def save_asset(car_name: str, image_path: str, hotspots: dict):
    """写入/更新一辆车的图片路径 + 热区坐标。"""
    data = _load()
    existing = data.get(car_name, {})
    data[car_name] = {
        "image": image_path or existing.get("image", ""),
        "hotspots": hotspots or existing.get("hotspots", {}),
    }
    os.makedirs(os.path.dirname(_STORE), exist_ok=True)
    with open(_STORE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data[car_name]
