"""演示模式(MOCK)下的输出生成。

没配 DeepSeek key 时用这里：直接拿【已挑好并锁定参数值的维度】拼出一份像样的对比，
让整个流程在零 key 情况下也能完整跑通、可演示。
填了 key 后就走真模型（见 comparison.py），这里不再参与。
"""
from agent.prompts import HOTSPOT_PARTS


def build_mock_result(customer, our_car, rival_car, dims):
    """dims: data/dimensions.select_dimensions() 挑好的维度，
    每条已带锁定的 our_value / rival_value / mock（默认结论）。"""
    our_specs = our_car["specs"]

    dimensions = []
    for d in dims:
        dimensions.append({
            "name": d["label"],
            "our_value": d["our_value"],
            "rival_value": d["rival_value"],
            "winner": d.get("mock", "tie"),
            "comment": _mock_comment(d["spec"], customer),
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

    # 演示：补一条我方劣势项，展示"找补"能力——销售既要知道弱点，也要知道怎么化解
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
        "指导价": "价格更亲民，同样的钱配置更高",
        "参考月供": "月供更低，每月少还几百，压力小一圈",
        "安全": "全系标配，带娃出行这一条最实在",
        "能耗油耗": "合资是省一点点，但差距很小；我们月供更低、保养更省，一年综合下来更划算，真不吃亏",
        "售后服务": "服务网络跟着市场同步建，坏了有人管、修得起，出海最怕的就是没人管",
        "保养成本": "保养便宜、周期长，跑得多也养得起",
        "后备箱": "后排放倒能塞下婴儿车/露营装备，出行不用取舍",
        "车身用钢": "关键部位用料足，碰撞时更护人",
        "智能座舱": "大屏好用，导航语音一句话搞定",
        "质保": "质保更长，后期省心又省钱",
        "轴距": "轴距更长，后排腿部空间更宽敞",
        "动力": "动力更足，超车并线更从容",
        "底盘/悬架": "底盘扎实，长途和烂路都更稳",
    }
    return m.get(key, "这一项对您的用车场景更合适")


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
                  "上车一句话——“导航去外婆家、空调26度、来点音乐”，车全办妥了。你双手握着方向盘专心开，副驾和后排聊着天，这一路你只管享受。"),
    }
    out = []
    for p in HOTSPOT_PARTS:
        title, data, benefit = text[p["key"]]
        out.append({"part": p["key"], "title": title, "data": data, "benefit": benefit})
    return out
