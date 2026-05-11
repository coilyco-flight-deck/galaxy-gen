# Skill handbook for galaxy-gen

Companion to [`../SKILL.md`](../SKILL.md). Stand-alone structural reference for the `.claude/skills/` surface in this repo. Every rule below is enforced by `scripts/validate_skills.py` against `.claude/skills/categories.yaml`. No external dependencies.

The machine-readable spec is [`.claude/skills/categories.yaml`](../../categories.yaml). When this file and the YAML disagree, the YAML is authoritative. Update both together.

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
├── scripts/
│   ├── validate_skills.py
│   └── check_dead_links.py
└── .pre-commit-config.yaml
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

Do not bypass the spec by adding a skill whose name doesn't match. The validator rejects unknown names by design, and the rejection is what keeps the surface coherent.

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

Some are validator-enforced, some honor-system. Either way they apply to every SKILL.md, every reference file, and every README that ships in this repo.

* **No em-dashes (U+2014).** Validator-enforced in SKILL.md prose. Use ` - ` for sidebars, parentheses for asides.
* **No italics.** Bold only for structural anchors at the start of bullets or as terms-of-art on first mention.
* **No prose tables.** Use flat bullets: `* <anchor> - <category> - <details>`. Tables only where structurally required (e.g. machine-readable specs).
* **No semicolons in prose.** Split into separate sentences. Code is fine.

The em-dash check masks inline code, fenced code blocks, quoted strings, and link targets before scanning. Legitimate uses (e.g. quoting prose from elsewhere) belong inside backticks or double quotes.

## 5. Size caps

* `max_skill_md_lines: 500`
* `max_skill_md_bytes: 10000`

Past either, the loader degrades. Push detail into `references/<topic>.md` under the same skill directory if a SKILL.md fills up. Reference files are not capped.

## 6. Cross-links

Two valid forms for in-prose references to other skills:

* Bare backticks: `` `skill-name` `` - passing mention, not navigable.
* Markdown link: `` [`skill-name`](../skill-name/SKILL.md) `` - navigable.

Either form: if the name does not resolve to a real skill, `check_dead_links.py` flags it as a defect.

External URLs, mailto links, bare anchors, and paths that escape the repo (`../`) are out of scope for the dead-link check.

## 7. Pre-commit wiring

The hooks below run on every commit. All must pass:

* `trufflehog` - offline secret scan via the local binary.
* `skill-conventions` - structure, size, em-dash, prefix taxonomy. Reads `.claude/skills/categories.yaml`.
* `dead-cross-links` - resolves every inline markdown link inside `.claude/skills/` to a real file.

Run the structural checks manually before committing for faster feedback:

```sh
python3 scripts/validate_skills.py <skill-name>
python3 scripts/check_dead_links.py .claude/skills/<skill-name>/
```

## 8. Editing the validator scripts

`validate_skills.py` and `check_dead_links.py` are Python 3, stdlib + PyYAML, ~700 lines combined. Edit them in this repo. Run the suite against the existing skills after any change to confirm nothing broke.

If a change affects the spec interpretation (new field in `categories.yaml`, new rule), update the spec, this handbook, and the relevant SKILL.md content in the same commit.
