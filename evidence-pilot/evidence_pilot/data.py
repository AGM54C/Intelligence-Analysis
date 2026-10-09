from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .common import ProtocolError, contained, digest, file_hash, read_json


EVIDENCE_FIELDS = (
    "evidence_id", "modality", "text", "image_ids", "source_id", "source_url",
    "published_at", "archived_at", "version", "supersedes",
    "observation_root_id_if_known", "provenance_basis",
)
REVISION_FIELDS = ("evidence_id", "status", "replacement_ids")
VERDICTS = {"supported", "refuted", "insufficient"}


@dataclass
class Case:
    path: Path
    case_id: str
    event_group: str
    split: str
    family: str
    ordinal: int
    question: dict[str, Any]
    evidence: dict[str, dict[str, Any]]
    images: dict[str, dict[str, Any]]
    schedule: dict[str, Any]

    def specification(self, history: str, stage: int, control: str = "core") -> dict:
        if control == "late_false_report":
            spec = self.schedule.get("controls", {}).get(control)
            if spec is None:
                raise ProtocolError(f"{self.case_id}: no {control} specification")
            return spec
        try:
            return self.schedule["histories"][history][str(stage)]
        except KeyError as exc:
            raise ProtocolError(f"{self.case_id}: missing history/stage {history}/{stage}") from exc

    def visible(self, history: str, stage: int, control: str = "core") -> tuple[dict, list[dict]]:
        """Only this whitelist crosses into the model. Never reads gold.json."""
        spec = self.specification(history, stage, control)
        active = []
        for eid in spec["active_evidence_ids"]:
            if eid not in self.evidence:
                raise ProtocolError(f"{self.case_id}: unknown evidence {eid}")
            record = self.evidence[eid]
            active.append({key: record[key] for key in EVIDENCE_FIELDS if key in record})
        revisions = [
            {key: revision[key] for key in REVISION_FIELDS if key in revision}
            for revision in spec.get("revision_events", [])
        ]
        overrides = {}
        if control == "visual_relation_change":
            control_spec = self.schedule.get("controls", {}).get(control)
            if not control_spec or not control_spec.get("image_overrides"):
                raise ProtocolError(f"{self.case_id}: no audited visual variant")
            overrides = control_spec["image_overrides"]
        seen = set()
        assets = []
        for record in active:
            for iid in record.get("image_ids", []):
                if iid in seen:
                    continue
                seen.add(iid)
                asset = dict(overrides.get(iid, self.images[iid]))
                path = contained(self.path / "assets", asset["file"])
                observed_hash = file_hash(path)
                if observed_hash != asset["sha256"]:
                    raise ProtocolError(f"{self.case_id}/{iid}: image bytes changed")
                assets.append({"image_id": iid, "path": path, "sha256": observed_hash})
        payload = {
            "question": self.question["question"],
            "target_time": self.question["target_time"],
            "active_evidence": active,
            "revision_events": revisions,
        }
        if control in {"text_only", "human_visual_facts"}:
            assets = []
            payload["visual_input_status"] = "图片未提供，不能假装已经看过图片。"
        if control == "human_visual_facts":
            # Explicit ablation only: never reachable for core requests.
            observations = read_json(self.path / "private" / "visual_facts.json")
            payload["visual_observations"] = [
                {"image_id": item["image_id"], "observations": item["observations"]}
                for item in observations["items"] if item["image_id"] in seen
            ]
        return payload, assets


