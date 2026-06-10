# Template: scenario-set

**Purpose**: Generate a complete platform-ready image set from one upload in a single pass. Pick a scenario card (a platform × purpose recipe such as an Amazon listing pack) and VibeSKU fans out every selected image slot — white-background packshots, hero images, lifestyle scenes, detail close-ups, infographic posters — as one coordinated batch.

**When to use**: User is launching or refreshing a COMPLETE listing on a specific platform (Amazon, Taobao/Tmall, Shopify, RED/Xiaohongshu) and wants the whole image set at once instead of running single templates one by one. For one precise image, use the single template (`white-background`, `ecom-hero`, `lifestyle-scene`, etc.) directly.

**Output type**: IMAGE | **Supports analysis**: Yes | **Cost**: 1K/2K = 1 credit/slot, 4K = 2 credits/slot

## Assets

| Role | Min | Max | Required |
|------|-----|-----|----------|
| PRODUCT (product images) | 1 | 10 | Yes |
| LOGO (brand logo) | 0 | 1 | No |

Upload multiple product angles when possible — some slots (alternate-angle catalog shots) reference a specific photo by upload order and degrade to a best-effort angle change when that photo is missing.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenarioId` | string | — (required) | **Scenario card** — the platform × purpose recipe (see below) |
| `slots` | string[] | — (required) | Slot IDs selected from that scenario's recipe — each slot = 1 output image |
| `imageSize` | string | `2K` | Resolution: `1K`, `2K`, or `4K` |
| `primaryLang` | string | scenario default | Language for on-image text (posters/infographics). Omit or `null` to use the scenario's marketplace default |

## Scenario Cards

| Scenario ID | Platform / Purpose | Default language | Slot recipe (slot id → content) |
|-------------|--------------------|------------------|--------------------------------|
| `amazon-pack` | Amazon listing image set | `en` | `main` (white-bg main, locked), `angle-2`/`angle-3` (alt-angle white-bg, best-effort, use photos #2/#3), `lifestyle`, `selling-points`, `detail` |
| `taobao-pack` | Taobao/Tmall 主图 + 详情页 | `zh-Hans` | Main images: `main-1` (hero, locked), `main-2` (alt angle), `main-3` (detail close-up), `main-4` (specs), `main-5` (white-bg). Detail page: `detail-hero` (selling points), `detail-lifestyle` (story poster), `detail-painpoint`, `detail-usage` (off by default) |
| `shopify-pack` | Shopify storefront set | `en` | `banner` (16:9 hero banner, locked), `main` (white-bg), `lifestyle-1`, `lifestyle-2` (in-use), `detail`, `callouts` (selling points) |
| `red-pack` | RED / Xiaohongshu post set | `zh-Hans` | `cover` (3:4 vertical poster, locked), `inner-lifestyle` (in-use), `inner-detail`, `inner-review` (review-style visual) |
| `custom-pack` | Build-your-own set | `en` | One slot per slot type — every slot id equals its slot type id (e.g. `white-bg-main`, `lifestyle`, `exploded-infographic`); pick any combination |

Notes:

- **Locked slots** are the anchor image of the pack (e.g. Amazon's white-background main). The dashboard always keeps them on; via API/CLI you may omit them, but including the locked slot is strongly recommended.
- **`slots` must come from the chosen scenario's recipe** — unknown slot ids are ignored, and at least one valid slot is required.
- Slot order in the recipe determines output order.

## Slot Types (content catalog)

Each slot maps to one of these content types. `custom-pack` exposes all of them as directly selectable slots.

| Slot type | Content | Ratio | Renders via |
|-----------|---------|-------|-------------|
| `white-bg-main` | Clean white-background main packshot | 1:1 | white-background engine |
| `white-bg-angle` | Alternate-angle catalog shot (uses matching photo when provided) | 1:1 | white-background engine |
| `hero-main` | Hero main image with styled staging | 1:1 | ecom-hero MAIN_IMAGE |
| `hero-banner` | Wide marketing banner | 16:9 | ecom-hero BANNER |
| `hero-poster` | Vertical promo poster | 3:4 | ecom-hero POSTER |
| `lifestyle` | Product in a realistic context scene | 1:1 | lifestyle-scene |
| `lifestyle-in-use` | Hands-on usage scene | 4:5 | lifestyle-scene (hand-only) |
| `lifestyle-story` | Lifestyle story poster with copy | 3:4 | KV lifestyle scene |
| `selling-points` | Selling-point visual with callouts | 1:1 | KV hero scene |
| `detail-texture` | Material/texture macro close-up | 1:1 | KV detail scene |
| `detail-function` | Functional detail / mechanism shot | 1:1 | KV functional detail scene |
| `specs-attributes` | Specs & attributes table visual | 1:1 | KV specs scene |
| `exploded-infographic` | Technical exploded infographic | 3:4 | exploded-view engine |
| `social-proof` | Review-style trust visual | 3:4 | KV social-proof scene |
| `pain-point` | Pain point vs. solution contrast | 3:4 | KV pain-point scene |
| `brand-story` | Brand story editorial poster | 3:4 | KV brand-story scene |
| `usage-guide` | Step-by-step usage guide | 3:4 | KV usage-guide scene |

## Product Analysis (supportsAnalysis)

`scenario-set` jobs support AI photo analysis: the platform reads the uploaded photos with a vision model and pre-fills `productName`, `brandName`, and `productDetails` (selling points), plus per-slot-type presentation ideas that automatically enrich each slot's prompt. In the dashboard this runs automatically after upload. Via API/CLI, provide a complete brief (`-n`, `-d`, `-b`) instead — analysis is not required when the brief is filled in.

## Examples

```bash
# Full Amazon listing set (6 images) from three product angles
vibesku generate -t scenario-set \
  -n "Ultimate Omega Softgels" -b "Nordic Naturals" \
  -d "High-absorption fish oil, lemon flavor, 90 softgels" \
  -i front.jpg back.jpg side.jpg \
  -o '{
    "scenarioId": "amazon-pack",
    "slots": ["main", "angle-2", "angle-3", "lifestyle", "selling-points", "detail"]
  }'

