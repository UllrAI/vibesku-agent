# VibeSKU Agent

VibeSKU agent skill repository — AI-powered e-commerce creative automation.

## Project Structure

```
├── CLAUDE.md              # Project instructions (this file)
├── AGENTS.md              # Symlink → CLAUDE.md
├── README.md              # Project overview
├── skill/                 # Skill content (installed by `npx skills add`)
│   ├── SKILL.md           # Skill definition (YAML frontmatter + Markdown)
│   ├── VERSION            # Skill semantic version (source of truth)
│   ├── bin/
│   │   └── vibesku.js     # Bundled CLI (self-contained, zero dependencies)
│   └── references/
│       ├── commands.md    # Full command reference
│       ├── ecom-hero.md   # ecom-hero template guide
│       ├── exploded-view.md  # exploded-view template guide
│       ├── kv-image-set.md   # kv-image-set template guide
│       ├── listing.md     # listing template guide
│       └── versioning.md  # Version check + auto-update policy
└── .gitignore
```

## Notes

- `bin/vibesku.js` is a pre-built CLI artifact from the VibeSKU monorepo — do not edit directly
- To update the CLI, rebuild in the VibeSKU repo (with commander bundled, CJS format) and copy the output here