def load_cases(root: Path, split: str, case_ids: list[str] | None = None) -> list[Case]:
    root = root.resolve()
    rows = list(csv.DictReader((root / "case_manifest.csv").read_text(encoding="utf-8-sig").splitlines()))
    ids = [row["case_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ProtocolError("Duplicate case IDs in manifest")
    group_splits = {}
    for row in rows:
        if row.get("event_group"):
            group = row["event_group"]
            if group in group_splits and group_splits[group] != row["split"]:
                raise ProtocolError(f"Event group {group} crosses development/diagnostic splits")
            group_splits[group] = row["split"]
    selected = set(case_ids or [])
    if selected - set(ids):
        raise ProtocolError(f"Unknown case IDs: {sorted(selected - set(ids))}")
    cases = []
    for ordinal, row in enumerate(rows):
        if row["split"] != split or (selected and row["case_id"] not in selected):
            continue
        if row["status"] not in {"DEV_READY", "FROZEN"}:
            raise ProtocolError(f"{row['case_id']}: status={row['status']}; real assets are required")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", row["case_id"]):
            raise ProtocolError("Case IDs must be neutral alphanumeric identifiers")
        path = contained(root, f"cases/{row['case_id']}")
        records = [json.loads(line) for line in (path / "public" / "evidence.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        evidence = {item["evidence_id"]: item for item in records}
        if len(evidence) != len(records):
            raise ProtocolError(f"{row['case_id']}: duplicate evidence IDs")
        question = read_json(path / "public" / "question.json")
        image_items = read_json(path / "public" / "images.json")["images"]
        images = {item["image_id"]: item for item in image_items}
        if len(images) != len(image_items):
            raise ProtocolError(f"{row['case_id']}: duplicate image IDs")
        if any(iid not in images for record in records for iid in record.get("image_ids", [])):
            raise ProtocolError(f"{row['case_id']}: unknown image reference")
        cases.append(Case(path, row["case_id"], row["event_group"], row["split"], row["family"], ordinal,
                          question, evidence, images, read_json(path / "schedule.json")))
    if not cases or (selected and selected != {case.case_id for case in cases}):
        raise ProtocolError("Requested split/case selection is empty or incomplete")
    return cases


def validate_cases(cases: list[Case], *, audit_gold: bool = True) -> dict:
    """Data audit. Gold is allowed here, never in the runner's request builder."""
    from PIL import Image
    report = []
    for case in cases:
        if not case.event_group:
            raise ProtocolError(f"{case.case_id}: event_group is required")
        final_hashes = []
        for history in ("clean", "misled"):
            for stage in (1, 2, 3):
                payload, assets = case.visible(history, stage)
                if len(assets) > 4:
                    raise ProtocolError(f"{case.case_id}: exceeds four-image pilot limit")
                active_ids = {e["evidence_id"] for e in payload["active_evidence"]}
                withdrawn = {r["evidence_id"] for r in payload["revision_events"] if r["status"] in {"withdrawn", "superseded"}}
                if active_ids & withdrawn:
                    raise ProtocolError(f"{case.case_id}: withdrawn evidence is active")
                for asset in assets:
                    with Image.open(asset["path"]) as image:
                        image.verify()
                if stage == 3:
                    final_hashes.append(digest({"payload": payload, "images": [(a["image_id"], a["sha256"]) for a in assets]}))
        if final_hashes[0] != final_hashes[1]:
            raise ProtocolError(f"{case.case_id}: final effective evidence differs between histories")
        for name in case.schedule.get("controls", {}):
            case.visible("misled", 4 if name == "late_false_report" else 3, name)
        if audit_gold:
            gold = read_json(case.path / "private" / "gold.json")
            if gold["final_verdict"] not in VERDICTS or not gold.get("annotation_basis"):
                raise ProtocolError(f"{case.case_id}: missing label/annotation basis")
            variant = gold.get("visual_relation_change")
            if variant and (variant["verdict"] == gold["final_verdict"] or variant["verdict"] not in VERDICTS):
                raise ProtocolError(f"{case.case_id}: visual variant must have an audited changed label")
        report.append({"case_id": case.case_id, "event_group": case.event_group, "final_bundle_hash": final_hashes[0]})
    return {"status": "STRUCTURAL_CHECKS_PASSED", "human_annotation_verified": False, "cases": report}
