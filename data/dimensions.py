"""对比维度字典（可替换 / 可扩展模块）。

设计目标：对比维度不再"车库有啥比啥"，而是【按这个客户挑相关的 6~8 条】，
并补齐出海关键维度（能耗、售后服务网络、保养成本）。

每条维度：
  key       内部键
  label     界面/对比表显示名
  spec      对应 car_library 里 specs 的字段名——【值只从车库取，绝不由模型编】
  base      基础维度：无论什么客户都比（价格/月供/安全）
  tags      场景关键词：命中这个客户的 care_most/worry/usage/车级 就优先选进来
  mock      演示模式下的默认结论：ours / rival / tie（真实模式由模型判断，忽略此字段）

⚠️ 替换真实车库时：只要 car_library 的 specs 里有对应 spec 字段，这里就能直接比；
   新增维度就往 DIMENSIONS 里加一条即可，上层不用动。
"""

DIMENSIONS = [
    # —— 基础维度：始终参与 ——
    {"key": "price",     "label": "指导价",       "spec": "指导价",     "base": True,  "mock": "ours",  "tags": ["性价比", "预算", "便宜", "价格"]},
    {"key": "loan",      "label": "参考月供",     "spec": "参考月供",   "base": True,  "mock": "ours",  "tags": ["月供", "预算", "压力", "性价比"]},
    {"key": "safety",    "label": "安全",         "spec": "安全",       "base": True,  "mock": "ours",  "tags": ["安全", "带娃", "孩子", "家人", "老人"]},
    # —— 出海关键补充维度 ——
    {"key": "fuel",      "label": "能耗/油耗",    "spec": "能耗油耗",   "mock": "rival", "tags": ["油耗", "能耗", "用车成本", "省", "经济", "跑得多", "网约"]},
    {"key": "range",     "label": "续航",         "spec": "续航",       "mock": "ours",  "tags": ["续航", "电", "充电", "纯电", "新能源"]},
    {"key": "service",   "label": "售后/服务网络", "spec": "售后服务",   "mock": "ours",  "tags": ["售后", "服务", "维修", "省心", "出海", "网点", "救援"]},
    {"key": "maintain",  "label": "保养成本",     "spec": "保养成本",   "mock": "ours",  "tags": ["保养", "用车成本", "维修", "跑得多", "省心", "耐用"]},
    # —— 常规维度：按客户在意点浮上来 ——
    {"key": "power",     "label": "动力",         "spec": "动力",       "mock": "ours",  "tags": ["动力", "越野", "超车", "操控", "马力"]},
    {"key": "wheelbase", "label": "轴距/空间",    "spec": "轴距",       "mock": "ours",  "tags": ["空间", "家用", "带娃", "五口", "乘坐", "腿部"]},
    {"key": "trunk",     "label": "后备箱",       "spec": "后备箱",     "mock": "ours",  "tags": ["空间", "装", "露营", "出游", "后备箱", "装备"]},
    {"key": "chassis",   "label": "底盘/悬架",    "spec": "底盘/悬架",  "mock": "tie",   "tags": ["底盘", "越野", "操控", "稳", "长途"]},
    {"key": "body",      "label": "车身用钢",     "spec": "车身用钢",   "mock": "ours",  "tags": ["安全", "用料", "碰撞", "钢"]},
    {"key": "cabin",     "label": "智能座舱",     "spec": "智能座舱",   "mock": "ours",  "tags": ["智能", "车机", "科技", "大屏", "导航"]},
    {"key": "warranty",  "label": "质保",         "spec": "质保",       "mock": "ours",  "tags": ["质保", "省心", "保值", "耐用"]},
]


def select_dimensions(customer: dict, our_car: dict, rival_car: dict, k: int = 8) -> list:
    """按这个客户挑 k 条相关维度。基础维度必进；其余按关键词命中打分。
    只保留【我方车库里有数据】的维度（没数据的不硬比，体现"查不到就不比"）。
    返回每条带上锁定的参数值 our_value / rival_value。
    """
    text = " ".join([
        customer.get("care_most", ""), customer.get("worry", ""),
        customer.get("usage", ""), customer.get("family", ""),
        our_car.get("level", ""),
    ])
    our_specs = our_car.get("specs", {})
    rival_specs = rival_car.get("specs", {})

    scored = []
    for d in DIMENSIONS:
        our_val = our_specs.get(d["spec"])
        if not our_val:                 # 我方没这条数据 → 不比
            continue
        score = 100 if d.get("base") else 0
        for kw in d.get("tags", []):
            if kw and kw in text:
                score += 10
        scored.append((score, d, our_val))

    scored.sort(key=lambda x: -x[0])
    out = []
    for score, d, our_val in scored[:k]:
        out.append({
            "key": d["key"], "label": d["label"], "spec": d["spec"],
            "mock": d.get("mock", "tie"),
            "our_value": our_val,
            "rival_value": rival_specs.get(d["spec"], "暂无数据"),
        })
    return out
