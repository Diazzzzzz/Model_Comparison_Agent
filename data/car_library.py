"""车型库（数据层 · 可替换模块）。

⚠️ 纯净版：不含任何车企数据。与企业合作后，在这里接入该车企的真实车型库 / RAG，
   让 get_car(name) / list_cars() 返回下面结构的 dict 即可，上层逻辑一行都不用改。

一台车的标准结构（接数据时照此填）：
  {
    "name":  "车型名",
    "brand": "品牌",
    "is_ours": True,          # ← 我方/意向车 = True；竞品 = False
    "level": "车级",          # 如 紧凑型SUV / 紧凑型轿车
    "specs": {                # 维度值只从这里取（数字锁）；字段名与 data/dimensions.py 的 spec 对应
        "指导价": "...", "参考月供": "...", "动力": "...", "轴距": "...",
        "后备箱": "...", "底盘/悬架": "...", "安全": "...", "车身用钢": "...",
        "智能座舱": "...", "质保": "...", "能耗油耗": "...", "售后服务": "...",
        "保养成本": "...",
    },
    "highlights": ["卖点1", "卖点2"],
  }

说明：工具一律【倾向 is_ours=True 的车（意向车/我方）】，与品牌无关——
      谁的数据接进来、谁被选为意向车，就向着谁。
"""

# ← 接入真实车型库后在此填充（我方 + 竞品）。演示数据见 demo/* 分支。
_CARS = {}


def list_cars():
    """返回所有车型的简要列表：[{name, brand, is_ours, level}, ...]"""
    return [
        {"name": c["name"], "brand": c["brand"], "is_ours": c["is_ours"], "level": c["level"]}
        for c in _CARS.values()
    ]


def our_cars():
    return [c for c in list_cars() if c["is_ours"]]


def rival_cars():
    return [c for c in list_cars() if not c["is_ours"]]


def get_car(name: str):
    """按车名取完整车型数据。找不到返回 None。"""
    return _CARS.get(name)
