"""Render a check for HTML/CSS."""
from __future__ import annotations

from coach import Check, StuckRecord, human_duration, is_stuck, stuck_for

WIDTH = 64
RULE = "  " + "-" * WIDTH


def _wrap(text: str, indent: str = "    ", width: int = WIDTH - 4) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(indent + cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(indent + cur)
    return lines


def _headline(check: Check, kid_mode: bool = True) -> tuple[str, str]:
    if kid_mode:
        if check.clean:
            return "ALL GOOD!", "Your HTML webpage has no broken tags or issues."
        problems = len(check.silent)
        word = "1 LITTLE BUG" if problems == 1 else f"{problems} LITTLE BUGS"
        return word, "Your webpage loads, but something inside needs fixing."

    if check.clean:
        return "NOTHING WRONG", "The HTML webpage is well-formed."
    problems = len(check.silent)
    word = "ONE THING TO FIX" if problems == 1 else f"{problems} THINGS TO FIX"
    return word, "The webpage has formatting or tag problems."


def render(check: Check, rec: StuckRecord, now: float, kid_mode: bool = True) -> str:
    lines: list[str] = []
    name = check.path.replace("\\", "/").rsplit("/", 1)[-1]

    lines.append("")
    lines.append("  " + name)
    lines.append(RULE)

    verdict, why = _headline(check, kid_mode=kid_mode)
    lines.append(f"  {verdict}")
    lines.append(f"  {why}")

    if rec.signature and not check.clean:
        elapsed = stuck_for(rec, now)
        if is_stuck(rec, now):
            lines.append("")
            lines.append(f"  STUCK FOR {human_duration(elapsed).upper()}")
            if kid_mode:
                lines.append("  You are working hard on this! Same bug, "
                             f"{rec.checks} tries in a row.")
                lines.append("  Time to take a breath or ask someone for a clue!")
            else:
                lines.append("  This is not 'not trying'. Same problem, "
                             f"{rec.checks} checks in a row.")
                lines.append("  This is the moment to walk over and ask a question.")
        elif elapsed >= 60:
            lines.append("")
            if kid_mode:
                lines.append(f"  (tackling this for {human_duration(elapsed)} - you got this!)")
            else:
                lines.append(f"  (same problem for {human_duration(elapsed)} - leave them to it)")
    lines.append("")

    if check.clean:
        lines.append("  Webpage structure looks neat and clean!")
        lines.append("")
        return "\n".join(lines)

    for i, f in enumerate(check.silent):
        if i:
            lines.append(RULE)
            lines.append("")
        lines.append("  QUIET BUG - webpage may look broken" if kid_mode else "  HTML TAG ISSUE")
        lines.append("")
        lines.append(f"  Line {f.line}: {f.title}")
        for l in _wrap(f.plain):
            lines.append(l)
        lines.append("")
        lines.append("  TRY THIS" if kid_mode else "  WHAT YOU COULD SAY")
        for l in _wrap('"' + f.parent_says + '"'):
            lines.append(l)
        if f.fix_hint:
            lines.append("")
            lines.append("  WHERE TO LOOK")
            for l in _wrap(f.fix_hint):
                lines.append(l)
        if f.search:
            lines.append("")
            lines.append("  SEARCH THIS ONLINE" if kid_mode else "  IF THEY WANT TO SEARCH")
            lines.append("    " + f.search[:WIDTH])
        lines.append("")

    return "\n".join(lines)


def summary(checks: list[tuple[Check, StuckRecord]], now: float, kid_mode: bool = True) -> str:
    lines = ["", "  " + "=" * WIDTH]
    if not checks:
        lines.append("  No HTML files found" if kid_mode else "  no HTML files found")
        lines.append("  " + "=" * WIDTH)
        return "\n".join(lines)

    clean = sum(1 for c, _ in checks if c.clean)
    stuck = sum(1 for c, r in checks if r.signature and is_stuck(r, now))
    clean_label = "all good" if kid_mode else "clean"
    lines.append(f"  {len(checks)} file(s)  ·  {clean} {clean_label}  ·  {stuck} stuck")
    lines.append("  " + "=" * WIDTH)
    for c, r in checks:
        name = c.path.replace("\\", "/").rsplit("/", 1)[-1]
        if c.clean:
            mark = "all good" if kid_mode else "ok"
        elif r.signature and is_stuck(r, now):
            mark = f"STUCK {human_duration(stuck_for(r, now))}"
        else:
            n = len(c.silent)
            mark = f"{n} to fix"
        lines.append(f"    {name:<28} {mark}")
    lines.append("")
    return "\n".join(lines)
