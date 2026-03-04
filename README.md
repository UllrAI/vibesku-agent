# VibeSKU Agent

Agent skill for [VibeSKU](https://www.vibesku.com) — AI-powered creative automation that turns product SKU photos into professional e-commerce visuals and marketplace-ready copy.

## Structure

```
skill/                     # Installed by `npx skills add`
├── SKILL.md               # Skill definition
├── VERSION                # Skill semantic version (source of truth)
├── bin/
│   └── vibesku.js         # Bundled CLI (self-contained, zero npm dependencies)
└── references/
    ├── commands.md        # Full command reference
    ├── ecom-hero.md       # ecom-hero template guide
    ├── exploded-view.md   # Exploded-view template guide
    ├── kv-image-set.md    # kv-image-set template guide
    ├── listing.md         # listing template guide
    └── versioning.md      # Version check + auto-update policy
```

## Installation

```bash
npx skills add ullrai/vibesku-agent
```

The CLI is bundled with the skill — no separate `npm install` required. Requires Node.js >= 18.

## License

MIT
