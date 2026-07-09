"""演示模式(MOCK)下的输出生成。

没配 DeepSeek key 时用这里：直接拿【已挑好并锁定参数值的维度】拼出一份像样的对比，
让整个流程在零 key 情况下也能完整跑通、可演示。
填了 key 后就走真模型（见 comparison.py），这里不再参与。

占优判断：数值型维度按【真实参数】比大小定谁占优（换数据也不会说错）；
非数值维度用维度字典里的默认结论兜底。
"""
import re
from agent.prompts import HOTSPOT_PARTS

# 数值型维度：越大越好 / 越小越好（用于按真实数值判占优）
_HIGHER_BETTER = {"轴距", "后备箱", "动力"}
_LOWER_BETTER = {"指导价", "参考月供", "能耗油耗", "保养成本"}


def _num(s):
    m = re.search(r"\d+(?:\.\d+)?", s or "")
    return float(m.group()) if m else None


def _smart_winner(spec, our_v, rival_v, fallback):
    """数值型维度按真实数值比；比不了就用维度字典的默认结论。差距 <1% 视为相当(tie)。"""
    o, r = _num(our_v), _num(rival_v)
    if o is not None and r is not None and (spec in _HIGHER_BETTER or spec in _LOWER_BETTER):
        hi = max(abs(o), abs(r)) or 1
        if abs(o - r) / hi < 0.01:          # 差距小于 1%，算相当
            return "tie"
        better_when_higher = spec in _HIGHER_BETTER
        return "ours" if (o > r) == better_when_higher else "rival"
    return fallback


# 维度与"客户在意点/顾虑"的关联词：用于优先保留客户已经担心的那条短板（正好用找补正面回应）
_SPEC_HINT = {
    "指导价": ["价格", "预算", "便宜", "贵", "性价比"],
    "参考月供": ["月供", "预算", "压力"],
    "能耗油耗": ["油耗", "能耗", "省", "用车成本"],
    "后备箱": ["空间", "后备箱", "装", "大"],
    "轴距": ["空间", "后排", "乘坐", "腿"],
    "保养成本": ["保养", "用车成本"],
    "品牌保值": ["保值", "品牌", "二手"],
}


def _hits(text, spec):
    return any(kw in text for kw in _SPEC_HINT.get(spec, []))


def build_mock_result(customer, our_car, rival_car, dims):
    """dims: data/dimensions.select_dimensions() 挑好的维度。

    立场：倾向【意向车（我方）】——参数事实不造假（数字锁），只诚实让最多 2 条短板，
    且优先留客户已经在担心的那条（正好用找补正面回应），其余短板不上桌、优势排在前面。
    完全数据驱动、与品牌无关：换任何车企的数据都适用，不预设我方在哪些维度占优。
    """
    care = customer.get("care_most", "").strip() or "性价比"
    worry = customer.get("worry", "").strip()
    care_worry = care + " " + worry

    rows = []
    for d in dims:
        winner = _smart_winner(d["spec"], d["our_value"], d["rival_value"], d.get("mock", "tie"))
        rows.append({
            "name": d["label"], "spec": d["spec"],
            "our_value": d["our_value"], "rival_value": d["rival_value"],
            "winner": winner,
            "comment": _mock_comment(d["spec"], winner, rival_car),
        })

    wins = [r for r in rows if r["winner"] == "ours"]
    ties = [r for r in rows if r["winner"] == "tie"]
    losses = [r for r in rows if r["winner"] == "rival"]
    # 倾向意向车：短板最多上桌 2 条，优先留客户已经在担心的那条
    losses.sort(key=lambda r: 0 if _hits(care_worry, r["spec"]) else 1)
    dimensions = wins + ties + losses[:2]     # 先亮优势，短板压到最后且只留 1~2 条

    # 话术从"实际占优的维度"动态生成——不预设我方赢在哪几项
    adv = "、".join(r["name"] for r in wins[:3]) or "多个关键方面"
    talk = (
        f"{customer.get('name','您')}，我特别理解您最看重{care}。{our_car['name']} 和 {rival_car['name']} 比，"
        f"{our_car['name']} 在 {adv} 这些方面更有优势，正是您日常最有感的地方。"
    )
    if worry:
        talk += (f"您担心的『{worry}』，我跟您交个底：这方面对方或许略强，但差距不大；"
                 f"{our_car['name']} 在更关键的地方更值、综合体验更好。")
    talk += "我建议您今天就试驾感受一下，很多客户一开就有数了。"

    return {
        "summary": f"更懂{care}的那台",
        "dimensions": dimensions,
        "talk_track": talk,
        "h5": {
            "scene_title": f"为{care}而来 · {our_car['name']}",
            "scene_prompt": _scene_prompt(our_car),
            "hotspots": _mock_hotspots(our_car),
        },
    }


