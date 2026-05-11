#!/usr/bin/env python3
"""Reject commits that introduce known-private strings into coilyco-ai.

The actual list of private strings lives in the Obsidian vault at
  coilyco-vault/Obsidian Vault/Notes/network/leak-denylist.txt
NOT in this repo. The vault is not git-tracked, so the strings never
enter coilyco-ai's history.

This script is the public half of that split: it knows where to look
and how to match, but holds no needles itself.

This is NOT a generic "personal info" detector - that's not really
possible. It's a denylist of specific strings already identified as
private. It catches re-introduction of *known* slips. It does not
catch *new* leaks. Update the vault denylist file when new private
strings show up; default content destinations to the vault.

Behavior when the vault file is missing (e.g. fresh clone without
the vault synced): print a loud warning, exit 0. Failing closed
would block legitimate work; the AGENTS.md guard rule + human review
remain the second line of defense.

To bypass for a known-good case, add the file path to ALLOWLIST below.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files that legitimately reference these strings and must not trip the hook.
# Keep this list short and document why each one is here. The point of the
# hook is to catch slips in OTHER files (scripts, USER.md, JOURNAL.md, skill
# definitions, READMEs, generated artifacts other than the bundle).
ALLOWLIST = {
    "AGENTS.md",                  # the rule document; names the alias to say "don't use it"
    "coily-context-bundle.md",    # regenerated; concatenates AGENTS.md verbatim
}


def find_denylist() -> Path | None:
    """Locate the vault-side denylist file. Returns None if missing."""
    home = Path.home()
    candidates = [
        home / "projects" / "coilysiren" / "coilyco-vault" / "Obsidian Vault" / "Notes" / "network" / "leak-denylist.txt",
        Path("X:/projects-x/coilysiren/coilyco-vault/Obsidian Vault/Notes/network/leak-denylist.txt"),
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def load_needles(path: Path) -> list[str]:
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out


def staged_files() -> list[Path]:
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        text=True,
    )
    return [Path(line) for line in out.splitlines() if line]


def main() -> int:
    deny_path = find_denylist()
    if deny_path is None:
        print(
            "leak-check: WARNING - vault denylist not found. Skipping check.",
            file=sys.stderr,
        )
        print(
            "  Expected at: coilyco-vault/Obsidian Vault/Notes/network/leak-denylist.txt",
            file=sys.stderr,
        )
        print(
            "  Sync the vault, or this hook is a no-op.",
            file=sys.stderr,
        )
        return 0

    needles = load_needles(deny_path)
    if not needles:
        print(
            f"leak-check: WARNING - {deny_path} is empty. Skipping check.",
            file=sys.stderr,
        )
        return 0

    leaks: list[tuple[str, int, str, str]] = []
    for path in staged_files():
        rel = str(path)
        if rel in ALLOWLIST:
            continue
        full = REPO_ROOT / path
        if not full.is_file():
            continue
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        text_lower = text.lower()
        for needle in needles:
            if needle.lower() in text_lower:
                for i, line in enumerate(text.splitlines(), 1):
                    if needle.lower() in line.lower():
                        leaks.append((rel, i, needle, line.strip()))
                        break  # one report per needle per file is enough

    if leaks:
        # Redact both the needle hint and the line context so CI logs don't
        # re-leak the same strings the hook is rejecting. The dev needs to
        # open the file locally to see what was matched.
        print("leak-check: forbidden private strings staged.", file=sys.stderr)
        print("", file=sys.stderr)
        for path, lineno, needle, line in leaks:
            ctx = line.replace(needle, "[REDACTED]") if needle in line else "[line redacted]"
            print(f"  {path}:{lineno}  matched a denylist entry", file=sys.stderr)
            print(f"    {ctx[:160]}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "If this content belongs in coilyco-ai (it almost never does),",
            file=sys.stderr,
        )
        print(
            "add the file path to ALLOWLIST in scripts/leak-check.py and",
            file=sys.stderr,
        )
        print(
            "document why. Otherwise move the content to the vault.",
            file=sys.stderr,
        )
        print(
            'See AGENTS.md "What never goes in coilyco-ai" for the rule.',
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
