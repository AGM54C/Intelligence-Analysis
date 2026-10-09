from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from evidence_pilot.backends import Completion, DryRunBackend
from evidence_pilot.common import ProtocolError, canonical, read_json, write_json
from evidence_pilot.data import load_cases, validate_cases
from evidence_pilot.dev_data import build_dataset
from evidence_pilot.evaluation import outcome, summarize
from evidence_pilot.outputs import next_state, parse_output, validate_output
from evidence_pilot.prompting import build_request
from evidence_pilot.runner import dataset_identity, make_tasks, read_records, run


ROOT = Path(__file__).resolve().parents[1]


def hypothesis(hid="R1H01", statement="画面归属尚待核对。"):
    return {"id": hid, "parent_ids": [], "statement": statement, "support_ids": ["E01"],
            "conflict_ids": [], "unresolved_points": ["尚缺完整画面。"]}


def answer(hypotheses=None, selected=None, verdict="insufficient", discarded=None):
    hs = hypotheses if hypotheses is not None else [hypothesis()]
    return {"hypotheses": hs, "selected_ids": selected if selected is not None else [h["id"] for h in hs],
            "discard_records": discarded or [], "verdict": verdict, "support_ids": [],
            "conflict_ids": [], "brief_justification": "测试数据，不是实验预测。"}


class StatefulFixture:
    name = "stateful-test-fixture"
    execution_kind = "TEST_FIXTURE"

    def identity(self):
        return {"backend": self.name, "execution_kind": self.execution_kind}

    def generate(self, request):
        previous = request.payload["previous_state"]
        # Existing hypothesis is retained verbatim. Re-evaluated citations are current.
        h = copy.deepcopy(previous[0]) if previous else hypothesis()
        if not previous:
            prefix = request.system.rsplit("前缀：", 1)[-1].split("。")[0]
            h["id"] = prefix + "01"
        return Completion(canonical(answer([h])), "eos", {})


