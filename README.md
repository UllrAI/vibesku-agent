# UllrAI Skills

Reusable agent skills for [UllrAI](https://ullr.ai) products. Each skill is a directory containing a `SKILL.md` with YAML frontmatter and optional reference files.

## Available Skills

| Skill | Description |
|-------|-------------|
| [vibesku](skills/vibesku) | AI-powered creative automation that turns product SKU photos into professional e-commerce visuals and marketplace-ready copy |

## Skill Structure

```
skills/
└── <skill-name>/
    ├── SKILL.md              # Skill definition (YAML frontmatter + instructions)
    └── references/           # Optional supporting docs
        └── *.md
```

## Installation

Install any skill using the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add ullrai/skills
```

Or install a specific skill:

```bash
npx skills add ullrai/skills/skills/vibesku
```

## Creating a New Skill

1. Create a directory under `skills/` with your skill name
2. Add a `SKILL.md` with YAML frontmatter (`name` and `description` fields)
3. Add any reference docs in a `references/` subdirectory
4. Update this README's skill table

## License

MIT
