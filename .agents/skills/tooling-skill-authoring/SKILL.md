---
name: tooling-skill-authoring
description: Skill-authoring discipline for this repo. Local categories.yaml, hooks stamped from agentic-os via agentic-os-kai. Triggers - skill, SKILL.md, frontmatter, categories.yaml, .agents/skills, skill authoring, skill hygiene, add skill, new skill, skill prefix, pre-commit hook fail.
---

# Skill authoring for galaxy-gen

Discipline document for the `.agents/skills/` surface in this repo. The skill content and the categories spec live here. The validator and link checker run as pre-commit hooks stamped from canonical copies in [`coilysiren/agentic-os/scripts/`](https://github.com/coilysiren/agentic-os/tree/main/scripts) via `make apply-skill-discipline-hooks` in `agentic-os-kai` (see [agentic-os-kai#544](https://github.com/coilysiren/agentic-os-kai/issues/544)).

Full structural rules are in [`references/handbook.md`](references/handbook.md).

## Layout

```
galaxy-gen/
├── .agents/skills/
│   ├── categories.yaml             # spec consumed by the skill-conventions hook
│   ├── coding-galaxy-gen-*/        # per-skill directories
│   │   └── SKILL.md
│   └── tooling-skill-authoring/    # this skill
│       ├── SKILL.md
│       └── references/handbook.md
└── .pre-commit-config.yaml         # managed block stamped by agentic-os-kai
```

All skills sit flat under `.agents/skills/`. No nesting. Sub-skill directories are invisible to the harness loader.

## Categories

Galaxy-gen's [`categories.yaml`](../categories.yaml) currently allows two families:

* `coding-galaxy-gen-*` - design and reference skills scoped to this repo's procedural galaxy sim. The three current skills (`-astrophysics`, `-cosmology`, `-references`) all live here.
* `tooling-*` - agent-ecosystem meta. Only `tooling-skill-authoring` for now.

Adding a new prefix or exact-name skill: edit `categories.yaml`, then create the directory. The validator rejects unknown names by design.

## SKILL.md frontmatter

Every SKILL.md begins with YAML frontmatter:

```yaml
---
name: <directory-name>
description: <one paragraph; pack keyword aliases for discoverability>
---
```

The `description` field is what the harness keyword-matches for triggering. Lead with the canonical name, then pack 5-10 natural-language phrasings users (and agents) might reach for. Don't be terse.

## Authoring loop

1. Pick the prefix. If none fits, add to `categories.yaml` first.
2. Create `.agents/skills/<name>/SKILL.md` with frontmatter + body.
3. Stage with `git add` and commit. The pre-commit hooks run automatically:
   - `skill-conventions` - structure, size, prefix taxonomy. Reads `.agents/skills/categories.yaml`.
   - `dead-cross-links` - inline `[text](path.md)` targets inside `.agents/skills/` must resolve.
   - `commit-closes-issue` - commit message must close a same-repo GitHub issue.
   - `trufflehog` - secret scan (local hook).
   - `coily-trailer` - audit-log trailer (local hook, requires the coily CLI).

To run the structural checks manually before committing, install pre-commit and run `pre-commit run --all-files`.

## Voice rules

* **No italics.** Bold only for structural anchors.
* **No prose tables.** Use flat bullets: `* <anchor> - <category> - <details>`.
* **No semicolons in prose.** Split into separate sentences.

## Size cap

`SKILL.md` is hard-capped at 500 lines and 10 KB by the validator. Past either, the harness loader degrades. Push detail into `references/<topic>.md` under the same skill directory if a SKILL.md is filling up. Reference files are not capped.

## Encode the why, not just the what

Every agent session starts cold. There is no human to ask why a rule was written. Each authoring rule should carry decision context, not just procedure.

Shape: lead with the rule, then a **Why:** line (incident, constraint, prior failure mode), then a **How to apply:** line (when the rule fires). Date-stamp the flag where useful so a future read can judge whether the why is still load-bearing.

## Skills are flat, not nested

Every skill is a peer directory directly under `.agents/skills/`. Do not nest sub-skills inside another skill's directory. Nested-skill discovery is poorly supported by the harness.

**How to apply:** routing tables in a meta-skill name peer-skill names, not paths into the meta's own dir. New routed skills get their own top-level directory.

## Design references stay in the repo

The skills here are design or usage reference for the galaxy-gen procedural sim. They are most useful adjacent to the code they describe, surface only in this repo's agent session, and gate through this repo's CI.

If a skill ever grows a runbook role (anti-signals, case library, "what to check when X breaks"), it probably belongs in a centralized investigation surface rather than in this repo. Runbook content benefits from being findable regardless of which repo's session an investigator happens to be in.

## Cross-links

Two valid forms for in-prose references to other skills:

* Bare backticks: `` `skill-name` `` - passing mention, not navigable.
* Markdown link: `` [`skill-name`](../skill-name/SKILL.md) `` - navigable.

If the name does not resolve to a real skill in this repo, `dead-cross-links` flags it. External URLs and paths that escape the repo (`../something/...`) are out of scope.

## Upgrading the hooks

When the canonical scripts in [`coilysiren/agentic-os/scripts/`](https://github.com/coilysiren/agentic-os/tree/main/scripts) change, re-run `make apply-skill-discipline-hooks` from `agentic-os-kai` to re-stamp local copies into every consumer repo. Re-run the suite to confirm nothing broke before pushing.
