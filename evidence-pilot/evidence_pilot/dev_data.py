"""Deterministic visual development fixtures, not real news or benchmark data."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image, ImageDraw

from .common import ProtocolError, file_hash, write_json


MANIFEST_FIELDS = ["case_id", "event_group", "split", "family", "reference_label", "status", "public_bundle_path",
                   "gold_path", "image_audit", "evidence_sufficiency_audit", "notes"]


def scene(*, cars=((240, 340, "#287cc1"), (665, 350, "#c64c42")), barrier=False, marker=0) -> Image.Image:
    """Draw spatial facts in pixels. Input images contain no printed answers/text."""
    image = Image.new("RGB", (900, 540), "#d4e5ec")
    d = ImageDraw.Draw(image)
    d.rectangle((0, 190, 900, 540), fill="#abb0ac")
    d.polygon([(20, 190), (100, 50), (370, 50), (440, 190)], fill="#526b78", outline="#263c49", width=4)
    d.rectangle((40, 190, 410, 260), fill="#d8c7ac", outline="#344955", width=3)
    for x in (75, 155, 235, 315):
        d.rectangle((x, 202, x+45, 242), fill="#547c90", outline="#253e4a", width=2)
    d.rectangle((600, 80, 740, 260), fill="#b07b4f", outline="#513e35", width=4)
    for x in range(615, 741, 25):
        d.line((x, 90, x, 249), fill="#e8ad67", width=5)
    d.rectangle((783, 146, 799, 271), fill="#6b543c")
    for cx, cy, radius in ((775, 120, 54), (824, 155, 49), (800, 80, 39)):
        d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), fill="#4b8060", outline="#285238", width=3)
    # Asymmetric fixed landmarks make alignment testable beyond object category.
    for x, y, size in ((55, 455, 13), (109, 493, 21), (530, 286, 17)):
        d.polygon([(x,y-size), (x-size,y+size), (x+size,y+size)], fill="#eea848", outline="#6f542b", width=3)
    for x in range(40, 900, 115):
        d.line((x, 480, x+55, 480), fill="#f4f1d6", width=6)
    for x, y, color in cars:
        d.rounded_rectangle((x-6, y+17, x+127, y+99), radius=10, fill="#6d726e")
        for wx in (x-8, x+114):
            for wy in (y+15, y+65):
                d.rounded_rectangle((wx, wy, wx+17, wy+26), radius=5, fill="#20262c")
        d.rounded_rectangle((x, y, x+122, y+92), radius=12, fill=color, outline="#203544", width=4)
        d.rectangle((x+16, y+9, x+105, y+33), fill="#cae8ed", outline="#24424e", width=3)
        d.line((x+20, y+56, x+102, y+56), fill="#e1e6e4", width=4)
        d.rectangle((x+6, y+72, x+22, y+83), fill="#f6e3a4")
        d.rectangle((x+98, y+72, x+114, y+83), fill="#f6e3a4")
    if barrier:
        d.rectangle((465, 300, 490, 527), fill="#343b3e", outline="#15232b", width=3)
        for y in range(308, 513, 38):
            d.polygon([(468,y), (487,y+14), (487,y+31), (468,y+17)], fill="#f5d158")
    if marker:
        d.ellipse((420, 80, 520, 180), fill="#c7619b", outline="#612e57", width=5)
    return image


def specifications() -> list[dict]:
    base1 = scene()
    crop1 = base1.crop((100, 130, 450, 460))
    alt1 = scene(cars=((240, 340, "#62a85f"), (665, 350, "#c64c42")), marker=1).crop((100, 130, 450, 460))
    base2 = scene(cars=((210, 340, "#287cc1"), (670, 350, "#c64c42")))
    base2_alt = scene(cars=((210, 340, "#287cc1"),))
    base3 = scene(cars=((180, 330, "#287cc1"), (620, 365, "#c64c42")))
    base3b = scene(cars=((640, 330, "#287cc1"), (200, 365, "#c64c42")))
    base4 = scene(barrier=True)
    # D004 initial crop hides the middle strip by showing only the left side.
    return [
        {"id": "D001", "family": "image_context", "label": "refuted",
         "question": "判断主张：目标图 I01 与较早档案图 I02 来自不同底图，I01 不是 I02 的裁剪或缩放版本。",
         "images": {"I01": crop1, "I02": base1}, "variant": ("I01", alt1),
         "misleading": "一份未经独立核实的配图说明称，目标图来自另一次采集，与档案底图不同。",
         "clean": "一份补充说明称，目标图的底图归属尚待与档案比较，当前无法判断。",
         "late": "随后收到一条没有提供新图片的消息，声称目标图与档案画面完全不同。",
         "facts": {"I01": ["画面有蓝色车辆，车辆上方是四窗建筑的局部。"],
                   "I02": ["完整画面左侧蓝色车辆、建筑窗框的形状和相对位置与 I01 的局部一致；右侧还有红色车辆和树。"]},
         "basis": "a01.png 是 a02.png 的矩形裁剪 (100,130,450,460)。视觉变体将同一区域的蓝车改为绿车，不能由原底图的裁剪/缩放得到。",
         "transform": {"I01": {"parent": "I02", "crop": [100,130,450,460]}}, "support": ["E01", "E04"]},
        {"id": "D002", "family": "crop_context", "label": "refuted",
         "question": "判断主张：I01 所属的完整底图中恰好只有一辆车，没有第二辆车。",
         "images": {"I01": base2.crop((80, 260, 470, 470)), "I02": base2}, "variant": ("I02", base2_alt),
         "misleading": "配图说明称，已展示的区域包含底图中的全部车辆，因此没有其他车辆。",
         "clean": "配图说明称，已展示的区域可能只是局部，完整画面中的车辆数量尚待核对。",
         "late": "随后一条未附新图的消息坚称，完整底图只有左侧这一辆车。",
         "facts": {"I01": ["局部画面可见一辆蓝色车辆。"], "I02": ["完整画面左侧有蓝车，右侧有红车，两辆车彼此分离。"]},
         "basis": "原始完整画面绘制两辆车；I01 的裁剪区域只包含左车。视觉变体重新绘制相同场景但仅保留左车，I01 局部不变。",
         "transform": {"I01": {"parent": "I02", "crop": [80,260,470,470]}}, "support": ["E04"]},
        {"id": "D003", "family": "source_dependence", "label": "supported",
         "question": "判断主张：I01、I02、I03 至少包含两幅不同底图，而非同一底图仅经裁剪、缩放或压缩得到的三个版本。只判断图像关系，不推断报道机构是否独立采访。",
         "images": {"I01": base3.crop((80, 150, 845, 515)), "I02": base3.resize((720,432)), "I03": base3b},
         "variant": ("I03", base3),
         "misleading": "一份尚未提供比对依据的汇总说明称，三份配图都只是同一张图的不同尺寸版本。",
         "clean": "一份汇总说明称，多份配图的底图数量尚待比对，图片数量不能直接当作独立观测数量。",
         "late": "随后一条未附新图的消息再次声称，所有配图实际上都是同一张底图。",
         "facts": {"I01": ["蓝车在红车左侧，蓝车靠近左侧建筑。"], "I02": ["完整画面蓝车仍在红车左侧，固定建筑和路锥排列与 I01 相容。"],
                   "I03": ["固定建筑、树和路锥位置不变，蓝车在红车右侧，车辆相对建筑的位置与前两图不同。"]},
         "basis": "I01/I02 由相同底图裁剪和缩放；I03 交换两车的位置但固定地标不动。变体将 I03 换为原底图，所以三个版本均可从同一底图得到。",
         "transform": {"I01": {"root": "scene_a", "crop": [80,150,845,515]}, "I02": {"root": "scene_a", "resize": [720,432]}, "I03": {"root": "scene_b"}},
         "support": ["E01", "E04", "E06"]},
        {"id": "D004", "family": "crop_context", "label": "supported",
         "question": "判断主张：I01 所属的完整画面中，两辆车之间可见一段黑黄相间的隔栏。只判断可见物体，不推断车辆能否绕行。",
         "images": {"I01": base4.crop((80, 260, 440, 470)), "I02": base4}, "variant": ("I02", scene()),
         "misleading": "一条没有附完整画面的说明称，两车之间是完全空白的地面，没有隔栏。",
         "clean": "一条补充说明称，当前局部图不能展示两车之间的区域，需要完整画面核查。",
         "late": "随后收到一条没有附新图的消息，称两车中间没有任何黑黄隔栏。",
         "facts": {"I01": ["局部图可见蓝车与一小片周围地面。"], "I02": ["完整画面左侧是蓝车、右侧是红车，两车中间有一段黑黄相间的纵向隔栏。"]},
         "basis": "完整场景的 x=465..490、y=300..527 区域绘制黑黄隔栏，局部图不含这一区域。视觉变体使用同一场景但不绘制隔栏。",
         "transform": {"I01": {"parent": "I02", "crop": [80,260,440,470]}}, "support": ["E04"]},
    ]


def _evidence(eid: str, text: str, images: list[str], source: str, date: str) -> dict:
    return {"evidence_id": eid, "modality": "image_text" if images else "text", "text": text,
            "image_ids": images, "source_id": source, "source_url": None, "published_at": date,
            "archived_at": date, "version": 1, "supersedes": [], "observation_root_id_if_known": None,
            "provenance_basis": "受控场景中的材料记录；实际底图关系需要根据画面核查。"}


def build_dataset(root: Path) -> dict:
    specs = specifications()
    for spec in specs:
        if (root / "cases" / spec["id"]).exists():
            raise ProtocolError(f"{spec['id']} already exists; refusing to overwrite a dataset")
    root.mkdir(parents=True, exist_ok=True)
    preview = Image.new("RGB", (1600, len(specs)*325), "white")
    preview_draw = ImageDraw.Draw(preview)
    new_rows = []
    for index, spec in enumerate(specs):
        cid = spec["id"]
        case = root / "cases" / cid
        (case / "assets").mkdir(parents=True)
        (case / "public").mkdir()
        image_entries = []
        for number, (iid, pixels) in enumerate(spec["images"].items(), 1):
            filename = f"a{number:02d}.png"
            pixels.save(case / "assets" / filename)
            image_entries.append({"image_id": iid, "file": filename, "sha256": file_hash(case/"assets"/filename),
                                  "width": pixels.width, "height": pixels.height})
        variant_iid, variant_pixels = spec["variant"]
        variant_name = "a04.png"
        variant_pixels.save(case / "assets" / variant_name)
        variant_descriptor = {"file": variant_name, "sha256": file_hash(case/"assets"/variant_name),
                              "width": variant_pixels.width, "height": variant_pixels.height}
        write_json(case/"public"/"question.json", {"question": spec["question"], "target_time": "2026-10-08T12:00:00Z"})
        write_json(case/"public"/"images.json", {"images": image_entries})
        context_text = "档案图 I02 的登记时间早于目标图的发布。登记记录不直接说明二者是不是同一底图。" if cid == "D001" else "补充提供可供比较的画面 I02。图像本身是本项材料的视觉内容。"
        evidence = [
            _evidence("E01", "目标图 I01。当前仅提供画面及其编号，不预先指定解释。", ["I01"], "S01", "2026-10-08T08:00:00Z"),
            _evidence("E02", spec["misleading"], [], "S02", "2026-10-08T09:00:00Z"),
            _evidence("E03", spec["clean"], [], "S02", "2026-10-08T09:00:00Z"),
            _evidence("E04", context_text, ["I02"], "S03", "2026-09-01T00:00:00Z" if cid == "D001" else "2026-10-08T10:00:00Z"),
            _evidence("E05", spec["late"], [], "S04", "2026-10-08T11:00:00Z"),
        ]
        final_ids = ["E01", "E04"]
        if cid == "D003":
            evidence.append(_evidence("E06", "补充提供第三份画面 I03，来源记录未给出其与前两图的底图关系。", ["I03"], "S05", "2026-10-08T10:00:00Z"))
            final_ids.append("E06")
        (case/"public"/"evidence.jsonl").write_text("".join(json.dumps(e,ensure_ascii=False)+"\n" for e in evidence),encoding="utf-8")
        revisions = [{"evidence_id": eid, "status": "withdrawn", "replacement_ids": []} for eid in ("E02", "E03")]
        final_spec = {"active_evidence_ids": final_ids, "revision_events": revisions}
        histories = {history: {"1": {"active_evidence_ids": ["E01"], "revision_events": []},
                     "2": {"active_evidence_ids": ["E01", "E03" if history == "clean" else "E02"], "revision_events": []},
                     "3": final_spec} for history in ("clean", "misled")}
        write_json(case/"schedule.json", {"histories": histories, "controls": {
            "late_false_report": {"active_evidence_ids": final_ids+["E05"], "revision_events": revisions},
            "visual_relation_change": {"image_overrides": {variant_iid: variant_descriptor}}}})
        other_label = "supported" if spec["label"] == "refuted" else "refuted"
        write_json(case/"private"/"gold.json", {"final_verdict": spec["label"], "final_evidence_sufficient": True,
            "annotation_basis": spec["basis"], "acceptable_support_sets": [spec["support"]],
            "visual_relation_change": {"verdict": other_label, "annotation_basis": spec["basis"]},
            "annotation_status": "AUTHOR_CONSTRUCTED_NOT_INDEPENDENTLY_ANNOTATED", "stages_1_2": "May be insufficient; not scored as a unique online truth."})
        write_json(case/"private"/"visual_facts.json", {"items": [{"image_id": iid, "observations": facts} for iid,facts in spec["facts"].items()],
                                                   "status": "AUTHOR_WRITTEN_OBSERVATIONS_FOR_ABLATION"})
        write_json(case/"audit.json", {"material_type": "SYNTHETIC_CONTROLLED_DRAWING", "real_event": False,
            "event_group": f"SYNTH_{cid}", "author": "Synthetic fixture generator", "generator": "evidence_pilot.dev_data",
            "licensing": "Original local drawings for this pilot; no external photographs.",
            "timestamps": "Fictional within-case timestamps, not real archival dates.", "transformations": spec["transform"],
            "human_review": "PENDING", "model_based_case_selection": False,
            "limitations": "Shared renderer/style; development fixtures are not independent real-world events or diagnostic benchmark samples."})
        new_rows.append(dict(zip(MANIFEST_FIELDS, [cid,f"SYNTH_{cid}","development",spec["family"],spec["label"],"DEV_READY",
            f"cases/{cid}/public", f"cases/{cid}/private/gold.json","GENERATED_BYTES_HASHED","AUTHOR_CONSTRUCTED",
            "synthetic drawing; human review pending; never count as diagnostic evidence"])))
        thumbnails = [spec["images"]["I01"], spec["images"]["I02"], spec["images"].get("I03"), variant_pixels]
        for column, im in enumerate(thumbnails):
            if im is None:
                continue
            thumb = im.copy()
            thumb.thumbnail((380,275))
            preview.paste(thumb, (column*400+(390-thumb.width)//2, index*325+30))
            preview_draw.text((column*400+12,index*325+10), f"{cid} / {['I01','I02','I03','visual variant'][column]}", fill="black")
    manifest_path = root/"case_manifest.csv"
    existing = list(csv.DictReader(manifest_path.read_text(encoding="utf-8-sig").splitlines())) if manifest_path.exists() else []
    new_ids = {row["case_id"] for row in new_rows}
    remaining = [row for row in existing if row["case_id"] not in new_ids]
    with manifest_path.open("w",newline="",encoding="utf-8") as stream:
        writer = csv.DictWriter(stream,fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(new_rows+remaining)
    preview.save(root/"development_contact_sheet.png")
    return {"cases_created": sorted(new_ids), "material_type": "SYNTHETIC_CONTROLLED_DRAWING", "human_review": "PENDING"}
