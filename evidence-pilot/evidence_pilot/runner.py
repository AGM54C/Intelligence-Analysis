from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .common import ProtocolError, digest, file_hash, read_json, utc_now, write_json
from .data import Case, validate_cases
from .outputs import next_state, parse_output, validate_output
from .prompting import build_request, code_identity


@dataclass(frozen=True)
class Task:
    case_id: str
    method: str
    history: str
    stage: int
    control: str = "core"

    @property
    def task_id(self) -> str:
        return f"{self.case_id}.{self.control}.{self.method}.{self.history}.s{self.stage}"


def make_tasks(cases: list[Case], config: dict, suite: str) -> list[Task]:
    if suite == "smoke":
        return [Task(case.case_id, "B", "clean", 3, "smoke_full") for case in cases]
    if suite not in {"core", "all"}:
        raise ProtocolError(f"Unknown suite: {suite}")
    tasks = [Task(case.case_id, method, history, stage) for case in cases for stage in (1, 2, 3)
             for method in ("A", "B", "C") for history in ("clean", "misled")]
    if suite == "all":
        for case in cases:
            for control in ("text_only", "human_visual_facts"):
                tasks.append(Task(case.case_id, "B", "clean", 3, control))
        plans = {item["id"]: item for item in config["required_plan"]}
        for case in cases:
            if case.case_id in plans["E2_late_false_report"]["case_ids"]:
                tasks.extend(Task(case.case_id, method, "misled", 4, "late_false_report") for method in ("A", "B", "C"))
            if case.case_id in plans["E2_visual_relation_change"]["case_ids"]:
                tasks.append(Task(case.case_id, "B", "clean", 3, "visual_relation_change"))
    return tasks


def dataset_identity(cases: list[Case]) -> str:
    # Private files are hashed for provenance, never parsed here or passed to a backend.
    return digest({case.case_id: {p.relative_to(case.path).as_posix(): file_hash(p)
                  for p in sorted(case.path.rglob("*")) if p.is_file()} for case in cases})


def read_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ProtocolError(f"Corrupted journal at line {line_no}; repair explicitly before resuming") from exc
    return records


