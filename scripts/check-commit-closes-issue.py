#!/usr/bin/env python3
"""Reject commit messages that lack a same-repo GitHub closing keyword.

Wired into each active coilysiren/* repo as a `commit-msg` pre-commit hook
via `apply-commit-msg-hook.py`. Canonical copy lives here in coilyco-ai;
rollout copies this file verbatim into each sibling repo.

Accepted patterns (case-insensitive):
    closes #N | close #N | closed #N
    fixes #N  | fix #N   | fixed #N
    resolves #N | resolve #N | resolved #N
    <this-owner>/<this-repo>#N with any of the above keywords

Rejected: cross-repo refs (`owner/other-repo#N`). The issue must live
in the repo the commit lands in. If the rule needs to span repos,
file the issue locally and link out from there instead.

Exempt: Merge / Revert / fixup! / squash! commits.

Exits 0 on accept, 1 on reject (with a dictation-friendly error
that names the fix to apply from a phone).
"""

from __future__ import annotations

import re
import subprocess
import sys

KEYWORD_RE = re.compile(
    r"\b(close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+([\w.-]+/[\w.-]+)?#\d+",
    re.IGNORECASE,
)
EXEMPT_PREFIXES = ("Merge ", "Revert ", "fixup! ", "squash! ")
ERROR = (
    "ERROR: commit message must close an issue in this repo.\n"
    "  Add 'closes #N' (or fixes #N / resolves #N) to the message.\n"
    "  Cross-repo refs (owner/other-repo#N) are rejected.\n"
    "  File the issue in this repo first if one does not exist (gh issue create).\n"
)
REMOTE_RE = re.compile(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$")


def this_repo() -> tuple[str, str] | None:
    """Return (owner, repo) lowercased from git remote 'origin', or None."""
    try:
        out = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = REMOTE_RE.search(out)
    if not m:
        return None
    return (m.group(1).lower(), m.group(2).lower())


def has_same_repo_ref(body: str, this: tuple[str, str] | None) -> bool:
    for match in KEYWORD_RE.finditer(body):
        qualifier = match.group(2)
        if qualifier is None:
            return True
        if this is None:
            continue
        owner, repo = qualifier.lower().split("/", 1)
        if (owner, repo) == this:
            return True
    return False


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write("usage: check-commit-closes-issue.py <commit-msg-file>\n")
        return 2
    raw = open(argv[1], encoding="utf-8").read()
    body = re.sub(r"(?m)^#.*\n?", "", raw).strip()
    if not body:
        return 0
    first_line = body.split("\n", 1)[0]
    if first_line.startswith(EXEMPT_PREFIXES):
        return 0
    if has_same_repo_ref(body, this_repo()):
        return 0
    sys.stderr.write(ERROR)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
