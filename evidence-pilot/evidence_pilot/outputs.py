from __future__ import annotations

import json
import re

from .common import ProtocolError
from .data import VERDICTS


HYPOTHESIS_FIELDS = ("id", "parent_ids", "statement", "support_ids", "conflict_ids", "unresolved_points")


def _ids(value, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value) or len(value) != len(set(value)):
        raise ProtocolError(f"{field}: expected unique string list")
    return value


def parse_output(raw: str) -> dict:
    """Parse only the final channel, never recover a JSON example from thinking."""
    text = raw.strip()
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1].strip()
    elif "<think>" in text:
        raise ProtocolError("Unclosed thinking block")
    for token in ("<|im_end|>", "<|endoftext|>"):
        if text.endswith(token):
            text = text[:-len(token)].strip()
    # Deterministic wrapper removal is logged, not a model retry or answer repair.
    if text.startswith("```json\n") and text.endswith("```"):
        text = text[8:-3].strip()
    elif text.startswith("```\n") and text.endswith("```"):
        text = text[4:-3].strip()
    try:
        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ProtocolError(f"Duplicate JSON key: {key}")
                result[key] = value
            return result
        def reject_constant(value):
            raise ProtocolError(f"Non-finite JSON number: {value}")
        result = json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"Final answer is not one JSON object: {exc.msg}") from exc
    if not isinstance(result, dict):
        raise ProtocolError("Final answer must be an object")
    return result


def validate_output(result: dict, *, method: str, stage: int, active_ids: set[str],
                    revision_ids: set[str], previous_state: list[dict], registry: dict[str, str]) -> dict:
    required = {"hypotheses", "selected_ids", "discard_records", "verdict", "support_ids", "conflict_ids", "brief_justification"}
    if not required <= result.keys() or result.get("verdict") not in VERDICTS:
        raise ProtocolError("Missing output fields or invalid verdict")
    if not isinstance(result["brief_justification"], str):
        raise ProtocolError("brief_justification must be text")
    for key in ("support_ids", "conflict_ids"):
        if set(_ids(result[key], key)) - active_ids:
            raise ProtocolError(f"{key}: cites inactive or unknown evidence")
    hypotheses = result["hypotheses"]
    if not isinstance(hypotheses, list) or not all(isinstance(h, dict) for h in hypotheses):
        raise ProtocolError("hypotheses must be a list of objects")
    previous_ids = {h["id"] for h in previous_state}
    all_ids = [h.get("id") for h in hypotheses]
    if not all(isinstance(hid, str) for hid in all_ids) or len(set(all_ids)) != len(all_ids):
        raise ProtocolError("Hypothesis IDs are missing or duplicated")
    if len(hypotheses) > {"A": 1, "B": 4, "C": len(previous_ids) + 4}[method]:
        raise ProtocolError("Candidate capacity exceeded")
    if method == "C" and not previous_ids <= set(all_ids):
        raise ProtocolError("C must explicitly re-evaluate every previously selected candidate")
    for hypothesis in hypotheses:
        if not set(HYPOTHESIS_FIELDS) <= hypothesis.keys():
            raise ProtocolError("Incomplete hypothesis")
        hid, statement = hypothesis["id"], hypothesis["statement"]
        if not isinstance(statement, str) or not statement.strip() or len(statement) > 120:
            raise ProtocolError("Hypothesis statement must have 1–120 characters")
        if hid in previous_ids:
            if registry.get(hid) != statement:
                raise ProtocolError("Existing hypothesis ID changed statement")
        elif not re.fullmatch(rf"R{stage}H[0-9]+", hid) or hid in registry:
            raise ProtocolError("New hypothesis needs a fresh stage-scoped ID")
        if set(_ids(hypothesis["parent_ids"], "parent_ids")) - set(registry):
            raise ProtocolError("Unknown parent hypothesis")
        for key in ("support_ids", "conflict_ids"):
            if set(_ids(hypothesis[key], key)) - active_ids:
                raise ProtocolError(f"Hypothesis {key} cites inactive evidence")
        _ids(hypothesis["unresolved_points"], "unresolved_points")
    selected = _ids(result["selected_ids"], "selected_ids")
    if set(selected) - set(all_ids) or len(selected) > {"A": 1, "B": 4, "C": 4}[method]:
        raise ProtocolError("Invalid selected_ids or survivor capacity exceeded")
    discarded = result["discard_records"]
    if not isinstance(discarded, list) or not all(isinstance(r, dict) for r in discarded):
        raise ProtocolError("discard_records must be a list of objects")
    expected_discards = (previous_ids | set(all_ids)) - set(selected)
    discard_ids = [r.get("hypothesis_id") for r in discarded]
    if len(discard_ids) != len(set(discard_ids)) or set(discard_ids) != expected_discards:
        raise ProtocolError("Every removed candidate must have exactly one discard record")
    for record in discarded:
        if record.get("reason_kind") not in {"constraint_conflict", "redundant", "capacity", "other"}:
            raise ProtocolError("Invalid discard reason_kind")
        if set(_ids(record.get("reason_evidence_ids"), "reason_evidence_ids")) - (active_ids | revision_ids):
            raise ProtocolError("Discard reason cites unknown evidence")
        if not isinstance(record.get("brief_reason"), str):
            raise ProtocolError("Missing brief discard reason")
    return result


def next_state(result: dict, method: str) -> list[dict]:
    if method == "B":
        return []
    by_id = {h["id"]: h for h in result["hypotheses"]}
    return [{key: by_id[hid][key] for key in HYPOTHESIS_FIELDS} for hid in result["selected_ids"]]
