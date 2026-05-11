---
name: tooling-skill-authoring
description: Skill-authoring discipline for coilysiren/galaxy-gen. Local rules, local validator, local categories.yaml. Galaxy-gen runs its own skill hygiene end-to-end without reaching into coilyco-ai. Use when adding, editing, or removing a skill under .claude/skills/, when a pre-commit hook fails on skill conventions or dead cross-links, when the categories spec needs a new prefix, or when explaining why these scripts live here. Triggers - skill, SKILL.md, frontmatter, categories.yaml, validate_skills.py, check_dead_links.py, .claude/skills, skill authoring, skill hygiene, skill discipline, add skill, new skill, skill prefix.
---

# Skill authoring for galaxy-gen

This file is the discipline document for the `.claude/skills/` surface inside `coilysiren/galaxy-gen`. It is self-contained. The validator, the categories spec, the cross-link checker, and the leak-check all run from this repo's `scripts/`, gated by this repo's `.pre-commit-config.yaml`, with no reach back into `coilysiren/coilyco-ai`.

The handbook for structural rules (prefix list, frontmatter shape, voice rules) lives at [`references/handbook.md`](references/handbook.md).

## Layout

```
galaxy-gen/
├── .claude/skills/
│   ├── categories.yaml             # spec consumed by validate_skills.py
│   ├── coding-galaxy-gen-*/        # per-skill directories
│   │   └── SKILL.md
│   └── tooling-skill-authoring/    # this skill
│       ├── SKILL.md
│       └── references/handbook.md  # structural rules
├── scripts/
│   ├── validate_skills.py          # structural validator
│   ├── check_dead_links.py         # markdown cross-link validator
│   └── leak-check.py               # private-string denylist
└── .pre-commit-config.yaml         # invokes the three checks
```

All skills sit flat under `.claude/skills/`. No nesting. Sub-skill directories are invisible to the loader.

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
2. Create `<repo>/.claude/skills/<name>/SKILL.md` with frontmatter + body.
3. Stage with `git add` and commit. The pre-commit hooks run automatically:
   - `skill-conventions` (validate_skills.py) - structure, size, em-dash check.
   - `dead-cross-links` (check_dead_links.py) - inline `[text](path.md)` targets must resolve.
   - `leak-check` - blocks known-private strings.
   - `trufflehog` - secret scan.

To run the checks manually before committing:

```sh
python3 scripts/validate_skills.py <name>
python3 scripts/check_dead_links.py .claude/skills/<name>/
```

## Voice rules

The validator enforces some. The rest are honor-system but apply to every SKILL.md, reference file, and README that ships in this repo:

* **No em-dashes (U+2014).** The validator flags them in SKILL.md prose. Use ` - ` for sidebars.
* **No italics.** Bold only for structural anchors.
* **No prose tables.** Use flat bullets: `* <anchor> - <category> - <details>`.
* **No semicolons in prose.** Split into separate sentences.
* **No signature.** Drafts never include Kai's signature; she appends it.

## Size cap

`SKILL.md` is hard-capped at 500 lines and 10 KB by the validator. Past either, the harness loader degrades. Push detail into `references/<topic>.md` under the same skill directory if a SKILL.md is filling up.

## Encode the why, not just the what

Every agent session starts cold. There is no human to ask why a rule was written. Each authoring rule below carries decision context, not just procedure. Hold that line when adding new rules.

Shape: lead with the rule, then a **Why:** line (incident, constraint, prior failure mode), then a **How to apply:** line (when the rule fires). Date-stamp the flag where useful so a future read can judge whether the why is still load-bearing.

## Skills are flat, not nested

Every skill is a peer directory directly under `.claude/skills/`. Do not nest sub-skills inside another skill's directory. Nested-skill discovery is poorly supported by the harness, and the global symlink convention (when used) only handles top-level skill dirs.

**Why:** the same flat-not-nested rule applies in coilyco-ai for the same reasons. Pre-flagged here so galaxy-gen authors don't reinvent the lesson.

**How to apply:** routing tables in a meta-skill name peer-skill names, not paths into the meta's own dir. New routed skills get their own top-level directory.

## Co-location is the right shape for these skills

These skills are pure design or usage reference for galaxy-gen specifically. They have no cross-repo failure surface, no runbook role, and never get invoked under partial-failure conditions where pulling in a sibling repo would be a problem.

**Why:** Kai's broader rule keeps investigation skills central in `coilyco-ai/.claude/skills/` so an investigator under pressure never has to clone three repos to find the right runbook. Design-reference skills are the inverse case: they are most useful when *adjacent to the code that uses them*, surface only in the right repo's session, and benefit from CI gating in the same repo as the code.

**How to apply:** if a galaxy-gen skill ever grows a runbook role (anti-signals, case library, "what to check when X breaks"), move it to `coilyco-ai/.claude/skills/` and add it to the appropriate router skill there. Don't keep runbook-shaped content here.

## Upstream sync

The scripts in `scripts/` (`validate_skills.py`, `check_dead_links.py`, `leak-check.py`) are vendored verbatim from `coilyco-ai/scripts/`. Coilyco-ai is the canonical upstream. When the upstream script changes, re-copy. Do not fork the behavior.

The discipline document (this SKILL.md) is intentionally galaxy-gen-tailored, not a verbatim copy of coilyco-ai's `tooling-skill-authoring`. Coilyco-ai's version covers a much larger skill surface (eleven prefix families, several exact-name skills) and a different toolchain (`setup.sh` for global symlinks, plugin-marketplace fast-forwards, Python-helpers bias). None of that applies here. If the broader policy in coilyco-ai changes (e.g. new exception to the co-location rule), update this file by hand.
