from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ProtocolError(ValueError):
    """A request or artifact violates the declared experiment protocol."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def contained(root: Path, relative: str) -> Path:
    """Resolve symlinks and reject absolute paths and parent-directory escapes."""
    rel = Path(relative)
    if rel.is_absolute():
        raise ProtocolError(f"Expected relative path: {relative}")
    path = (root / rel).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ProtocolError(f"Path leaves the declared root: {relative}")
    return path