class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.data = cls.root / "data"
        build_dataset(cls.data)
        cls.cases = load_cases(cls.data, "development")
        cls.config = read_json(ROOT / "configs" / "development.json")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def request(self, method="B", history="clean", stage=3, previous=None, control="core"):
        return build_request(self.cases[0], method, history, stage, self.config, previous, control)

    def check_answer(self, result, method="C", stage=1, previous=None, registry=None):
        return validate_output(result, method=method, stage=stage, active_ids={"E01", "E04"},
                               revision_ids={"E02", "E03"}, previous_state=previous or [], registry=registry or {})

    def test_four_cases_have_images_and_identical_final_evidence(self):
        report = validate_cases(self.cases)
        self.assertEqual(4, len(report["cases"]))
        self.assertFalse(report["human_annotation_verified"])

    def test_restart_full_inputs_and_seeds_identical(self):
        for case in self.cases:
            a = build_request(case, "B", "clean", 3, self.config, [hypothesis()])
            b = build_request(case, "B", "misled", 3, self.config, [hypothesis(statement="另外一个旧猜想。")])
            self.assertEqual(a.serializable(), b.serializable())
            self.assertEqual([], a.payload["previous_state"])

    def test_only_inherited_state_changes_final_A_input(self):
        a = self.request("A", "clean", previous=[hypothesis()])
        b = self.request("A", "misled", previous=[hypothesis(statement="不同解释。")])
        self.assertEqual(a.evidence_hash, b.evidence_hash)
        self.assertNotEqual(a.input_hash, b.input_hash)

    def test_core_does_not_read_private_answers(self):
        with patch("evidence_pilot.data.read_json", side_effect=AssertionError("Private read in core")):
            req = self.request()
        payload = canonical(req.serializable())
        self.assertNotIn("annotation_basis", payload)
        self.assertNotIn("final_verdict", payload)

    def test_unknown_public_fields_and_future_evidence_are_excluded(self):
        case = copy.deepcopy(self.cases[0])
        case.question["gold_label"] = "SECRET_GOLD"
        case.evidence["E01"]["private_note"] = "SECRET_GOLD"
        case.evidence["E04"]["text"] = "SECRET_FUTURE"
        req = build_request(case, "A", "clean", 1, self.config)
        text = canonical(req.serializable())
        self.assertNotIn("SECRET_GOLD", text)
        self.assertNotIn("SECRET_FUTURE", text)

    def test_text_and_visual_fact_controls_have_no_images(self):
        text_only = self.request(control="text_only")
        visual = self.request(control="human_visual_facts")
        self.assertFalse(text_only.assets)
        self.assertFalse(visual.assets)
        self.assertNotIn("visual_observations", text_only.payload)
        self.assertIn("visual_observations", visual.payload)

    def test_visual_variant_changes_pixels_but_preserves_text(self):
        original, variant = self.request(), self.request(control="visual_relation_change")
        self.assertEqual(original.payload, variant.payload)
        self.assertNotEqual(original.assets[0]["sha256"], variant.assets[0]["sha256"])

    def test_schedules_cannot_activate_withdrawn_evidence(self):
        case = copy.deepcopy(self.cases[0])
        case.schedule["histories"]["clean"]["3"]["active_evidence_ids"].append("E02")
        with self.assertRaisesRegex(ProtocolError, "withdrawn evidence"):
            validate_cases([case])

    def test_asset_escape_is_rejected(self):
        case = copy.deepcopy(self.cases[0])
        case.images["I01"]["file"] = "../../private/gold.json"
        with self.assertRaisesRegex(ProtocolError, "leaves"):
            case.visible("clean", 1)

    def test_parse_uses_final_answer_after_thinking(self):
        expected = answer([])
        parsed = parse_output('<think>{"verdict":"supported"}</think>\n'+canonical(expected)+'<|im_end|>')
        self.assertEqual(expected, parsed)

    def test_unclosed_thinking_or_multiple_json_objects_rejected(self):
        for raw in ('<think>'+canonical(answer()), canonical(answer())+canonical(answer()), '{"verdict":"supported","verdict":"refuted"}', '{"score":NaN}'):
            with self.subTest(raw=raw[:30]), self.assertRaises(ProtocolError):
                parse_output(raw)

    def test_removed_evidence_cannot_support_current_verdict(self):
        result = answer()
        result["support_ids"] = ["E02"]
        with self.assertRaisesRegex(ProtocolError, "inactive"):
            self.check_answer(result)

    def test_candidate_pool_capacity_and_unknown_selection_rejected(self):
        for result in (answer([hypothesis(f"R1H{i}") for i in range(5)]), answer(selected=["UNKNOWN"])):
            with self.assertRaises(ProtocolError):
                self.check_answer(result)

    def test_candidate_id_cannot_change_statement(self):
        old = hypothesis()
        new = hypothesis(statement="完全不同的事实主张。")
        with self.assertRaisesRegex(ProtocolError, "changed statement"):
            self.check_answer(answer([new]), stage=2, previous=[old], registry={old["id"]:old["statement"]})

    def test_discarded_candidate_is_not_a_survivor(self):
        hs = [hypothesis(), hypothesis("R1H02", "另一种解释。")]
        result = answer(hs, selected=[hs[0]["id"]], discarded=[{"hypothesis_id":hs[1]["id"],"reason_kind":"capacity","reason_evidence_ids":[],"brief_reason":"容量限制"}])
        self.check_answer(result)
        self.assertEqual([hs[0]], next_state(result, "C"))
        self.assertEqual([], next_state(result, "B"))

    def test_all_planned_requests_count_and_unique_ids(self):
        tasks = make_tasks(self.cases, self.config, "all")
        self.assertEqual(96, len(tasks))
        self.assertEqual(96, len({task.task_id for task in tasks}))
        self.assertEqual(72, len(make_tasks(self.cases, self.config, "core")))

    def test_state_survives_core_and_late_controls(self):
        output = self.root/"stateful"
        with redirect_stdout(io.StringIO()):
            run(self.cases[:1], self.config, StatefulFixture(), output, suite="all")
        records = read_records(output/"records.jsonl")
        self.assertTrue(all(r["status"] == "valid" for r in records))
        self.assertTrue(any(r["control"]=="late_false_report" and r["method"]=="C" and r["previous_state"] for r in records))
        for r in records:
            if r["method"] == "B":
                self.assertEqual([], r["previous_state"])

    def test_resume_does_not_duplicate_calls(self):
        output = self.root/"resume"
        with redirect_stdout(io.StringIO()):
            first = run(self.cases, self.config, DryRunBackend(), output, suite="smoke", max_calls=1)
            second = run(self.cases, self.config, DryRunBackend(), output, suite="smoke", resume=True)
        self.assertEqual("PARTIAL_BUDGET_STOP", first["status"])
        self.assertEqual(4, second["completed_requests"])
        self.assertEqual([1,3], [s["calls"] for s in read_json(output/"run.json")["sessions"]])

    def test_inflight_is_not_automatically_retried(self):
        output = self.root/"inflight"
        with redirect_stdout(io.StringIO()):
            run(self.cases, self.config, DryRunBackend(), output, suite="smoke", max_calls=1)
        write_json(output/"inflight.json", {"task_id":"D002.smoke_full.B.clean.s3"})
        with self.assertRaisesRegex(ProtocolError, "No automatic retry"):
            run(self.cases, self.config, DryRunBackend(), output, suite="smoke", resume=True)

    def test_resume_refuses_changed_config(self):
        output = self.root/"changed-config"
        with redirect_stdout(io.StringIO()):
            run(self.cases, self.config, DryRunBackend(), output, suite="smoke", max_calls=1)
        cfg = copy.deepcopy(self.config)
        cfg["generation"]["temperature"] = .9
        with self.assertRaisesRegex(ProtocolError, "Resume rejected"):
            run(self.cases, cfg, DryRunBackend(), output, suite="smoke", resume=True)

    def test_non_model_run_is_never_scored_as_accuracy(self):
        output = self.root/"no-fake-scores"
        with redirect_stdout(io.StringIO()):
            run(self.cases, self.config, DryRunBackend(), output, suite="all")
        report = summarize(output, self.data)
        self.assertEqual("NOT_COMPUTED_NON_MODEL_RUN", report["score_status"])
        self.assertIsNone(report["accuracy"])
        self.assertEqual(96, report["record_count"])
        self.assertTrue(all(r["same_full_input"] for r in report["paired_inputs"] if r["method"]=="B"))

    def test_failure_counts_distinguish_abstention_and_invalid(self):
        self.assertEqual("abstain", outcome({"status":"valid","parsed_output":{"verdict":"insufficient"}},"supported"))
        self.assertEqual("invalid", outcome({"status":"truncated"},"supported"))
        self.assertEqual("correct", outcome({"status":"valid","parsed_output":{"verdict":"insufficient"}},"insufficient"))

    def test_invalid_round_preserves_last_valid_state_without_retry(self):
        class InvalidOnce(StatefulFixture):
            def __init__(self): self.calls=0
            def generate(self,request):
                self.calls+=1
                if self.calls==7: return Completion("not JSON","eos",{})
                return super().generate(request)
        backend=InvalidOnce()
        output=self.root/"invalid-state"
        with redirect_stdout(io.StringIO()):
            run(self.cases[:1],self.config,backend,output,suite="core")
        records=read_records(output/"records.jsonl")
        self.assertEqual(18,backend.calls)
        self.assertEqual("invalid_output",records[6]["status"])
        self.assertEqual("R1H01",records[12]["previous_state"][0]["id"])

    def test_runtime_failure_is_logged_and_never_retried(self):
        class Broken(StatefulFixture):
            def generate(self,request): raise RuntimeError("intentional test failure")
        output=self.root/"runtime-failure"
        with redirect_stdout(io.StringIO()), self.assertRaisesRegex(RuntimeError,"intentional"):
            run(self.cases,self.config,Broken(),output,suite="smoke")
        self.assertEqual("runtime_error",read_records(output/"records.jsonl")[0]["status"])
        with self.assertRaisesRegex(ProtocolError,"runtime failure"):
            run(self.cases,self.config,Broken(),output,suite="smoke",resume=True)

    def test_evaluator_counts_and_primary_differences(self):
        # Hand-constructed scoring inputs live only in this temporary test directory.
        output=self.root/"scoring-unit-fixture"
        output.mkdir()
        rows=[]
        labels={"D001":"refuted","D002":"refuted","D003":"supported","D004":"supported"}
        for index,case in enumerate(self.cases):
            for method in ("A","B","C"):
                for history in ("clean","misled"):
                    label=labels[case.case_id]
                    verdict=label
                    status="valid"
                    if method=="A" and history=="misled": verdict="refuted" if label=="supported" else "supported"
                    if method=="C":
                        if history=="clean" and index>=2: verdict="insufficient"
                        if history=="misled":
                            if index==0: status="truncated"
                            elif index==1: verdict="supported"
                            elif index==3: verdict="insufficient"
                    rows.append({"case_id":case.case_id,"method":method,"history":history,"stage":3,"control":"core",
                        "task_id":f"{case.case_id}.core.{method}.{history}.s3","event_group":case.event_group,
                        "input_hash":case.case_id if method=="B" else case.case_id+history,"evidence_hash":case.case_id,
                        "seed":1,"status":status,"parsed_output":answer([],verdict=verdict),"raw_output":"unit test fixture","usage":{}})
        write_json(output/"run.json", {"status":"COMPLETED","execution_kind":"MODEL_INFERENCE",
            "UNIT_TEST_FIXTURE":True,"identity":{"cases":[{"case_id":c.case_id,"split":c.split} for c in self.cases],
            "dataset_hash":dataset_identity(self.cases)}})
        (output/"records.jsonl").write_text("".join(canonical(row)+"\n" for row in rows),encoding="utf-8")
        report=summarize(output,self.data)
        deltas={row["method"]:row["accuracy_clean_minus_misled"] for row in report["paired_differences"]}
        self.assertEqual({"A":1.0,"B":0.0,"C":.25},deltas)
        for row in report["aggregate"]:
            self.assertEqual(4,sum(row[key] for key in ("correct","wrong","abstain","invalid")))
            self.assertIsNone(row["grounded_correct_among_reviewed"])
        self.assertTrue(report["human_review_pending"])

    def test_event_group_cannot_cross_splits(self):
        folder=self.root/"cross-split"
        folder.mkdir()
        (folder/"case_manifest.csv").write_text("case_id,event_group,split,status\nD001,E1,development,DEV_READY\nP001,E1,diagnostic,FROZEN\n",encoding="utf-8")
        with self.assertRaisesRegex(ProtocolError,"crosses"):
            load_cases(folder,"development")


if __name__ == "__main__":
    unittest.main()
