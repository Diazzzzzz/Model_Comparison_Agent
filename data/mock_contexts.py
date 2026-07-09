"""模拟"对话上下文"（销售-客户的现场对话片段）。

对应需求里的【输入3：工牌录音转文字自动获取上下文】。
真实场景要接 ASR + 工牌硬件，MVP 先用这几段假对话顶替，
用来演示"从对话里自动提炼客户标签"这个能力的雏形。

每段对话自带 tags（演示模式下"提炼"的结果就用它，保证跟对话内容对得上）。
当前为【东风本田演示版】。
"""

MOCK_CONTEXTS = {
    "ctx1": {
        "title": "展厅对话·王先生（看CR-V，比RAV4）",
        "transcript": (
            "销售：王哥您好，之前看您对 CR-V 挺感兴趣的，今天再来看看？\n"
            "客户：对，就是有点纠结。朋友让我看看丰田 RAV4，说日系里丰田更保值。\n"
            "销售：您平时主要什么场景用车呀？\n"
            "客户：上下班通勤为主，周末带我家小孩出去玩。孩子才两岁，空间和安全我最看重。\n"
            "客户：后备箱得能装，推车、大包小包都得塞得下。\n"
            "销售：预算和月供方面您大概什么范围？\n"
            "客户：尽量控制在20万以内，月供别超过4000。\n"
            "客户：就是有点担心，CR-V 油耗高不高？保值是不是没丰田好？"
        ),
        "tags": {
            "name": "王先生",
            "intent_car": "本田CR-V",
            "budget": "20万内，月供4000内",
            "usage": "城市通勤 + 周末带娃出游",
            "family": "三口之家，2岁小孩",
            "care_most": "空间、安全",
            "worry": "油耗、保值不如丰田",
            "heat": "高（在比价中）",
            "rival_car": "丰田RAV4荣放",
        },
    },
    "ctx2": {
        "title": "展厅对话·陈先生（看思域，比卡罗拉）",
        "transcript": (
            "销售：陈先生您喜欢什么样的车？\n"
            "客户：我年轻人第一台车，想要开着有劲、外观运动一点的。\n"
            "客户：思域我挺心动，但家里人让我看卡罗拉，说省心保值，纠结。\n"
            "销售：您比较在意哪些方面？\n"
            "客户：动力和操控肯定要，外观得帅；主要自己上下班开，偶尔约朋友跑跑山。\n"
            "客户：就是担心思域后排空间够不够、油耗是不是比卡罗拉高？\n"
            "销售：预算方面呢？\n"
            "客户：15万左右能接受。"
        ),
        "tags": {
            "name": "陈先生",
            "intent_car": "本田思域",
            "budget": "15万左右",
            "usage": "通勤、偶尔跑山约朋友",
            "family": "单身，年轻首购",
            "care_most": "动力、操控、颜值",
            "worry": "后排空间、油耗比卡罗拉高",
            "heat": "中（思域和卡罗拉之间摇摆）",
            "rival_car": "丰田卡罗拉",
        },
    },
}


def list_contexts():
    return [{"id": k, "title": v["title"]} for k, v in MOCK_CONTEXTS.items()]


def get_context(cid: str):
    return MOCK_CONTEXTS.get(cid)


def parse_dialogue(transcript: str):
    """把 '销售：xxx' / '客户：xxx' 的文本拆成 [{who, text}]，供界面画成对话气泡。"""
    lines = []
    for raw in transcript.split("\n"):
        raw = raw.strip()
        if not raw:
            continue
        if "：" in raw:
            who, text = raw.split("：", 1)
        elif ":" in raw:
            who, text = raw.split(":", 1)
        else:
            who, text = "客户", raw
        lines.append({"who": who.strip(), "text": text.strip()})
    return lines
