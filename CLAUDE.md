# UllrAI Skills

Agent skills repository for [UllrAI](https://ullr.ai) products — reusable instruction sets that extend AI coding agent capabilities.

## Project Structure

```
├── CLAUDE.md              # Project instructions (this file)
├── AGENTS.md              # Symlink → CLAUDE.md
├── README.md              # Project overview
├── skills/                # All skills live here
│   └── <skill-name>/
│       ├── SKILL.md       # Skill definition (YAML frontmatter + Markdown)
│       └── references/    # Detailed reference docs
└── .gitignore
```

## Skill Specification

- Each skill is a self-contained directory under `skills/`
- `SKILL.md` must include YAML frontmatter with `name` and `description` fields
- `description` should list trigger keywords for agent discovery
- Detailed docs go in a `references/` subdirectory
- Directory names use kebab-case

## Current Skills

- **vibesku** — AI-powered e-commerce creative automation (hero/KV images, listing copy)