def _scene_prompt(our_car):
    """按车型给一个具体、出片的场景（SUV 走户外，轿车走都市/公路）。"""
    level = our_car.get("level", "")
    if "越野" in level or "SUV" in level:
        return ("a scenic mountain road trip at golden hour, green forest and open sky, "
                "warm cinematic light, family outdoor mood, clean empty road")
    return ("a stylish city night street with light trails and neon reflections, "
            "dynamic youthful mood, cinematic lighting, clean empty road")


# 我方占优时的正向点评
_WIN = {
    "指导价": "价格更亲民，同样的钱配置更高",
    "参考月供": "月供更低，每月少还几百，压力小一圈",
    "安全": "全系标配，带娃出行这一条最实在",
    "能耗油耗": "油耗更低，一年下来省不少油钱",
    "售后服务": "服务网络密、坏了有人管、修得起，省心",
    "保养成本": "保养便宜、周期长，跑得多也养得起",
    "后备箱": "后排放倒能塞下婴儿车/露营装备，出行不用取舍",
    "车身用钢": "关键部位用料足，碰撞时更护人",
    "智能座舱": "大屏好用，导航语音一句话搞定",
    "质保": "质保更长，后期省心又省钱",
    "轴距": "轴距更长，后排腿部空间更宽敞",
    "动力": "动力更足，超车并线更从容",
    "底盘/悬架": "底盘扎实，长途和烂路都更稳",
}

# 我方劣势时给销售的"找补"话术
_LOSE = {
    "指导价": "【找补】价格是略高一点，但配置、用料和空间给得更足，落地算下来不虚",
    "参考月供": "【找补】月供略高一点点，差不了多少，但车更值、开着更好，长期更划算",
    "能耗油耗": "【找补】对方这项确实略省，但差距很小，综合用车成本不吃亏",
    "后备箱": "【找补】后备箱略小一点，但日常够用，后排放倒照样能装",
    "轴距": "【找补】轴距略短一点，实际乘坐空间不吃亏",
    "动力": "【找补】这项参数对方略高，但我们调校更好开，日常更够用",
    "保养成本": "【找补】保养略贵一点，但网点多、省心",
}


def _mock_comment(spec, winner, rival_car):
    if winner == "ours":
        return _WIN.get(spec, "这一项对您的用车场景更合适")
    if winner == "rival":
        return _LOSE.get(spec, f"【找补】这项{rival_car['brand']}略强，但差距不大，我方在更关键的点上占优，综合更划算")
    return "两者接近，看个人偏好"


def _mock_hotspots(our_car):
    specs = our_car["specs"]
    # 每项：(标题, 数据, 人话解读)
    text = {
        "front": ("动力更从容", specs.get('动力', '强劲动力'),
                  "红灯一转绿，你轻点油门，推背感稳稳把车送出去，旁边那台还在慢悠悠，你已经从容并线超过。那种“随叫随到”的底气，开过就回不去了。"),
        "wheel": ("底盘更稳", specs.get('底盘/悬架', '独立悬架'),
                  "深夜跑长途，一道道路面接缝从车底滑过，车里却只有孩子均匀的呼吸声。底盘把颠簸都替你咽了下去，家人一觉睡到目的地。"),
        "body": ("车身更护人", f"{specs.get('车身用钢', '高强度车身')}｜{specs.get('安全', '多气囊')}",
                 "高速上有车突然加塞，你本能一把方向——稳住车身的，是这身高强度钢和满车气囊。副驾的她、后排熟睡的孩子，甚至没察觉刚才那一惊。"),
        "roof": ("空间更能装", f"后备箱{specs.get('后备箱', '超大')}｜轴距{specs.get('轴距', '宽敞')}",
                 "周五一下班，后备箱塞进帐篷、天幕、孩子的滑板车，一家人往山里开去。后视镜里城市越来越远，前面是一整个周末的自由。"),
        "cabin": ("座舱更聪明", f"{specs.get('智能座舱', '智能大屏')}｜{specs.get('质保', '长质保')}",
                  "上车一句话——“导航去公司、空调26度、来点音乐”，车全办妥了。你双手握着方向盘专心开，副驾和后排聊着天，这一路你只管享受。"),
    }
    out = []
    for p in HOTSPOT_PARTS:
        title, data, benefit = text[p["key"]]
        out.append({"part": p["key"], "title": title, "data": data, "benefit": benefit})
    return out
