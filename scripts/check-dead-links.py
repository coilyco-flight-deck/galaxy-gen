#!/usr/bin/env python3
"""
Find dead cross-links inside .claude/skills/.

Scans every Markdown file under .claude/skills/, extracts inline markdown
links (`[text](target)` and `[text](target#anchor)`), and reports any
local-relative target that doesn't resolve to a real file or directory.

Out of scope:
- External URLs (anything with a scheme, e.g. http://, mailto:).
- Bare anchors (`#section`) - no anchor index is maintained.
- Paths that escape the repo via leading `../`.
- Reference-style links (`[text][ref]` definitions).
- Image links (`![alt](src)`).
- Bare skill-name mentions in prose.

Usage (when run directly):
    python3 scripts/check-dead-links.py            # scan everything
    python3 scripts/check-dead-links.py path ...   # scan only the given files

Canonical copy lives in coilysiren/agentic-os/scripts/. Each consumer repo
gets a stamped copy via agentic-os-kai's apply-skill-discipline-hooks
rollout. Exits 0 on clean, 1 with per-violation report on stderr.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Pre-commit runs the hook with the consumer repo as cwd.
REPO_ROOT = Path.cwd()
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"

LINK_RE = re.compile(
    r"(?<!\!)\[(?P<text>[^\]\n]+)\]\((?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\)"
)

EXTERNAL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "ftp://",
    "git@",
    "tel:",
    "javascript:",
)

SKIP_PATH_PARTS = {"node_modules"}
SKIP_FILE_BASENAMES = {"TEMPLATE.md"}
PLACEHOLDER_TARGETS = {"...", "TBD", "TODO"}


def is_external(target: str) -> bool:
    if target.startswith("#"):
        return True
    if target.startswith(EXTERNAL_PREFIXES):
        return True
    if target in PLACEHOLDER_TARGETS:
        return True
    if "://" in target.split("/")[0]:
        return True
    # Anything that escapes the repo via `..` is external.
    if target.startswith("../") or "/../" in target:
        return True
    return False


def strip_anchor(target: str) -> str:
    return target.split("#", 1)[0]


def iter_markdown_files(roots: list[Path]):
    for root in roots:
        if root.is_file() and root.suffix == ".md":
            if root.name in SKIP_FILE_BASENAMES:
                continue
            if SKIP_PATH_PARTS & set(root.parts):
                continue
            yield root
            continue
        if root.is_dir():
            for p in sorted(root.rglob("*.md")):
                if p.name in SKIP_FILE_BASENAMES:
                    continue
                if SKIP_PATH_PARTS & set(p.parts):
                    continue
                yield p


def strip_fenced_code(text: str) -> str:
    out = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("\n")
            continue
        out.append("\n" if in_fence else line)
    return "".join(out)


INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_inline_code(text: str) -> str:
    return INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), text)


def check_file(md_path: Path) -> list[str]:
    violations = []
    raw = md_path.read_text(errors="replace")
    text = strip_inline_code(strip_fenced_code(raw))
    for m in LINK_RE.finditer(text):
        target_raw = m.group("target")
        if is_external(target_raw):
            continue
        target = strip_anchor(target_raw).strip()
        if not target:
            continue
        resolved = (md_path.parent / target).resolve()
        try:
            resolved.relative_to(REPO_ROOT)
        except ValueError:
            violations.append(
                f"{md_path.relative_to(REPO_ROOT)}: link [{m.group('text')}]({target_raw}) "
                f"-> resolves outside repo: {resolved}"
            )
            continue
        if not resolved.exists():
            line_no = text.count("\n", 0, m.start()) + 1
            violations.append(
                f"{md_path.relative_to(REPO_ROOT)}:{line_no}: dead link "
                f"[{m.group('text')}]({target_raw}) -> {resolved.relative_to(REPO_ROOT)}"
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        prog="check-dead-links",
        description="Find dead cross-links inside the skills directory.",
    )
    parser.add_argument(
        "--skills-dir",
        default=".claude/skills",
        help="Path to the skills directory (relative to the repo root). "
        "Default: .claude/skills. Ignored when positional paths are given.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional list of paths to scope the dead-link check to. "
        "When empty, the entire --skills-dir is walked.",
    )
    ns = parser.parse_args(argv[1:])

    global SKILLS_DIR
    SKILLS_DIR = (REPO_ROOT / ns.skills_dir).resolve()

    if ns.paths:
        roots = [Path(a).resolve() for a in ns.paths]
    else:
        if not SKILLS_DIR.is_dir():
            sys.stderr.write(f"check_dead_links.py: {SKILLS_DIR} not found\n")
            return 2
        roots = [SKILLS_DIR]

    all_violations: list[str] = []
    for md in iter_markdown_files(roots):
        all_violations.extend(check_file(md))

    if not all_violations:
        print("dead-link check: OK")
        return 0

    for v in all_violations:
        sys.stderr.write(f"FAIL: {v}\n")
    sys.stderr.write(f"\n{len(all_violations)} dead link(s).\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