def run(cases: list[Case], config: dict, backend, output: Path, *, suite: str = "all",
        resume: bool = False, max_calls: int | None = None, runtime_minutes: float | None = None) -> dict:
    if max_calls is not None and max_calls < 1:
        raise ProtocolError("max_calls must be positive")
    validate_cases(cases, audit_gold=False)
    if any(case.split == "diagnostic" for case in cases) and backend.execution_kind == "MODEL_INFERENCE":
        if not config.get("ready_for_model_execution") or not config["runtime"].get("frozen") or not config["data"].get("manifest_frozen"):
            raise ProtocolError("Diagnostic inference requires a frozen runtime, dataset, and approved execution config")
    tasks = make_tasks(cases, config, suite)
    for task in tasks:
        next(case for case in cases if case.case_id == task.case_id).visible(task.history, task.stage, task.control)
    identity = {
        "config": config, "code_hash": code_identity(), "dataset_hash": dataset_identity(cases),
        "backend": backend.identity(), "tasks": [asdict(task) for task in tasks],
        "cases": [{"case_id": c.case_id, "event_group": c.event_group, "split": c.split, "family": c.family} for c in cases],
    }
    fingerprint = digest(identity)
    metadata_path, log_path = output / "run.json", output / "records.jsonl"
    if output.exists() and not resume:
        raise ProtocolError("Output directory already exists; use a new directory or explicit --resume")
    if resume:
        if not metadata_path.exists():
            raise ProtocolError("Cannot resume without run.json")
        metadata = read_json(metadata_path)
        if metadata["fingerprint"] != fingerprint:
            raise ProtocolError("Resume rejected: code, data, config, backend, or task plan changed")
    else:
        output.mkdir(parents=True)
        metadata = {"fingerprint": fingerprint, "identity": identity, "created_at": utc_now(),
                    "execution_kind": backend.execution_kind, "status": "RUNNING", "sessions": []}
        write_json(metadata_path, metadata)
    records = read_records(log_path)
    if len({r["task_id"] for r in records}) != len(records):
        raise ProtocolError("Duplicate task results in journal")
    expected_order = [task.task_id for task in tasks]
    if [r["task_id"] for r in records] != expected_order[:len(records)]:
        raise ProtocolError("Journal does not match the frozen task order")
    completed = {r["task_id"]: r for r in records}
    inflight_path = output / "inflight.json"
    if inflight_path.exists():
        inflight = read_json(inflight_path)
        if inflight["task_id"] not in completed:
            raise ProtocolError("Unfinished request may already have consumed compute; inspect inflight.json. No automatic retry.")
        inflight_path.unlink()
    if any(record["status"] == "runtime_error" for record in records):
        raise ProtocolError("A runtime failure is recorded. Inspect it and start an explicitly separate run; no silent retry.")
    states, registries = {}, {}
    by_case = {case.case_id: case for case in cases}
    started = time.perf_counter()
    invoked = 0
    used_wall = sum(s.get("wall_seconds", 0) for s in metadata["sessions"])
    remaining_wall = config["budget"]["max_runtime_hours"] * 3600 - used_wall
    time_cap = min(runtime_minutes * 60, remaining_wall) if runtime_minutes is not None else remaining_wall
    if time_cap <= 0:
        raise ProtocolError("Runtime budget must be positive")
    metadata["status"] = "RUNNING"
    session = {"started_at": utc_now(), "calls": 0}
    metadata["sessions"].append(session)
    write_json(metadata_path, metadata)
    try:
        for task in tasks:
            key = (task.case_id, task.method, task.history)
            previous = [] if task.method == "B" else states.get(key, [])
            registry = {} if task.method == "B" else registries.get(key, {})
            if task.task_id in completed:
                record = completed[task.task_id]
            else:
                if (max_calls is not None and invoked >= max_calls) or time.perf_counter() - started >= time_cap:
                    metadata["status"] = "PARTIAL_BUDGET_STOP"
                    break
                case = by_case[task.case_id]
                request = build_request(case, task.method, task.history, task.stage, config, previous, task.control)
                write_json(output / "requests" / f"{task.task_id}.json", request.serializable())
                write_json(inflight_path, {"task_id": task.task_id, "started_at": utc_now(), "input_hash": request.input_hash})
                record = {**asdict(task), "task_id": task.task_id, "event_group": case.event_group, "split": case.split,
                          "execution_kind": backend.execution_kind, "seed": request.seed, "input_hash": request.input_hash,
                          "evidence_hash": request.evidence_hash, "started_at": utc_now(), "previous_state": previous,
                          "parsed_output": None, "status": "runtime_error", "usage": {}}
                call_started = time.perf_counter()
                fatal = None
                try:
                    completion = backend.generate(request)
                    invoked += 1
                    record.update(raw_output=completion.raw_output, finish_reason=completion.finish_reason,
                                  usage=completion.usage, processed_input_hash=completion.processed_input_hash)
                    if completion.finish_reason == "length_or_time_limit":
                        record.update(status="truncated", error="Generation ended without EOS at a length/time boundary")
                    else:
                        try:
                            parsed = validate_output(parse_output(completion.raw_output), method=task.method, stage=task.stage,
                                active_ids={e["evidence_id"] for e in request.payload["active_evidence"]},
                                revision_ids={e["evidence_id"] for e in request.payload["revision_events"]},
                                previous_state=previous, registry=registry)
                            record.update(status="valid", parsed_output=parsed)
                        except (ProtocolError, TypeError, KeyError) as exc:
                            record.update(status="invalid_output", error=str(exc))
                except Exception as exc:
                    invoked += 1
                    record.update(status="runtime_error", error=f"{type(exc).__name__}: {exc}")
                    fatal = exc
                record.update(finished_at=utc_now(), elapsed_seconds=time.perf_counter() - call_started)
                with log_path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                inflight_path.unlink()
                completed[task.task_id] = record
                print(f"[{len(completed)}/{len(tasks)}] {task.task_id}: {record['status']}", flush=True)
                if fatal is not None:
                    raise fatal
            if task.control == "core" and record["status"] == "valid":
                states[key] = next_state(record["parsed_output"], task.method)
                registries.setdefault(key, {}).update({h["id"]: h["statement"] for h in record["parsed_output"]["hypotheses"]})
            # Invalid/truncated responses retain the last valid state, without repair/retry.
        else:
            metadata["status"] = "COMPLETED"
    except BaseException:
        metadata["status"] = "FAILED_OR_INTERRUPTED"
        raise
    finally:
        session.update(finished_at=utc_now(), calls=invoked, wall_seconds=time.perf_counter() - started)
        metadata.update(completed_requests=len(completed), planned_requests=len(tasks))
        write_json(metadata_path, metadata)
    return {"status": metadata["status"], "execution_kind": backend.execution_kind,
            "completed_requests": len(completed), "planned_requests": len(tasks), "output": str(output)}
