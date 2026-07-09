"""客户标签（模拟数据 + 标准字段定义）。

⚠️ 这是【可替换模块】——按需求，客户标签模块要能整体换成你们真实标签。
   替换方式：保持 TAG_SCHEMA 的字段结构 + 让 list_customers()/get_customer()
   返回同样结构的 dict，即可无缝接入你们真实客户库。字段名要改也集中在这一处。

当前为【东风本田演示版】。
"""

# 客户画像的"统一字段"（就是架构里说的顾客库统一字段）
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

_CUSTOMERS = {
    "c1": {
        "name": "王先生",
        "intent_car": "本田CR-V",
        "budget": "20万内，月供4000内",
        "usage": "城市通勤 + 周末带娃出游",
        "family": "三口之家，有一个2岁小孩",
        "care_most": "空间、安全、保值率",
        "worry": "担心油耗、保值率是不是不如丰田",
        "heat": "高（已看车2次，比价中）",
        "rival_car": "丰田RAV4荣放",
    },
    "c2": {
        "name": "陈先生",
        "intent_car": "本田思域",
        "budget": "15万左右",
        "usage": "上下班通勤，偶尔跑山、约朋友",
        "family": "单身，年轻首购",
        "care_most": "动力、操控、外观颜值",
        "worry": "后排空间够不够、油耗高不高",
        "heat": "中（在思域和卡罗拉之间摇摆）",
        "rival_car": "丰田卡罗拉",
    },
    "c3": {
        "name": "张女士",
        "intent_car": "本田CR-V",
        "budget": "20万，看重用车成本",
        "usage": "家用 + 接送老人小孩",
        "family": "夫妻 + 老人，五口人",
        "care_most": "空间、可靠、保养便宜",
        "worry": "跑得多，担心后期保养保值",
        "heat": "高（本周想定）",
        "rival_car": "丰田RAV4荣放",
    },
}


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
