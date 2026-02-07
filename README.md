# Agent Skills

This repository contains reusable agent skills organized under `skills/`.

## Available skills
- `skills/odt` — OpenDocument Text (ODT) creation, editing, tracked changes, schema validation, and language support (including Khmer).
- `skills/idml` — Adobe InDesign IDML creation, editing, translation workflows, validation, and schema-based checks.

## Install with `npx skills` (Recommended)
Requires Node.js and npm (so `npx` is available).

Install the skill collection:
```bash
npx skills add sungkhum/agent-skills
```

Install a single skill:
```bash
npx skills add https://github.com/sungkhum/agent-skills --skill odt
npx skills add https://github.com/sungkhum/agent-skills --skill idml
```

Optional: disable anonymous telemetry:
```bash
DISABLE_TELEMETRY=1 npx skills add sungkhum/agent-skills
```

## Quick Start (Manual copy)
Use the ODT skill in a project with agent skills enabled:

```bash
git clone https://github.com/sungkhum/agent-skills.git
mkdir -p .github/skills
cp -R agent-skills/skills/odt .github/skills/odt
cp -R agent-skills/skills/idml .github/skills/idml
```

## Claude Code (Community Marketplace)
After this repository is approved in the community marketplace, install via:

```bash
/plugin install odt-idml-skills@community
```

## Install a skill
Copy a skill folder into your agent’s skills directory.

### Generic install
```bash
git clone https://github.com/sungkhum/agent-skills.git
mkdir -p ~/.claude/skills
cp -R agent-skills/skills/odt ~/.claude/skills/odt
cp -R agent-skills/skills/idml ~/.claude/skills/idml
```

### GitHub Copilot (Agent Skills)
Copilot reads skills from `.github/skills` or `.claude/skills` inside a repo. If you want to use the ODT skill for a specific project:

```bash
# inside your project repo
mkdir -p .github/skills
cp -R /path/to/agent-skills/skills/odt .github/skills/odt
cp -R /path/to/agent-skills/skills/idml .github/skills/idml
```

## Skill structure
Each skill is a folder with a required `SKILL.md` and optional `scripts/`, `references/`, and `assets/` directories.

```
skills/<skill-name>/
  SKILL.md
  scripts/
  references/
  assets/
```

## Notes
- Do not add extra documentation files inside the skill folder.
- Keep skills lean and place deep reference material in `references/`.
