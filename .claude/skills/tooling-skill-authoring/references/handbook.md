# Skill handbook for galaxy-gen

Companion to [`../SKILL.md`](../SKILL.md). Stand-alone structural reference for the `.claude/skills/` surface in `coilysiren/galaxy-gen`. Self-contained: every rule below is enforced by `scripts/validate_skills.py` against `.claude/skills/categories.yaml` in this repo, with no reach into `coilysiren/coilyco-ai`.

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
│   ├── check_dead_links.py
│   └── leak-check.py
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

Do not bypass the spec by adding a skill whose name doesn't match. The validator rejects unknown names by design, and it is the rejection that keeps the surface coherent.

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
* **No load-bearing as a metaphor.** Reserve it for physical-engineering uses.
* **No signature in drafts.** Kai appends her own. Never include hers.

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

External URLs, mailto links, bare anchors, and sibling-repo paths are out of scope for the dead-link check.

## 7. Pre-commit wiring

The four hooks below run on every commit. All four must pass:

* `trufflehog` - offline secret scan via the local binary.
* `leak-check` - rejects staged files that introduce known-private strings. Denylist lives outside the repo at `~/projects/coilysiren/coilyco-vault/...`; if the vault is not synced, the hook prints a warning and passes.
* `skill-conventions` - structure, size, em-dash, prefix taxonomy. Reads `.claude/skills/categories.yaml`.
* `dead-cross-links` - resolves every inline markdown link inside `.claude/skills/` to a real file.

Run the structural checks manually before committing if you want fast feedback:

```sh
python3 scripts/validate_skills.py <skill-name>
python3 scripts/check_dead_links.py .claude/skills/<skill-name>/
```

## 8. Upstream sync

Galaxy-gen vendors the three scripts (`validate_skills.py`, `check_dead_links.py`, `leak-check.py`) verbatim from `coilyco-ai/scripts/`. Coilyco-ai is the canonical upstream for the validator implementation. The categories spec, this handbook, and the SKILL.md content are galaxy-gen-tailored and do not sync upstream.

When the upstream script changes:

1. Re-copy the script verbatim from `coilyco-ai/scripts/` into `galaxy-gen/scripts/`.
2. Run the validators against the existing skills to confirm nothing broke.
3. Commit with a message naming the upstream commit.

Do not fork the script behavior. If a galaxy-gen-specific change is needed, lift it upstream first.

## 9. When to escalate to coilyco-ai

Some skill shapes belong centrally, not in galaxy-gen, even when they touch galaxy-gen:

* Runbooks, investigation guides, anti-signal libraries for galaxy-gen failures. Reason: cross-repo failure surface. An investigator under pressure should find the runbook in one place regardless of which repo's session they happen to be in.
* Cross-cutting tooling that applies to multiple repos. Reason: avoid drift across vendored copies.

Galaxy-gen's local surface stays narrow: design references, usage references, and the discipline document for the local skills. Anything broader belongs in `coilyco-ai/.claude/skills/`.
