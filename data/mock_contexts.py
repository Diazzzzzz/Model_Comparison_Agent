"""现场对话上下文（数据层 · 可替换模块）。

对应【输入3：工牌录音转文字自动获取上下文】。真实场景接 ASR + 工牌硬件。

⚠️ 纯净版：不含内置示例对话。接入时让 get_context(id) 返回 {title, transcript, tags} 结构即可，
   transcript 为"销售：… / 客户：…"的多行文本，parse_dialogue() 会拆成对话气泡。
"""

# ← 接入真实对话/ASR 后在此填充。演示数据见 demo/* 分支。
MOCK_CONTEXTS = {}


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
