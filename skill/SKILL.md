---
name: vibesku
description: |
  CLI for VibeSKU — an AI-powered creative automation platform that turns product SKU photos
  into professional e-commerce visuals and marketplace-ready copy at scale.
  Use when the user wants to: (1) generate hero banners, detail page poster sets, or listing copy
  from product photos via the command line, (2) authenticate with VibeSKU (browser login or API key),
  (3) browse or inspect generation templates (ecom-hero, detail-poster-set, listing),
  (4) refine AI-generated outputs with edit instructions, (5) export/download image and text results,
  (6) run batch generation across a product catalog, (7) manage credits (check balance, purchase, redeem),
  (8) configure CLI settings. Triggers on mentions of "vibesku", "product visuals", "SKU photos",
  "ecommerce images", "hero banner", "listing copy", "product image generation", "batch generation",
  "VisionKV", or any VibeSKU CLI workflow.
---

# VibeSKU CLI

Command-line interface for [VibeSKU](https://www.vibesku.com) — AI-powered creative automation that turns product SKU photos into agency-grade e-commerce visuals and marketplace-ready copy in seconds.

## What VibeSKU Does

VibeSKU replaces manual creative production for e-commerce teams. Upload a product photo, define brand guidelines, and receive complete multi-format visual sets:

- **Hero banners** (16:9) — headline-safe layouts with automatic lighting and shadow matching
- **Detail page poster sets** — cohesive visual series for PDPs and campaign storytelling
- **Listing copy** — SEO-optimized titles, benefit-led bullet points for marketplaces (Amazon, Shopify, etc.)

Core capabilities: VisionKV™ visual system (complete visual collections from a single product), high-fidelity product restoration (1:1 precision on textures/logos/packaging), multilingual text overlays, and omni-channel format output (16:9, 9:16, 1:1).

**Credit costs**: 1K/2K image = 1 credit, 4K image = 2 credits, short video = 5 credits, copy = 1 credit.

## Setup

The CLI is bundled with this skill at `bin/vibesku.js` — a self-contained Node.js script with zero external dependencies (requires Node.js >= 18).

**Determine the CLI path** relative to this skill's install location:

```bash
# The bundled CLI path (relative to this SKILL.md):
node <skill-dir>/bin/vibesku.js --help
```

**Optional**: Create a shell alias for convenience:

```bash
alias vibesku="node <skill-dir>/bin/vibesku.js"
```

When running commands in this document, replace `vibesku` with `node <skill-dir>/bin/vibesku.js` if the global command is not available.

## Authentication

Two methods, resolved in priority order:

1. **CLI token** (`vibesku auth login`) — browser-based device flow, tokens at `~/.vibesku/config.json`
2. **API key** — `VIBESKU_API_KEY` env var > config file key (from `vibesku init` or `vibesku config set-key`)

```bash
vibesku auth login                # Browser login (recommended)
vibesku init vsk_<key>            # API key for CI/CD
```

## Typical Workflow

```bash
vibesku auth login                              # 1. Authenticate
vibesku templates                               # 2. Browse templates
vibesku templates info ecom-hero                # 3. Inspect template (assets, options, example cmd)
vibesku credits                                 # 4. Check balance
vibesku generate -t ecom-hero \
  -n "Wireless Headphones" \
  -i product.jpg -l logo.png \
  -b "AudioTech"                                # 5. Generate visuals
vibesku status <job-id> --watch                 # 6. Monitor until complete
vibesku refine <output-uuid> -p "brighter background" # 7. Refine (optional, requires full UUID)
vibesku export <job-id> -o ./output             # 8. Download results
```

## Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `vibesku auth login\|logout\|status\|refresh` | Authentication management |
| `vibesku init <api-key>` | Initialize with API key (verifies against server) |
| `vibesku config set-key\|set-url\|show\|reset` | CLI configuration |
| `vibesku templates [info <id>]` | List templates / inspect template spec |
| `vibesku generate -t <id> [options]` | Generate visuals or copy (auto-uploads assets) |
| `vibesku refine <output-id> -p <prompt>` | Refine output with edit instructions |
| `vibesku status <job-id> [--watch]` | Check job progress and output list |
| `vibesku jobs [-p <page>] [-t <template>]` | List jobs with pagination and filter |
| `vibesku export <job-id> [-o <dir>]` | Download images and text outputs |
| `vibesku batch <file> [--dry-run]` | Bulk generation from JSON file |
| `vibesku credits [show\|buy\|redeem <code>]` | Credit balance, purchase, and redemption |

All commands support `--json` for machine-readable output (pipe to `jq`).

## Command Details

For full option flags, usage examples, and batch file format, see [commands.md](references/commands.md).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `VIBESKU_API_KEY` | API key (overrides config file) |
| `VIBESKU_BASE_URL` | Custom API URL (overrides config file) |
| `NO_COLOR` | Disable colored output |

## Key Behaviors

- **Asset upload**: `vibesku generate -i` auto-uploads product images; `-l` uploads logo
- **Credit tracking**: Generation and refine show remaining balance on success; insufficient credits prompt to buy/redeem
- **Watch mode**: `vibesku status --watch` polls every 5s until all runs complete
- **Interactive menus**: `vibesku credits buy` shows pricing menu in TTY; use `--tier`/`--mode` for CI
- **Non-interactive detection**: Auto-detects piped input / no TTY (implies `--no-browser` for auth)
- **Refinement lineage**: `vibesku status` output table shows parent→child relationships for refined outputs
- **Modify vs Regenerate**: To modify an existing output (change background, adjust lighting, remove elements, etc.), use `vibesku refine <output-id> -p "<instruction>"` instead of generating a new image. Only use `vibesku generate` when creating from scratch.
- **Full UUID required for refine**: `vibesku refine` requires a full UUID (e.g. `beb47f34-fdf8-49c4-9b9f-96bd367ed145`). The `vibesku status` table truncates IDs — use `vibesku status <job-id> --json` to get full output UUIDs.
- **Agent-friendly output**: When used by AI agents or in automation pipelines, prefer `--json` flag for all commands. For example, `vibesku templates --json` returns all template metadata in a single call, avoiding the need to run `vibesku templates info <id>` for each template individually.
