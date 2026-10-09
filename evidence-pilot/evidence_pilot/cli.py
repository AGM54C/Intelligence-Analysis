from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .common import ProtocolError, read_json, write_json


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Image-text evidence revision pilot; default backend never calls a model.")
    sub = p.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-dev", help="Create four explicitly synthetic visual development cases")
    build.add_argument("--data", type=Path, required=True)
    validate = sub.add_parser("validate", help="Check assets, schedules, labels, and final paired evidence")
    validate.add_argument("--data", type=Path, required=True)
    validate.add_argument("--split", default="development", choices=["development", "diagnostic"])
    validate.add_argument("--cases", nargs="+")
    validate.add_argument("--output", type=Path)
    run = sub.add_parser("run")
    run.add_argument("--data", type=Path, required=True)
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--split", default="development", choices=["development", "diagnostic"])
    run.add_argument("--cases", nargs="+")
    run.add_argument("--suite", choices=["smoke", "core", "all"], default="smoke")
    run.add_argument("--backend", choices=["dry-run", "transformers"], default="dry-run")
    run.add_argument("--model-path", type=Path)
    run.add_argument("--resume", action="store_true")
    run.add_argument("--max-calls", type=int)
    run.add_argument("--runtime-minutes", type=float)
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--run", type=Path, required=True)
    evaluate.add_argument("--data", type=Path, required=True)
    evaluate.add_argument("--reviews", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "build-dev":
            from .dev_data import build_dataset
            result = build_dataset(args.data)
        elif args.command == "validate":
            from .data import load_cases, validate_cases
            result = validate_cases(load_cases(args.data, args.split, args.cases))
            if args.output:
                write_json(args.output, result)
        elif args.command == "run":
            from .backends import DryRunBackend, TransformersBackend
            from .data import load_cases, validate_cases
            from .runner import make_tasks, run
            config = read_json(args.config)
            cases = load_cases(args.data, args.split, args.cases)
            validate_cases(cases, audit_gold=False)
            if args.output.exists() and not args.resume:
                raise ProtocolError("Output directory already exists; select a new directory or explicit --resume")
            for task in make_tasks(cases, config, args.suite):
                next(case for case in cases if case.case_id == task.case_id).visible(task.history, task.stage, task.control)
            if args.backend == "transformers":
                if not args.model_path:
                    raise ProtocolError("--model-path is required; this program never downloads model weights automatically")
                if args.split == "diagnostic" and not (config.get("ready_for_model_execution") and config["runtime"].get("frozen") and config["data"].get("manifest_frozen")):
                    raise ProtocolError("Freeze the diagnostic data/runtime configuration before loading model weights")
                backend = TransformersBackend(config, args.model_path)
            else:
                backend = DryRunBackend()
            result = run(cases, config, backend, args.output, suite=args.suite, resume=args.resume,
                         max_calls=args.max_calls, runtime_minutes=args.runtime_minutes)
        else:
            from .evaluation import summarize
            result = summarize(args.run, args.data, args.reviews)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ProtocolError, FileNotFoundError, ModuleNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
