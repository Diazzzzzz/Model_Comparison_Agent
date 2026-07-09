"""客户标签（数据层 · 可替换模块）。

⚠️ 纯净版：不含内置示例客户。TAG_SCHEMA 是"顾客库统一字段"的定义，接入企业真实客户库 / CDP 时，
   保持字段结构、让 list_customers()/get_customer() 返回同结构 dict 即可。字段要增删也集中在这一处。
"""

# 客户画像的"统一字段"（架构里说的顾客库统一字段）
# key = 内部字段名；label = 界面显示名
TAG_SCHEMA = [
    {"key": "name", "label": "客户称呼"},
    {"key": "intent_car", "label": "意向车型"},
    {"key": "budget", "label": "预算 / 可接受月供"},
    {"key": "usage", "label": "主要用途"},
    {"key": "family", "label": "家庭结构"},
    {"key": "care_most", "label": "最在意的点"},
    {"key": "worry", "label": "主要顾虑"},
    {"key": "heat", "label": "意向热度"},
    {"key": "rival_car", "label": "正在纠结的竞品"},
]

# ← 接入真实客户库后在此填充。演示数据见 demo/* 分支。
_CUSTOMERS = {}


def list_customers():
    """[{id, name, intent_car, rival_car}, ...] 供界面下拉。"""
    return [
        {"id": cid, "name": c["name"], "intent_car": c["intent_car"], "rival_car": c["rival_car"]}
        for cid, c in _CUSTOMERS.items()
    ]


def get_customer(cid: str):
    return _CUSTOMERS.get(cid)


def blank_customer():
    """手动新建客户时的空模板。"""
    return {item["key"]: "" for item in TAG_SCHEMA}
