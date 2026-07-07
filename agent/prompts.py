"""提示词模板。集中放这里，方便调。"""
import json

# H5 上固定的 5 个可点击部件（车图和坐标是固定的，AI 只负责填每个部件讲什么）
HOTSPOT_PARTS = [
    {"key": "front", "label": "车头 / 动力"},
    {"key": "wheel", "label": "轮胎 / 底盘"},
    {"key": "body", "label": "车身 / 安全"},
    {"key": "roof", "label": "车顶 / 空间"},
    {"key": "cabin", "label": "座舱 / 智能"},
]

SYSTEM_PROMPT = """你是一名资深汽车销售顾问的 AI 助手。你的任务：站在【我方车型】的立场，
针对一位具体的购车客户，做一份"扬长避短、正向引导"的车型对比。
原则：
1. 只讲事实，但选择性地突出我方优势、弱化劣势——这是给销售用的说服工具，不是中立评测。
2. 紧扣这位客户【最在意的点】和【顾虑】说话，把参数翻译成对他的好处。
3. 语言口语、接地气，让一线销售照着就能对客户说。
必须严格返回 JSON，不要任何多余文字。"""


def build_user_prompt(customer: dict, our_car: dict, rival_car: dict) -> str:
    parts_desc = "、".join(f'{p["key"]}({p["label"]})' for p in HOTSPOT_PARTS)
    schema = {
        "summary": "一句话总结：为什么这位客户该选我方车（20字内）",
        "dimensions": [
            {
                "name": "对比维度名（如：安全）",
                "our_value": "我方该维度的具体参数/表现",
                "rival_value": "竞品该维度的具体参数/表现",
                "winner": "ours / rival / tie 三选一",
                "comment": "一句话点评，翻译成对这位客户的好处",
            }
        ],
        "talk_track": "一段话术：销售照着念，30秒内抓住客户，紧扣他最在意的点和顾虑",
        "h5": {
            "scene_title": "H5 场景标题（如：带娃出游的安全之选）",
            "scene_prompt": "一句英文的图像生成提示词，描述适合这台车的户外场景背景，不要出现车",
            "hotspots": [
                {"part": f"上面5个part之一({parts_desc})",
                 "title": "5-8字短标题",
                 "data": "该部件的关键参数/数据（短，带数字，如 '2.0T 204马力' '高强度钢78%'）",
                 "benefit": "人话解读：这个数据对购车人有啥实在方便/好处，1-2句，别堆术语"}
            ],
        },
    }
    return (
        "【客户画像】\n" + json.dumps(customer, ensure_ascii=False, indent=2) +
        "\n\n【我方车型】\n" + json.dumps(our_car, ensure_ascii=False, indent=2) +
        "\n\n【竞品车型】\n" + json.dumps(rival_car, ensure_ascii=False, indent=2) +
        "\n\n请给出对比。dimensions 至少覆盖 6 个维度，务必包含『月供/用车成本』和『安全』。"
        "为了让销售可信、有准备，dimensions 里必须包含 1~2 个我方处于劣势的诚实项（winner 设为 rival）。"
        "对每个 winner=rival 的项，comment 必须写成给销售的『找补话术』：先承认差距，再化解"
        "（弱化影响 / 转移到我方强项 / 给客户一个不吃亏的理由），紧扣这位客户的顾虑。"
        "h5.hotspots 必须给满 5 个，每个 part 用且仅用一次，顺序对应：" + parts_desc +
        "。\n严格按以下 JSON 结构返回（只返回 JSON）：\n" +
        json.dumps(schema, ensure_ascii=False, indent=2)
    )


EXTRACT_TAGS_SYSTEM = """你是销售助手。下面是一段销售和客户的现场对话。
请从中提炼客户画像，严格返回 JSON，字段：name(客户称呼), intent_car(意向车型),
budget(预算/月供), usage(主要用途), family(家庭结构), care_most(最在意的点),
worry(主要顾虑), heat(意向热度), rival_car(正在纠结的竞品)。
提炼不到的字段就填空字符串。只返回 JSON。"""