# Taobao 主图五图 + 详情页三张（默认中文文案）
vibesku generate -t scenario-set \
  -n "智能保温杯" -d "12小时保温，LED 温显" -b "暖芯" \
  -i cup.jpg cup-side.jpg \
  -o '{
    "scenarioId": "taobao-pack",
    "slots": ["main-1", "main-2", "main-3", "main-4", "main-5", "detail-hero", "detail-lifestyle", "detail-painpoint"]
  }'

# Shopify storefront set with English copy at 4K
vibesku generate -t scenario-set \
  -n "Minimalist Desk Lamp" -i lamp.jpg \
  -o '{
    "scenarioId": "shopify-pack",
    "slots": ["banner", "main", "lifestyle-1", "detail", "callouts"],
    "imageSize": "4K"
  }'

# RED post set (cover + 3 inner images)
vibesku generate -t scenario-set \
  -n "氨基酸洗面奶" -i cleanser.jpg \
  -o '{
    "scenarioId": "red-pack",
    "slots": ["cover", "inner-lifestyle", "inner-detail", "inner-review"]
  }'

# Custom pick: just a white-bg main, an exploded infographic, and a usage guide
vibesku generate -t scenario-set \
  -n "RGB Gaming Keyboard" -i keyboard.jpg \
  -o '{
    "scenarioId": "custom-pack",
    "slots": ["white-bg-main", "exploded-infographic", "usage-guide"],
    "primaryLang": "en"
  }'
```

## Tips

- **Billing**: Each slot = 1 image = 1 credit (1K/2K) or 2 credits (4K). The Amazon pack at 2K costs 6 credits.
- **Regenerate one slot**: Each output is tagged with its slot id. To redo a single image, run `generate` again with `"slots": ["<slot-id>"]` on the same job, or use `vibesku refine <output-id>` for an edit instead of a redo.
- **Partial failure**: Slots fan out independently — if one slot fails to start, the rest still run and only successful slots are billed.
- **`primaryLang`** only affects slots that render on-image copy (posters/infographics); packshots and plain scenes are text-free.
- **Choosing between this and `kv-image-set`**: `kv-image-set` produces a stylistically unified vertical poster series for a detail page; `scenario-set` mixes engines (packshots + heroes + scenes + posters) to cover a platform's full image checklist.
