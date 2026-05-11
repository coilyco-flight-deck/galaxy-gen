---
name: tooling-skill-authoring
description: Skill-authoring discipline for the galaxy-gen repo. Local rules, local validator, local categories.yaml. Adds or edits go through this guide. Use when adding, editing, or removing a skill under .claude/skills/, when a pre-commit hook fails on skill conventions or dead cross-links, when the categories spec needs a new prefix, or when explaining why these scripts live here. Triggers - skill, SKILL.md, frontmatter, categories.yaml, validate_skills.py, check_dead_links.py, .claude/skills, skill authoring, skill hygiene, skill discipline, add skill, new skill, skill prefix.
---

# Skill authoring for galaxy-gen

Discipline document for the `.claude/skills/` surface in this repo. Self-contained: the validator, the categories spec, the cross-link checker, and the pre-commit hooks that gate them all live in this repository.

Full structural rules are in [`references/handbook.md`](references/handbook.md).

## Layout

```
galaxy-gen/
├── .claude/skills/
│   ├── categories.yaml             # spec consumed by validate_skills.py
│   ├── coding-galaxy-gen-*/        # per-skill directories
│   │   └── SKILL.md
│   └── tooling-skill-authoring/    # this skill
│       ├── SKILL.md
│       └── references/handbook.md
├── scripts/
│   ├── validate_skills.py          # structural validator
│   └── check_dead_links.py         # markdown cross-link validator
└── .pre-commit-config.yaml         # invokes the two checks
```

All skills sit flat under `.claude/skills/`. No nesting. Sub-skill directories are invisible to the harness loader.

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
2. Create `.claude/skills/<name>/SKILL.md` with frontmatter + body.
3. Stage with `git add` and commit. The pre-commit hooks run automatically:
   - `skill-conventions` (validate_skills.py) - structure, size, em-dash check.
   - `dead-cross-links` (check_dead_links.py) - inline `[text](path.md)` targets must resolve.
   - `trufflehog` - secret scan.

To run the structural checks manually before committing:

```sh
python3 scripts/validate_skills.py <name>
python3 scripts/check_dead_links.py .claude/skills/<name>/
```

## Voice rules

The validator enforces the em-dash rule. The rest are honor-system but apply to every SKILL.md, reference file, and README that ships in this repo:

* **No em-dashes (U+2014).** Use ` - ` for sidebars.
* **No italics.** Bold only for structural anchors.
* **No prose tables.** Use flat bullets: `* <anchor> - <category> - <details>`.
* **No semicolons in prose.** Split into separate sentences.

## Size cap

`SKILL.md` is hard-capped at 500 lines and 10 KB by the validator. Past either, the harness loader degrades. Push detail into `references/<topic>.md` under the same skill directory if a SKILL.md is filling up. Reference files are not capped.

## Encode the why, not just the what

Every agent session starts cold. There is no human to ask why a rule was written. Each authoring rule below carries decision context, not just procedure. Hold that line when adding new rules.

Shape: lead with the rule, then a **Why:** line (incident, constraint, prior failure mode), then a **How to apply:** line (when the rule fires). Date-stamp the flag where useful so a future read can judge whether the why is still load-bearing.

## Skills are flat, not nested

Every skill is a peer directory directly under `.claude/skills/`. Do not nest sub-skills inside another skill's directory. Nested-skill discovery is poorly supported by the harness.

**How to apply:** routing tables in a meta-skill name peer-skill names, not paths into the meta's own dir. New routed skills get their own top-level directory.

## Design references stay in the repo

The skills here are design or usage reference for the galaxy-gen procedural sim. They are most useful adjacent to the code they describe, surface only in this repo's agent session, and gate through this repo's CI.

If a skill ever grows a runbook role (anti-signals, case library, "what to check when X breaks"), it probably belongs in a centralized investigation surface rather than in this repo. Runbook content benefits from being findable regardless of which repo's session an investigator happens to be in.

## Cross-links

Two valid forms for in-prose references to other skills:

* Bare backticks: `` `skill-name` `` - passing mention, not navigable.
* Markdown link: `` [`skill-name`](../skill-name/SKILL.md) `` - navigable.

If the name does not resolve to a real skill in this repo, `check_dead_links.py` flags it. External URLs and paths that escape the repo (`../something/...`) are out of scope for the check.
