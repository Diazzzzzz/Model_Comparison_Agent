"""核心：把 客户 + 我方车 + 竞品车 → 对比表 / 话术 / H5 三件套。

流程：
  有 DeepSeek key  → 真调模型
  没 key / 强制mock → 用 mock_data 按真实参数拼出样例
两条路返回的结构完全一样，上层不用关心走了哪条。
"""
from config import Config
from data import car_library
from agent import llm_client, image_client, mock_data
from agent.prompts import (
    SYSTEM_PROMPT, build_user_prompt, HOTSPOT_PARTS,
    EXTRACT_TAGS_SYSTEM,
)

_VALID_PARTS = {p["key"] for p in HOTSPOT_PARTS}


def generate_comparison(customer: dict, our_car_name: str, rival_car_name: str) -> dict:
    our_car = car_library.get_car(our_car_name)
    rival_car = car_library.get_car(rival_car_name)
    if not our_car or not rival_car:
        raise ValueError("车型没找到，请检查车型名")

    if Config.text_mock():
        result = mock_data.build_mock_result(customer, our_car, rival_car)
        result["_mode"] = "演示模式(未配 DeepSeek key)"
    else:
        result = llm_client.chat_json(
            SYSTEM_PROMPT, build_user_prompt(customer, our_car, rival_car)
        )
        result["_mode"] = f"DeepSeek 生成({Config.DEEPSEEK_MODEL})"

    result = _normalize(result)
    # H5 场景背景图（有火山 key 才真生成，否则 None → 前端用渐变兜底）
    img = image_client.generate_scene(result["h5"].get("scene_prompt", ""))
    result["h5"]["scene_image_url"] = img["url"]
    result["h5"]["image_status"] = img  # {url, status, detail}，用于界面显示火山成没成功
    result["our_car"] = our_car
    result["rival_car"] = rival_car
    result["customer"] = customer
    return result


def _normalize(result: dict) -> dict:
    """补齐/清洗模型输出，保证前端拿到的结构稳定。"""
    result.setdefault("summary", "")
    result.setdefault("dimensions", [])
    result.setdefault("talk_track", "")
    h5 = result.setdefault("h5", {})
    h5.setdefault("scene_title", "")
    h5.setdefault("scene_prompt", "")

    # 把 hotspots 整理成"按固定 part 顺序、每个 part 一个"的字典
    raw = {h.get("part"): h for h in h5.get("hotspots", []) if isinstance(h, dict)}
    fixed = []
    for p in HOTSPOT_PARTS:
        h = raw.get(p["key"], {})
        fixed.append({
            "part": p["key"],
            "label": p["label"],
            "title": h.get("title") or p["label"],
            "data": h.get("data") or "",
            "benefit": h.get("benefit") or h.get("selling_point") or "点击了解这个部件的优势",
        })
    h5["hotspots"] = fixed
    return result


def extract_tags_from_context(transcript: str) -> dict:
    """从对话上下文提炼客户标签（对应输入3）。没 key 时给个演示结果。"""
    if Config.text_mock():
        return {
            "name": "（演示）从对话提炼的客户",
            "intent_car": "长城哈弗H6",
            "budget": "15万内，月供3000内",
            "usage": "通勤+带娃出游",
            "family": "三口之家，2岁小孩",
            "care_most": "安全、空间、性价比",
            "worry": "怕国产不保值、小毛病多",
            "heat": "高",
            "rival_car": "丰田RAV4荣放",
        }
    return llm_client.chat_json(EXTRACT_TAGS_SYSTEM, transcript)
