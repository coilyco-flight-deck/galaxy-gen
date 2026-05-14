#!/usr/bin/env python3
"""pre-commit hook: assert .coily/coily.yaml has a top-level `catalog:` block.

Schema and rollout: coilysiren/coilyco-ai#420.

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
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover
    print(
        "check-catalog-block: PyYAML not available. Install with `pip install pyyaml`.",
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
TRACKER = "coilysiren/coilyco-ai#420"


def fail(msg: str) -> NoReturn:
    print(f"check-catalog-block: {msg}")
    print(f"  see {TRACKER} for schema")
    sys.exit(1)


def main() -> int:
    path = Path(".coily/coily.yaml")
    if not path.exists():
        fail(f"{path} not found. Every coilysiren/* repo needs a coily.yaml.")

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
