"""演示模式(MOCK)下的输出生成。

没配 DeepSeek key 时用这里：直接拿真实车型参数，按规则拼出一份像样的对比，
让整个流程在【零 key】情况下也能完整跑通、可演示。
填了 key 后就走真模型（见 comparison.py），这里不再参与。
"""
from agent.prompts import HOTSPOT_PARTS

# 演示模式下，认为我方在这些维度占优（销售工具，突出本车优势）
_OUR_WIN_KEYS = {"参考月供", "后备箱", "安全", "车身用钢", "智能座舱", "质保", "轴距"}


def build_mock_result(customer, our_car, rival_car):
    our_specs = our_car["specs"]
    rival_specs = rival_car["specs"]

    dimensions = []
    for key, our_val in our_specs.items():
        rival_val = rival_specs.get(key, "—")
        winner = "ours" if key in _OUR_WIN_KEYS else "tie"
        dimensions.append({
            "name": key,
            "our_value": our_val,
            "rival_value": rival_val,
            "winner": winner,
            "comment": _mock_comment(key, customer),
        })

    care = customer.get("care_most", "").strip() or "性价比"
    worry = customer.get("worry", "").strip()
    talk = (
        f"{customer.get('name','您')}，我特别理解您最看重{care}。"
        f"就拿{our_car['name']}和{rival_car['name']}比：同样这个价位，我们月供更轻松、"
        f"空间和安全用料都实打实占优。"
    )
    if worry:
        talk += f"您担心的『{worry}』，其实正是我们的强项——" \
                f"{our_car['name']}给的是{our_specs.get('质保','长质保')}，用料上{our_specs.get('车身用钢','高强度车身')}，这些都是白纸黑字写进合同的。"
    talk += "我建议您今天就试驾感受一下，很多客户一开就有数了。"

    # 演示：加一条我方劣势项，展示"找补"能力——销售既要知道弱点，也要知道怎么化解
    dimensions.append({
        "name": "品牌 / 保值率",
        "our_value": "国产品牌，保值率近年快速提升",
        "rival_value": f"{rival_car['brand']}合资品牌，二手保值率偏高",
        "winner": "rival",
        "comment": (
            f"【找补】客户就担心这个（{worry or '保值/品牌'}）。这么说："
            f"合资保值确实略高，但这两年差距明显在缩小；而且我们省下的差价 + 更长质保，"
            f"几年下来实际持有成本更低，真不吃亏。"
        ),
    })

    hotspots = _mock_hotspots(our_car)

    return {
        "summary": f"同价位更懂{care}的那台",
        "dimensions": dimensions,
        "talk_track": talk,
        "h5": {
            "scene_title": f"为{care}而来 · {our_car['name']}",
            "scene_prompt": _scene_prompt(our_car),
            "hotspots": hotspots,
        },
    }


def _scene_prompt(our_car):
    """按车型给一个具体、出片的场景（越野车走户外硬核，家用车走风景公路）。"""
    level = our_car.get("level", "")
    if "越野" in level:
        return ("a rugged off-road gravel mountain trail at golden hour, "
                "dramatic cliffs and pine forest, adventurous outdoor mood")
    return ("an open scenic coastal highway winding through green mountains at sunset, "
            "warm cinematic light, clean empty road")


def _mock_comment(key, customer):
    m = {
        "参考月供": "月供更低，每月少还几百，压力小一圈",
        "后备箱": "后排放倒能塞下婴儿车/露营装备，出行不用取舍",
        "安全": "全系标配，带娃出行这一条最实在",
        "车身用钢": "关键部位用料足，碰撞时更护人",
        "智能座舱": "大屏好用，导航语音一句话搞定",
        "质保": "质保更长，后期省心又省钱",
        "轴距": "轴距更长，后排腿部空间更宽敞",
        "动力": "动力够用，超车并线更从容",
        "指导价": "价格更亲民，同样的钱配置更高",
        "底盘/悬架": "底盘扎实，长途和烂路都更稳",
    }
    return m.get(key, "这一项对您的用车场景更合适")


def _mock_hotspots(our_car):
    specs = our_car["specs"]
    # 每项：(标题, 数据, 人话解读)
    text = {
        "front": ("动力更从容", specs.get('动力', '强劲动力'),
                  "市区超车、上坡满载都不费劲，开着不憋屈。"),
        "wheel": ("底盘更稳", specs.get('底盘/悬架', '独立悬架'),
                  "过烂路、跑长途都更稳更舒服，家人坐着不颠。"),
        "body": ("车身更护人", f"{specs.get('车身用钢', '高强度车身')}｜{specs.get('安全', '多气囊')}",
                 "真撞上了车身不容易变形，护住一家人。"),
        "roof": ("空间更能装", f"后备箱{specs.get('后备箱', '超大')}｜轴距{specs.get('轴距', '宽敞')}",
                 "婴儿车、露营装备随便塞，出行不用取舍。"),
        "cabin": ("座舱更聪明", f"{specs.get('智能座舱', '智能大屏')}｜{specs.get('质保', '长质保')}",
                  "大屏语音一句话搞定，还有长质保兜底，用着省心。"),
    }
    out = []
    for p in HOTSPOT_PARTS:
        title, data, benefit = text[p["key"]]
        out.append({"part": p["key"], "title": title, "data": data, "benefit": benefit})
    return out
