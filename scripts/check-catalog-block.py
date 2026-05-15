#!/usr/bin/env python3
"""pre-commit hook: assert this repo's catalog config has a top-level `catalog:` block.

Looks at `.agent-guard/agent-guard.yaml` first (external-facing repos),
then falls back to `.coily/coily.yaml` (Kai's personal repos). One of
the two must exist and carry the block.

Schema and rollout: coilysiren/agentic-os-kai#420. Two-file rollout: coilysiren/agentic-os-kai#480.

Required keys inside `catalog:`:
    kind, type, system, owner, lifecycle, description, dependsOn, providesApis.

`dependsOn` and `providesApis` must be lists. Trivial repos (e.g. a single
.gitignore) still declare these, using `[]` for empty rather than omitting
the key. Empty is fine. Missing is not.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import NoReturn

try:
    import yaml  # type: ignore[import-untyped, unused-ignore]
except ImportError:  # pragma: no cover
    print(
        "check-catalog-block: PyYAML not available.\n"
        "  Short-term fix: pip install pyyaml\n"
        "  Durable fix: this hook is running under `language: system` against a host\n"
        "  python that lacks pyyaml. Migrate the repo's .pre-commit-config.yaml entry\n"
        "  for catalog-block-present to the uv-managed shape (`language: python` +\n"
        "  `additional_dependencies: [pyyaml]`). Canonical block:\n"
        "    agentic-os-kai/scripts/apply-catalog-block-hook.py (MANAGED_BLOCK).\n"
        "  Refresh fleet-wide with: coily exec apply-catalog-block-hook\n"
        "  Tracker: coilysiren/agentic-os-kai#488",
        file=sys.stderr,
    )
    sys.exit(1)


REQUIRED_KEYS = (
    "kind",
    "type",
    "system",
    "owner",
    "lifecycle",
    "description",
    "dependsOn",
    "providesApis",
)
LIST_KEYS = ("dependsOn", "providesApis")
TRACKER = "coilysiren/agentic-os-kai#420"


def fail(msg: str) -> NoReturn:
    print(f"check-catalog-block: {msg}")
    print(f"  see {TRACKER} for schema")
    sys.exit(1)


CONFIG_PATHS = (
    Path(".agent-guard/agent-guard.yaml"),
    Path(".coily/coily.yaml"),
)


def main() -> int:
    path = next((p for p in CONFIG_PATHS if p.exists()), None)
    if path is None:
        fail(
            "no catalog config found. Every coilysiren/* repo needs either "
            ".agent-guard/agent-guard.yaml (external-facing) or "
            ".coily/coily.yaml (personal)."
        )

    try:
        data = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        fail(f"{path} is not valid YAML: {exc}")
    if not isinstance(data, dict):
        fail(f"{path} top level must be a mapping")

    catalog = data.get("catalog")
    if not isinstance(catalog, dict):
        fail(f"{path} missing top-level `catalog:` block")

    missing = [k for k in REQUIRED_KEYS if k not in catalog]
    if missing:
        fail(
            "catalog block missing required keys: "
            + ", ".join(missing)
            + ". Trivial repos still declare them (use [] for list keys)."
        )

    for k in LIST_KEYS:
        if not isinstance(catalog[k], list):
            fail(f"catalog.{k} must be a list (use [] for empty)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
