# VibeSKU Agent

Agent skill for [VibeSKU](https://www.vibesku.com) — AI-powered creative automation that turns product SKU photos into professional e-commerce visuals and marketplace-ready copy.

## Structure

```
skill/                     # Installed by `npx skills add`
├── SKILL.md               # Skill definition
├── bin/
│   └── vibesku.js         # Bundled CLI (self-contained, zero npm dependencies)
└── references/
    └── commands.md        # Full command reference
```

## Installation

```bash
npx skills add ullrai/vibesku-agent
```

The CLI is bundled with the skill — no separate `npm install` required. Requires Node.js >= 18.

## License

MIT
