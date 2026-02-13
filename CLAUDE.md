# VibeSKU Agent

VibeSKU agent skill repository — AI-powered e-commerce creative automation.

## Project Structure

```
├── CLAUDE.md              # Project instructions (this file)
├── AGENTS.md              # Symlink → CLAUDE.md
├── README.md              # Project overview
├── skill/                 # Skill content (installed by `npx skills add`)
│   ├── SKILL.md           # Skill definition (YAML frontmatter + Markdown)
│   ├── bin/
│   │   └── vibesku.js     # Bundled CLI (self-contained, zero dependencies)
│   └── references/
│       └── commands.md    # Full command reference
└── .gitignore
```

## Notes

- `bin/vibesku.js` is a pre-built CLI artifact from the VibeSKU monorepo — do not edit directly
- To update the CLI, rebuild in the VibeSKU repo (with commander bundled, CJS format) and copy the output here
