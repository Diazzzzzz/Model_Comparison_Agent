"""车型对比 Agent · Web 入口（Flask）。

一键流程：销售填客户标签 + 选两款车 → 生成 ①对比表 ②话术 ③可点击客户H5。
运行：  pip install -r requirements.txt  &&  python app.py
然后浏览器打开 http://127.0.0.1:5000
"""
import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, abort

from config import Config
from data import car_library, customer_tags, mock_contexts, car_assets
from agent import comparison, bg_remove
from agent.prompts import HOTSPOT_PARTS

app = Flask(__name__)

CARS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "cars")

# MVP：结果先存内存（重启即清空）。将来接数据库只改这里。
RESULTS = {}


def _match_car(name, cars):
    """把（可能不精确的）车名匹配到车库里的正式名。匹配不到返回原值。
    与品牌无关：去品牌词时用每辆车自己的 brand 字段，不写死任何品牌。"""
    name = (name or "").strip()
    names = [c["name"] for c in cars]
    if name in names:
        return name
    for n in names:                       # 互相包含：核心型号名 ↔ 含品牌全名
        if n and (n in name or name in n):
            return n
    for c in cars:                        # 去掉该车自己的品牌词，再按核心型号名比
        core = c["name"].replace(c.get("brand", ""), "").strip()
        if core and (core in name or name in core):
            return c["name"]
    return name


@app.route("/")
def index():
    # 支持两种预填：加载示例客户 / 从对话上下文提取
    customer = customer_tags.blank_customer()
    note = ""
    dialogue = None  # 现场对话气泡（选了对话上下文时展示）
    cid = request.args.get("customer_id")
    ctx_id = request.args.get("ctx_id")
    if cid:
        preset = customer_tags.get_customer(cid)
        if preset:
            customer = preset
            note = f"已载入示例客户：{preset['name']}（含意向车型/竞品）"
    elif ctx_id:
        ctx = mock_contexts.get_context(ctx_id)
        if ctx:
            # 演示模式直接用对话自带的标签（跟对话内容对得上）；有 key 时才真调模型提炼
            if Config.text_mock():
                customer = ctx.get("tags") or customer
            else:
                customer = comparison.extract_tags_from_context(ctx["transcript"])
            dialogue = mock_contexts.parse_dialogue(ctx["transcript"])
            note = f"已从对话《{ctx['title']}》自动提炼客户标签，可再手动修改"

    # 把车名规范化到车库正式名（模型可能抽出简称，下拉框是含品牌的全名）
    customer = dict(customer)
    customer["intent_car"] = _match_car(customer.get("intent_car"), car_library.our_cars())
    customer["rival_car"] = _match_car(customer.get("rival_car"), car_library.rival_cars())

    return render_template(
        "index.html",
        schema=customer_tags.TAG_SCHEMA,
        customer=customer,
        dialogue=dialogue,
        preset_customers=customer_tags.list_customers(),
        contexts=mock_contexts.list_contexts(),
        our_cars=car_library.our_cars(),
        rival_cars=car_library.rival_cars(),
        note=note,
        mock_mode=Config.text_mock(),
    )


@app.route("/generate", methods=["POST"])
def generate():
    customer = {item["key"]: request.form.get(item["key"], "").strip()
                for item in customer_tags.TAG_SCHEMA}
    # 选车用独立字段名 sel_our / sel_rival，避免与客户标签里的 rival_car 文本框重名
    our_car = request.form.get("sel_our", "")
    rival_car = request.form.get("sel_rival", "")
    if not car_library.get_car(our_car) or not car_library.get_car(rival_car):
        abort(400, "请从下拉框里选择有效的车型（我方 + 竞品）")
    if our_car == rival_car:
        abort(400, "我方车型和竞品不能是同一款")
    result = comparison.generate_comparison(customer, our_car, rival_car)
    rid = uuid.uuid4().hex[:8]
    RESULTS[rid] = result
    return redirect(url_for("result", rid=rid))


@app.route("/result/<rid>")
def result(rid):
    data = RESULTS.get(rid)
    if not data:
        abort(404)
    return render_template("result.html", r=data, rid=rid)


@app.route("/h5/<rid>")
def h5(rid):
    """客户侧可点击 H5（销售把这个链接/二维码发给客户）。"""
    data = RESULTS.get(rid)
    if not data:
        abort(404)
    # 若这辆车在管理页标注过真图+热区，就用它；否则 H5 回退到通用剪影
    asset = car_assets.get_asset(data["our_car"]["name"])
    return render_template("h5.html", r=data, rid=rid, asset=asset)


# ======== 内部管理页：车图 + 热区标注（非销售页，将来迁入后台系统）========

@app.route("/admin")
def admin():
    return render_template(
        "admin.html",
        cars=car_library.list_cars(),
        parts=HOTSPOT_PARTS,
        assets=car_assets.all_assets(),
    )


MAX_COLORS = 64  # 动态行数上限（扫描区间），实际有多少填多少


def _save_bytes(raw, ext=".png"):
    """把图片字节存到 static/cars，返回可访问路径。"""
    os.makedirs(CARS_DIR, exist_ok=True)
    fname = f"car_{uuid.uuid4().hex[:12]}{ext}"
    with open(os.path.join(CARS_DIR, fname), "wb") as fp:
        fp.write(raw)
    return f"/static/cars/{fname}"




def _save_upload(file, cutout=True):
    """保存上传图片，返回可访问路径。cutout=True 先自动去背景。"""
    ext = os.path.splitext(file.filename)[1].lower() or ".png"
    if ext not in (".png", ".jpg", ".jpeg", ".webp"):
        abort(400, "图片格式仅支持 png/jpg/webp")
    raw = file.read()
    if cutout:
        raw, ok = bg_remove.remove_bg(raw)
        if ok:
            ext = ".png"
    return _save_bytes(raw, ext)


@app.route("/admin/cutout", methods=["POST"])
def admin_cutout():
    """选图时即时抠图：收一张图 → 抠图存好 → 返回可访问路径。"""
    f = request.files.get("image")
    if not f or not f.filename:
        abort(400, "没有图片")
    cutout = request.form.get("cutout", "on") == "on"
    return {"path": _save_upload(f, cutout)}






@app.route("/admin/save", methods=["POST"])
def admin_save():
    car = request.form.get("car", "").strip()
    if not car_library.get_car(car):
        abort(400, "请选择有效车型")
    try:
        hotspots = json.loads(request.form.get("hotspots", "{}"))
    except json.JSONDecodeError:
        abort(400, "热区坐标格式错误")

    cutout = request.form.get("cutout") == "on"  # 是否自动抠图

    # 行数是动态的（可加可减），扫一段较大的区间，跳过空行
    colors = []
    for i in range(MAX_COLORS):
        name = request.form.get(f"color_name_{i}", "").strip()
        hexv = request.form.get(f"color_hex_{i}", "").strip() or "#cccccc"
        hex2 = request.form.get(f"color_hex2_{i}", "").strip()  # 拼色第二色，可空
        keep = request.form.get(f"color_keep_{i}", "").strip()
        f = request.files.get(f"color_img_{i}")
        image = _save_upload(f, cutout) if (f and f.filename) else keep
        if name and image:
            entry = {"name": name, "hex": hexv, "image": image}
            if hex2:
                entry["hex2"] = hex2
            colors.append(entry)

    if not colors:
        abort(400, "至少要有一个颜色（填颜色名 + 传一张图）")

    car_assets.save_asset(car, colors, hotspots)
    return redirect(url_for("admin", saved=car))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
