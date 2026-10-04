"""CodeCoach HTML Coach: State management and stuck tracking."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

import html_silent as HS

STUCK_AFTER = 15 * 60


@dataclass
class Check:
    path: str
    ran: bool
    output: str
    error: None = None
    silent: list[HS.Finding] = field(default_factory=list)
    timed_out: bool = False

    @property
    def clean(self) -> bool:
        return not self.silent


@dataclass
class StuckRecord:
    signature: str = ""
    first_seen: float = 0.0
    last_seen: float = 0.0
    checks: int = 0


def signature(check: Check) -> str:
    parts: list[str] = []
    for f in check.silent:
        parts.append(f"html:{f.kind}:{f.name}:{f.title}")
    if not parts:
        return ""
    return hashlib.sha256("|".join(sorted(parts)).encode("utf-8")).hexdigest()[:16]


def update_record(prev: StuckRecord | None, sig: str, now: float) -> StuckRecord:
    if not sig:
        return StuckRecord()
    if prev is None or prev.signature != sig:
        return StuckRecord(signature=sig, first_seen=now, last_seen=now, checks=1)
    return StuckRecord(signature=sig, first_seen=prev.first_seen,
                       last_seen=now, checks=prev.checks + 1)


def stuck_for(rec: StuckRecord, now: float) -> float:
    if not rec.signature:
        return 0.0
    return max(0.0, now - rec.first_seen)


def is_stuck(rec: StuckRecord, now: float) -> bool:
    return rec.signature != "" and stuck_for(rec, now) >= STUCK_AFTER


def human_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    if seconds < 60:
        return f"{seconds} second" if seconds == 1 else f"{seconds} seconds"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
    hours = minutes // 60
    rem = minutes % 60
    return f"{hours} hour" if rem == 0 and hours == 1 else (f"{hours} hours" if rem == 0 else f"{hours}h {rem}m")


class Coach:
    def __init__(self, state_dir: Path | None = None):
        self.state_file = (state_dir / "codecoach_state.json") if state_dir else None
        self.records: dict[str, StuckRecord] = {}
        self.load()

    def load(self):
        if not self.state_file or not self.state_file.is_file():
            return
        try:
            raw = json.loads(self.state_file.read_text(encoding="utf-8"))
            for path, d in raw.items():
                self.records[path] = StuckRecord(**d)
        except Exception:
            self.records = {}

    def save(self):
        if not self.state_file:
            return
        data = {p: asdict(r) for p, r in self.records.items()}
        try:
            self.state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def examine(self, file_path: Path, now: float = 0.0) -> tuple[Check, StuckRecord]:
        if now <= 0.0:
            now = time.time()
        p_str = str(file_path.resolve())

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = ""

        findings = HS.check_html(content, path=p_str)
        check = Check(path=p_str, ran=True, output="", silent=findings)

        sig = signature(check)
        prev = self.records.get(p_str)
        rec = update_record(prev, sig, now)
        if rec.signature:
            self.records[p_str] = rec
        else:
            self.records.pop(p_str, None)

        return check, rec
