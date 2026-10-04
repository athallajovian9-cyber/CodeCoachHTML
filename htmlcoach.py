#!/usr/bin/env python3
"""CodeCoach HTML - tell kids and parents what is wrong with HTML webpages.

    python htmlcoach.py index.html         check one file
    python htmlcoach.py --folder .         check all .html underneath
    python htmlcoach.py --watch .          stay open, report on every save
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import coach as C
import report as RP

HERE = Path(__file__).resolve().parent

SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", "build", "dist"}


def find_html(folder: Path) -> list[Path]:
    out = []
    for p in sorted(folder.rglob("*.html")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    for p in sorted(folder.rglob("*.htm")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return sorted(set(out))


def main() -> int:
    ap = argparse.ArgumentParser(description="CodeCoach HTML - web coding help for kids")
    ap.add_argument("target", help="a .html file, or a folder")
    ap.add_argument("--folder", action="store_true", help="treat target as a folder")
    ap.add_argument("--watch", action="store_true", help="report again on every save")
    ap.add_argument("--kid", action="store_true", default=True,
                    help="use kid-friendly language (default: True)")
    ap.add_argument("--parent", dest="kid", action="store_false",
                    help="use parent mode language")
    ap.add_argument("--interval", type=float, default=1.0,
                    help="seconds between checks while watching")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"  no such path: {target}")
        return 2

    engine = C.Coach(state_dir=HERE)

    def one_pass() -> int:
        now = time.time()
        if target.is_dir():
            checks = [engine.examine(p, now=now) for p in find_html(target)]
            print(RP.summary(checks, now, kid_mode=args.kid))
            worst = 0
            for check, rec in checks:
                if not check.clean:
                    print(RP.render(check, rec, now, kid_mode=args.kid))
                    worst = 1
            return worst

        check, rec = engine.examine(target, now=now)
        print(RP.render(check, rec, now, kid_mode=args.kid))
        return 0 if check.clean else 1

    if args.watch:
        print(f"  watching {target}")
        print("  reports on every save · Ctrl-C to stop")
        seen: dict[str, float] = {}
        try:
            while True:
                current = {}
                files = [target] if target.is_file() else find_html(target)
                for p in files:
                    try:
                        current[str(p)] = p.stat().st_mtime
                    except OSError:
                        continue
                if current != seen:
                    seen = current
                    one_pass()
                    engine.save()
                time.sleep(max(0.2, args.interval))
        except KeyboardInterrupt:
            print()
            print("  stopped. The stuck timer is saved, so it continues next time.")
            engine.save()
            return 0

    rc = one_pass()
    engine.save()
    return rc


if __name__ == "__main__":
    sys.exit(main())
