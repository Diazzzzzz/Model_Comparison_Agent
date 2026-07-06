"""模拟"对话上下文"（销售-客户的现场对话片段）。

对应需求里的【输入3：工牌录音转文字自动获取上下文】。
真实场景要接 ASR + 工牌硬件，MVP 先用这几段假对话顶替，
用来演示"从对话里自动提炼客户标签"这个能力的雏形。

每段对话自带 tags（演示模式下"提炼"的结果就用它，保证跟对话内容对得上）。
"""

MOCK_CONTEXTS = {
    "ctx1": {
        "title": "展厅对话·王先生（看H6，比RAV4）",
        "transcript": (
            "销售：王哥您好，之前看您对哈弗H6挺感兴趣的，今天再来看看？\n"
            "客户：对，就是有点纠结。我一个朋友让我看看丰田的RAV4，说合资的保值。\n"
            "销售：您平时主要什么场景用车呀？\n"
            "客户：上下班通勤为主，周末带我家小孩出去玩。孩子才两岁，安全我最看重。\n"
            "客户：空间也得够，推车、大包小包得装得下。\n"
            "销售：预算和月供方面您大概什么范围？\n"
            "客户：尽量控制在15万以内吧，月供别超过3000，压力大。\n"
            "客户：就是有点担心，国产车小毛病会不会多？以后是不是不好卖、掉价快？"
        ),
        "tags": {
            "name": "王先生",
            "intent_car": "长城哈弗H6",
            "budget": "15万内，月供3000内",
            "usage": "城市通勤 + 周末带娃出游",
            "family": "三口之家，2岁小孩",
            "care_most": "安全、空间",
            "worry": "怕国产车小毛病多、不保值",
            "heat": "高（在比价中）",
            "rival_car": "丰田RAV4荣放",
        },
    },
    "ctx2": {
        "title": "展厅对话·李女士（看坦克300，比途观L）",
        "transcript": (
            "销售：李姐您喜欢什么样的车型？\n"
            "客户：我就喜欢方方正正、硬派一点的，主要想周末去越野、露营。\n"
            "客户：坦克300我挺心动，但又在看大众途观L，纠结。\n"
            "销售：您比较在意哪些方面？\n"
            "客户：越野能力肯定要，外观要硬朗，后备箱能装露营装备。\n"
            "客户：就是担心坦克油耗是不是很高？平时在市区开好不好停车？\n"
            "销售：预算方面呢？\n"
            "客户：20万左右能接受。"
        ),
        "tags": {
            "name": "李女士",
            "intent_car": "长城坦克300",
            "budget": "20万左右",
            "usage": "周末越野、露营",
            "family": "夫妻二人，爱玩户外",
            "care_most": "越野能力、外观硬朗、装备空间",
            "worry": "油耗高不高、市区好不好停",
            "heat": "中（坦克300和途观L之间摇摆）",
            "rival_car": "大众途观L",
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
