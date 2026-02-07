# Agent Skills

This repository contains reusable agent skills organized under `skills/`.

## Available skills
- `skills/odt` — OpenDocument Text (ODT) creation, editing, tracked changes, schema validation, and language support (including Khmer).

## Install a skill
Copy a skill folder into your agent’s skills directory.

Example:
```bash
git clone https://github.com/sungkhum/agent-skills.git
mkdir -p ~/.claude/skills
cp -R agent-skills/skills/odt ~/.claude/skills/odt
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
