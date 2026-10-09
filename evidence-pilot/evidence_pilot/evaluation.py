from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from .common import ProtocolError, read_json, write_json
from .data import load_cases
from .runner import dataset_identity, read_records


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def outcome(record: dict, gold: str) -> str:
    if record["status"] != "valid":
        return "invalid"
    verdict = record["parsed_output"]["verdict"]
    if verdict == gold:
        return "correct"
    return "abstain" if verdict == "insufficient" else "wrong"


def summarize(run_dir: Path, dataset_root: Path, review_path: Path | None = None) -> dict:
    metadata = read_json(run_dir / "run.json")
    records = read_records(run_dir / "records.jsonl")
    report_dir = run_dir / "evaluation"
    report_dir.mkdir(exist_ok=True)
    paired_inputs = []
    indexed = {(r["case_id"], r["method"], r["history"]): r for r in records if r["control"] == "core" and r["stage"] == 3}
    for (cid, method, history), clean in indexed.items():
        if history != "clean" or (cid, method, "misled") not in indexed:
            continue
        misled = indexed[(cid, method, "misled")]
        paired_inputs.append({"case_id": cid, "method": method,
            "same_evidence": clean["evidence_hash"] == misled["evidence_hash"],
            "same_full_input": clean["input_hash"] == misled["input_hash"],
            "same_seed": clean["seed"] == misled["seed"],
            "same_processed_input": (clean.get("processed_input_hash") == misled.get("processed_input_hash")) if clean.get("processed_input_hash") and misled.get("processed_input_hash") else None,
            "same_raw_output": clean.get("raw_output") == misled.get("raw_output")})
    _write_csv(report_dir / "paired_input_audit.csv", paired_inputs)
    common = {"execution_kind": metadata["execution_kind"], "run_status": metadata["status"],
              "record_count": len(records), "paired_inputs": paired_inputs}
    if metadata["execution_kind"] != "MODEL_INFERENCE":
        result = {**common, "score_status": "NOT_COMPUTED_NON_MODEL_RUN", "accuracy": None,
                  "note": "This is a pipeline check. Fixture outputs are never reported as model performance."}
        write_json(report_dir / "summary.json", result)
        return result
    if any(not row["same_evidence"] or (row["method"] == "B" and (not row["same_full_input"] or not row["same_seed"] or row["same_processed_input"] is False)) for row in paired_inputs):
        raise ProtocolError("Paired-input audit failed; repair implementation before interpreting accuracy")
    selected_cases = metadata["identity"]["cases"]
    splits = {c["split"] for c in selected_cases}
    cases = [case for split in sorted(splits) for case in load_cases(dataset_root, split, [c["case_id"] for c in selected_cases if c["split"] == split])]
    if dataset_identity(cases) != metadata["identity"]["dataset_hash"]:
        raise ProtocolError("Dataset changed since the run; preserve the original labels/assets before scoring")
    by_case = {c.case_id: c for c in cases}
    golds = {c.case_id: read_json(c.path / "private" / "gold.json") for c in cases}
    review_rows = read_records(review_path) if review_path else []
    reviews = {r["task_id"]: r for r in review_rows}
    if len(reviews) != len(review_rows) or set(reviews) - {r["task_id"] for r in records}:
        raise ProtocolError("Human review contains duplicate or unknown task IDs")
    rows, review_template = [], []
    for record in records:
        review_template.append({"task_id": record["task_id"], "grounded_correct": None,
            "compatible_candidate_generated": None, "compatible_candidate_selected": None,
            "verdict_uses_compatible_candidate": None, "error_types": [], "reviewer": None, "notes": ""})
        if record["stage"] < 3:
            continue
        cid, control = record["case_id"], record["control"]
        gold = golds[cid]["visual_relation_change"]["verdict"] if control == "visual_relation_change" else golds[cid]["final_verdict"]
        result = outcome(record, gold)
        reviewed = reviews.get(record["task_id"], {}).get("grounded_correct")
        if reviewed is not None and not isinstance(reviewed, bool):
            raise ProtocolError("grounded_correct review must be true, false, or null")
        if reviewed is True and result != "correct":
            raise ProtocolError("A wrong/invalid verdict cannot be counted as grounded_correct")
        rows.append({"task_id": record["task_id"], "case_id": cid, "event_group": by_case[cid].event_group,
                     "method": record["method"], "history": record["history"], "control": control,
                     "stage": record["stage"], "gold": gold, "outcome": result, "grounded_correct": reviewed})
    groups = defaultdict(list)
    for row in rows:
        groups[(row["method"], row["history"], row["control"], row["stage"])].append(row)
    aggregate = []
    for (method, history, control, stage), members in groups.items():
        counts = Counter(row["outcome"] for row in members)
        event_scores = defaultdict(list)
        for row in members:
            event_scores[row["event_group"]].append(int(row["outcome"] == "correct"))
        n = len(members)
        item = {"method": method, "history": history, "control": control, "stage": stage,
                "n_cases": n, "n_events": len(event_scores), **{key: counts[key] for key in ("correct", "wrong", "abstain", "invalid")},
                "accuracy": counts["correct"] / n, "event_macro_accuracy": sum(sum(v)/len(v) for v in event_scores.values())/len(event_scores),
                "coverage": (counts["correct"] + counts["wrong"]) / n,
                "grounded_reviewed": sum(r["grounded_correct"] is not None for r in members),
                "grounded_correct_among_reviewed": sum(r["grounded_correct"] is True for r in members)}
        for label in ("supported", "refuted"):
            label_rows = [row for row in members if row["gold"] == label]
            correct = sum(row["outcome"] == "correct" for row in label_rows)
            item[f"{label}_correct"] = correct
            item[f"{label}_n"] = len(label_rows)
            item[f"{label}_recall"] = correct / len(label_rows) if label_rows else None
        recall_values = [item[f"{label}_recall"] for label in ("supported", "refuted")]
        item["macro_recall"] = sum(recall_values) / 2 if all(v is not None for v in recall_values) else None
        if not item["grounded_reviewed"]:
            item["grounded_correct_among_reviewed"] = None
        aggregate.append(item)
    outcome_index = {(r["case_id"], r["method"], r["history"]): r for r in rows if r["control"] == "core" and r["stage"] == 3}
    transitions = []
    for cid, method, history in outcome_index:
        if history == "clean" and (cid, method, "misled") in outcome_index:
            transitions.append({"case_id": cid, "event_group": by_case[cid].event_group, "method": method,
                "clean_outcome": outcome_index[(cid, method, "clean")]["outcome"],
                "misled_outcome": outcome_index[(cid, method, "misled")]["outcome"]})
    _write_csv(report_dir / "final_cases.csv", rows)
    _write_csv(report_dir / "aggregate.csv", aggregate)
    _write_csv(report_dir / "paired_outcomes.csv", transitions)
    differences = []
    for method in ("A", "B", "C"):
        pairs = [p for p in transitions if p["method"] == method]
        if not pairs:
            continue
        event_deltas = defaultdict(list)
        for pair in pairs:
            event_deltas[pair["event_group"]].append(int(pair["clean_outcome"] == "correct") - int(pair["misled_outcome"] == "correct"))
        counts = Counter((p["clean_outcome"], p["misled_outcome"]) for p in pairs)
        differences.append({"method":method, "paired_cases":len(pairs), "paired_events":len(event_deltas),
            "accuracy_clean_minus_misled":sum(sum(v) for v in event_deltas.values())/len(pairs),
            "event_macro_difference":sum(sum(v)/len(v) for v in event_deltas.values())/len(event_deltas),
            "correct_to_wrong":counts[("correct","wrong")], "wrong_to_correct":counts[("wrong","correct")]})
    _write_csv(report_dir / "paired_differences.csv", differences)
    control_changes = []
    for row in rows:
        if row["control"] not in {"visual_relation_change", "late_false_report"}:
            continue
        base_history = "misled" if row["control"] == "late_false_report" else "clean"
        base = outcome_index.get((row["case_id"], row["method"], base_history))
        if base:
            control_changes.append({"case_id":row["case_id"], "method":row["method"], "control":row["control"],
                "original_gold":base["gold"], "variant_gold":row["gold"], "original_outcome":base["outcome"],
                "variant_outcome":row["outcome"], "correct_to_wrong":base["outcome"]=="correct" and row["outcome"]=="wrong"})
    _write_csv(report_dir / "control_changes.csv", control_changes)
    candidate_audits = []
    for cid, method, history in outcome_index:
        if method == "B":
            continue
        ids = [f"{cid}.core.{method}.{history}.s{stage}" for stage in (1,2,3)]
        annotations = [reviews.get(tid,{}) for tid in ids]
        fields = ("compatible_candidate_generated", "compatible_candidate_selected", "verdict_uses_compatible_candidate")
        for annotation in annotations:
            if any(annotation.get(field) is not None and not isinstance(annotation[field],bool) for field in fields):
                raise ProtocolError("Candidate review values must be true, false, or null")
        complete = all(isinstance(a.get(field),bool) for a in annotations for field in fields[:2])
        eligible = (any(a[fields[0]] for a in annotations[:2]) and not annotations[1][fields[1]]) if complete else None
        candidate_audits.append({"case_id":cid,"method":method,"history":history,"review_complete":complete,
            "generation_failure_before_correction":not any(a[fields[0]] for a in annotations[:2]) if complete else None,
            "eligible_for_recovery_at_stage3":eligible,
            "reasonable_candidate_returned":annotations[2][fields[0]] if eligible else None,
            "reasonable_candidate_restored_to_pool":annotations[2][fields[1]] if eligible else None,
            "verdict_uses_compatible_candidate":annotations[2].get(fields[2])})
    _write_csv(report_dir / "candidate_review.csv", candidate_audits)
    template_path = report_dir / "human_review_template.jsonl"
    if not template_path.exists():
        import json
        template_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in review_template), encoding="utf-8")
    gpu_seconds = sum(r.get("usage", {}).get("gpu_seconds") or 0 for r in records)
    result = {**common, "score_status": "EXPLORATORY_DESCRIPTIVE", "aggregate": aggregate,
              "data_splits":sorted(splits), "paired_differences":differences,
              "human_review_pending": any(r["grounded_correct"] is None for r in rows),
              "measured_generation_gpu_seconds": gpu_seconds,
              "billed_cost": None, "billing_note": "Generation time excludes rental idle time and model loading; use provider billing separately.",
              "B_output_difference_count": sum(r["method"] == "B" and not r["same_raw_output"] for r in paired_inputs)}
    write_json(report_dir / "summary.json", result)
    return result
