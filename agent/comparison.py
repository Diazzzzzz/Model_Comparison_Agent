"""核心：把 客户 + 我方车 + 竞品车 → 对比表 / 话术 / H5 三件套。

流程：
  1. 按这个客户挑选对比维度（data/dimensions.py），参数值直接锁定为车库里的值。
  2. 有 DeepSeek key  → 真调模型；模型只判断 winner + 写 comment/话术，【不许改数字】。
     没 key / 强制mock → 用 mock_data 按锁定的维度拼样例。
  3. 事后对话术做防幻觉软校验（数字必须在源参数/客户信息里出现过）。
两条路返回的结构完全一样，上层不用关心走了哪条。
"""
import json
import re
from config import Config
from data import car_library
from data.dimensions import select_dimensions
from agent import llm_client, image_client, mock_data
from agent.prompts import SYSTEM_PROMPT, build_user_prompt, HOTSPOT_PARTS

_NUM = re.compile(r"\d+(?:\.\d+)?")


def generate_comparison(customer: dict, our_car_name: str, rival_car_name: str) -> dict:
    our_car = car_library.get_car(our_car_name)
    rival_car = car_library.get_car(rival_car_name)
    if not our_car or not rival_car:
        raise ValueError("车型没找到，请检查车型名")

    # 维度按这个客户挑；每条维度的参数值直接取自车库（事实，锁定，不由模型编）
    dims = select_dimensions(customer, our_car, rival_car)

    if Config.text_mock():
        result = mock_data.build_mock_result(customer, our_car, rival_car, dims)
        result["_mode"] = "演示模式(未配 DeepSeek key)"
    else:
        prompt_dims = [{"name": d["label"], "our_value": d["our_value"],
                        "rival_value": d["rival_value"]} for d in dims]
        model = llm_client.chat_json(
            SYSTEM_PROMPT, build_user_prompt(customer, our_car, rival_car, prompt_dims)
        )
        result = _merge_model(model, dims)   # 数字锁：表格值用车库的，模型只给 winner+comment
        result["_mode"] = f"DeepSeek 生成({Config.DEEPSEEK_MODEL})"

    result = _normalize(result)
    result = _verify_numbers(result, our_car, rival_car, customer)

    # H5 场景背景图（有火山 key 才真生成，否则 None → 前端用渐变兜底）
    img = image_client.generate_scene(result["h5"].get("scene_prompt", ""))
    result["h5"]["scene_image_url"] = img["url"]
    result["h5"]["image_status"] = img  # {url, status, detail}，用于界面显示火山成没成功
    result["our_car"] = our_car
    result["rival_car"] = rival_car
    result["customer"] = customer
    return result


def _merge_model(model: dict, dims: list) -> dict:
    """把模型产出的 winner/comment 合并回"车库锁定的参数值"。
    模型不允许改数字——our_value/rival_value 只来自 dims（车库）。"""
    calls = {c.get("name"): c for c in model.get("dimension_calls", []) if isinstance(c, dict)}
    out = []
    for d in dims:
        c = calls.get(d["label"], {})
        w = c.get("winner", "tie")
        out.append({
            "name": d["label"],
            "our_value": d["our_value"],
            "rival_value": d["rival_value"],
            "winner": w if w in ("ours", "rival", "tie") else "tie",
            "comment": c.get("comment", ""),
        })
    return {
        "summary": model.get("summary", ""),
        "dimensions": out,
        "talk_track": model.get("talk_track", ""),
        "h5": model.get("h5", {}),
    }


def _verify_numbers(result: dict, our_car: dict, rival_car: dict, customer: dict) -> dict:
    """防幻觉软校验：话术里出现的数字，必须能在"车库参数 + 客户信息"里找到，
    否则标 _warn 提示人工核对（只提示、不拦截；宁可误报也别放过杜撰的参数）。"""
    allowed = set()
    for src in (our_car.get("specs", {}), rival_car.get("specs", {}), customer):
        allowed |= set(_NUM.findall(json.dumps(src, ensure_ascii=False)))
    talk = result.get("talk_track", "") or ""
    bad = [n for n in _NUM.findall(talk) if n not in allowed]
    if bad:
        uniq = "、".join(dict.fromkeys(bad))
        result["_warn"] = f"话术中出现源参数/客户信息里没有的数字：{uniq}，请人工核对是否杜撰"
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
    from agent.prompts import EXTRACT_TAGS_SYSTEM
    if Config.text_mock():
        return {
            "name": "（演示）从对话提炼的客户",
            "intent_car": "本田CR-V",
            "budget": "20万内，月供4000内",
            "usage": "通勤+带娃出游",
            "family": "三口之家，2岁小孩",
            "care_most": "空间、安全、保值",
            "worry": "油耗、保值不如丰田",
            "heat": "高",
            "rival_car": "丰田RAV4荣放",
        }
    return llm_client.chat_json(EXTRACT_TAGS_SYSTEM, transcript)
