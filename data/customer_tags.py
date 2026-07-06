"""客户标签（模拟数据 + 标准字段定义）。

⚠️ 这是【可替换模块】——按需求，客户标签模块要能整体换成你们真实标签。
   替换方式：保持 TAG_SCHEMA 的字段结构 + 让 list_customers()/get_customer()
   返回同样结构的 dict，即可无缝接入你们真实客户库。字段名要改也集中在这一处。
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
        "intent_car": "长城哈弗H6",
        "budget": "15万内，月供3000内",
        "usage": "城市通勤 + 周末带娃出游",
        "family": "三口之家，有一个2岁小孩",
        "care_most": "安全、空间、性价比",
        "worry": "担心国产车不如合资保值、怕小毛病多",
        "heat": "高（已看车2次，比价中）",
        "rival_car": "丰田RAV4荣放",
    },
    "c2": {
        "name": "李女士",
        "intent_car": "长城坦克300",
        "budget": "20万左右",
        "usage": "自驾越野、露营",
        "family": "夫妻二人，爱玩户外",
        "care_most": "越野能力、外观硬朗、装备空间",
        "worry": "油耗高不高、城市开好不好停",
        "heat": "中（在坦克300和途观L之间摇摆）",
        "rival_car": "大众途观L",
    },
    "c3": {
        "name": "张先生",
        "intent_car": "长城哈弗H6",
        "budget": "18万，看重月供压力小",
        "usage": "网约车 + 家用",
        "family": "夫妻 + 老人，五口人",
        "care_most": "空间、耐用、用车成本",
        "worry": "跑得多，担心后期维修保养贵",
        "heat": "高（本周想定）",
        "rival_car": "大众途观L",
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
