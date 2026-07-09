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
针对一位具体的购车客户，做一份“扬长避短、正向引导”的车型对比。

原则：
1. 【只包装事实，不制造事实】对比表每条维度的参数值都已由系统给定并锁定，你不得改动、
   不得新增任何数字或参数。你只负责判断每条维度谁占优，并把参数“翻译成对这位客户的好处”。
2. 紧扣这位客户【最在意的点】和【顾虑】说话。
3. 语言口语、接地气，一线销售照着就能对客户说。
4. 【合规】禁止使用“最”“第一”“绝对”“No.1”等绝对化 / 最高级用语；不得虚构或贬损竞品，
   只做客观占优判断。凡是给定信息里没有的内容，一律写“暂无数据”，绝不猜测或编造。
必须严格返回 JSON，不要任何多余文字。"""


def build_user_prompt(customer: dict, our_car: dict, rival_car: dict, dimensions: list) -> str:
    """dimensions: 系统已挑好并锁定参数值的维度列表 [{name, our_value, rival_value}]。
    模型只判断 winner + 写 comment，不允许改动数值。"""
    parts_desc = "、".join(f'{p["key"]}({p["label"]})' for p in HOTSPOT_PARTS)
    schema = {
        "summary": "一句话总结：为什么这位客户该选我方车（20字内，不用绝对化词）",
        "dimension_calls": [
            {"name": "维度名（必须与【给定维度】里的 name 一模一样）",
             "winner": "ours / rival / tie 三选一",
             "comment": "一句话点评：把参数翻译成对这位客户的好处；若 winner=rival，写成给销售的『找补话术』"}
        ],
        "talk_track": ("话术，严格 4 拍：①共情他最在意的点 → ②点出我方关键差异（引用给定参数）"
                       "→ ③正面化解他的顾虑 → ④促成下一步试驾。口语、接地气，80~120 字，"
                       "数字只能引用给定参数。"),
        "h5": {
            "scene_title": "H5 场景标题（如：带娃出游的安全之选）",
            "scene_prompt": "一句英文的图像生成提示词，描述适合这台车的户外场景背景，不要出现车",
            "hotspots": [
                {"part": f"上面5个part之一({parts_desc})",
                 "title": "5-8字短标题",
                 "data": "该部件关键参数（只能用【给定维度】或【我方车型】里已有的数字，没有就留空，不要编）",
                 "benefit": ("给客户造梦的场景化文案：用有画面感的语言，描绘他拥有这台车后一个具体、"
                             "打动人的生活瞬间（结合他的家庭/用途/在意的点），2-3句，有代入感，"
                             "让他仿佛‘看见’那个画面。别干讲参数、别喊口号。")}
            ],
        },
    }
    return (
        "【客户画像】\n" + json.dumps(customer, ensure_ascii=False, indent=2) +
        "\n\n【我方车型】\n" + json.dumps(our_car, ensure_ascii=False, indent=2) +
        "\n\n【竞品车型】\n" + json.dumps(rival_car, ensure_ascii=False, indent=2) +
        "\n\n【给定维度（参数值已锁定，禁止改动数值，只判断 winner 并写 comment）】\n" +
        json.dumps(dimensions, ensure_ascii=False, indent=2) +
        "\n\n要求：\n"
        "1. 对每条给定维度都产出一个 dimension_calls 条目，name 必须与给定维度完全一致。\n"
        "2. 为了让销售可信、有准备，必须保留 1~2 条我方处于劣势的诚实项（winner=rival）。"
        "对每条 winner=rival 的项，comment 写成给销售的『找补话术』：先承认差距，再化解"
        "（弱化影响 / 转移到我方强项 / 给客户一个不吃亏的理由），紧扣这位客户的顾虑。\n"
        "3. 所有数字只能来自给定维度 / 车型参数，不得新增或改动；给定里没有的信息写“暂无数据”，不要编造。\n"
        "4. 禁止使用“最”“第一”“绝对”“No.1”等绝对化用语。\n"
        "5. h5.hotspots 必须给满 5 个，每个 part 用且仅用一次，顺序对应：" + parts_desc +
        "。\n严格按以下 JSON 结构返回（只返回 JSON）：\n" +
        json.dumps(schema, ensure_ascii=False, indent=2)
    )


EXTRACT_TAGS_SYSTEM = """你是销售助手。下面是一段销售和客户的现场对话。
请从中提炼客户画像，严格返回 JSON，字段：name(客户称呼), intent_car(意向车型),
budget(预算/月供), usage(主要用途), family(家庭结构), care_most(最在意的点),
worry(主要顾虑), heat(意向热度), rival_car(正在纠结的竞品)。
提炼不到的字段就填空字符串。只返回 JSON。"""
