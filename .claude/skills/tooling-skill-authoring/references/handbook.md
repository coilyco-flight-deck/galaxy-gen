# Skill handbook for galaxy-gen

Companion to [`../SKILL.md`](../SKILL.md). Structural reference for the `.claude/skills/` surface in this repo. Rules below are enforced by the hooks subscribed from [agentic-os](https://github.com/coilysiren/agentic-os) against [`.claude/skills/categories.yaml`](../../categories.yaml).

The machine-readable spec is `categories.yaml`. When this file and the YAML disagree, the YAML is authoritative. Update both together.

## 1. Layout

```
galaxy-gen/
├── .claude/skills/
│   ├── categories.yaml
│   ├── coding-galaxy-gen-*/
│   │   ├── SKILL.md
│   │   └── references/             # optional, for files that overflow SKILL.md
│   └── tooling-skill-authoring/
│       ├── SKILL.md
│       └── references/handbook.md
└── .pre-commit-config.yaml         # subscribes to agentic-os
```

Flat is the only shape. Nested skill directories are invisible to the loader.

## 2. Categories

Two families are currently allowed. Both `enforce_status: false` (no status line required).

* `coding-galaxy-gen-*` - design and reference skills scoped to this repo. Three skills today: `-astrophysics`, `-cosmology`, `-references`.
* `tooling-*` - agent-ecosystem meta. One skill today: `tooling-skill-authoring`.

Adding a new family:

1. Edit `categories.yaml` and add the entry (prefix or exact-name).
2. Update this handbook with a one-line description of the family and the reason it exists.
3. Create the directory and SKILL.md. The validator now accepts it.

Do not bypass the spec by adding a skill whose name does not match. The validator rejects unknown names by design, and the rejection is what keeps the surface coherent.

## 3. SKILL.md frontmatter

Every SKILL.md begins with YAML frontmatter, two fields required:

```yaml
---
name: <directory-name>
description: <one paragraph; pack keyword aliases liberally>
---
```

`description` is keyword-matched for triggering by the harness. Lead with the canonical skill name, then 5-10 natural-language aliases. Optimize for discoverability over brevity.

## 4. Voice rules

Honor-system. Not enforced by the validator. They apply to every SKILL.md, every reference file, and every README that ships in this repo.

* **No italics.** Bold only for structural anchors at the start of bullets or as terms-of-art on first mention.
* **No prose tables.** Use flat bullets: `* <anchor> - <category> - <details>`. Tables only where structurally required (e.g. machine-readable specs).
* **No semicolons in prose.** Split into separate sentences. Code is fine.

## 5. Size caps

* `max_skill_md_lines: 500`
* `max_skill_md_bytes: 10000`

Past either, the loader degrades. Push detail into `references/<topic>.md` under the same skill directory if a SKILL.md fills up. Reference files are not capped.

## 6. Cross-links

Two valid forms for in-prose references to other skills:

* Bare backticks: `` `skill-name` `` - passing mention, not navigable.
* Markdown link: `` [`skill-name`](../skill-name/SKILL.md) `` - navigable.

Either form: if the name does not resolve to a real skill, the `dead-cross-links` hook flags it as a defect.

External URLs, mailto links, bare anchors, and paths that escape the repo (`../`) are out of scope for the dead-link check.

## 7. Pre-commit wiring

The hooks below run on every commit. All must pass.

* `trufflehog` - offline secret scan (local hook).
* `coily-trailer` - audit-log trailer (local hook, requires the coily CLI).
* `skill-conventions` - structure, size, prefix taxonomy. From [agentic-os](https://github.com/coilysiren/agentic-os).
* `dead-cross-links` - resolves every inline markdown link inside `.claude/skills/` to a real file. From agentic-os.
* `commit-closes-issue` - commit-msg gate requiring `closes #N` for a same-repo issue. From agentic-os.

Run all hooks manually for faster feedback: `pre-commit run --all-files`.

## 8. Upgrading

Bump `rev:` for the `agentic-os` block in `.pre-commit-config.yaml` to pick up new hook versions. Run `pre-commit autoupdate` to do this in bulk. Always re-run the suite after a bump.

## 9. When to escalate

Some skill shapes belong centrally, not in galaxy-gen, even when they touch galaxy-gen:

* Runbooks, investigation guides, anti-signal libraries for galaxy-gen failures. Reason: cross-repo failure surface.
* Cross-cutting tooling that applies to multiple repos.

Galaxy-gen's local surface stays narrow: design references, usage references, and the discipline document for the local skills.
