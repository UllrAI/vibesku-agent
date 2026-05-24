# Template: lifestyle-scene

**Purpose**: Place a product into a realistic usage scene with optional props, hands, or a full figure while preserving product fidelity.

**When to use**: User wants one product photo rendered in a believable real-life environment rather than a poster, exploded infographic, or white-background packshot.

**Output type**: IMAGE | **Supports analysis**: No | **Cost**: 1K/2K = 1 credit, 4K = 2 credits

## Assets

| Role | Min | Max | Required |
|------|-----|-----|----------|
| PRODUCT (product images) | 1 | 5 | Yes |
| LOGO (brand logo) | 0 | 1 | No |

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scenePreset` | string | `auto` | Scene setting: `auto`, `kitchen`, `outdoor`, `cafe`, `bedroom`, `office`, `gym`, `beach`, `gallery`, or `custom` |
| `customScene` | string | — | Free-form scene description, used when `scenePreset=custom` |
| `timeOfDay` | string | `auto` | Lighting mood: `auto`, `morning`, `golden-hour`, `evening`, or `studio-light` |
| `propsEnabled` | boolean | `true` | Allow tasteful supporting props |
| `personMode` | string | `none` | People handling: `none`, `hand-only`, or `full-figure` |
| `aspectRatio` | string | `1:1` | Output ratio, such as `1:1`, `4:5`, `16:9`, or `9:16` |
| `imageSize` | string | `2K` | Resolution: `1K`, `2K`, or `4K` |
| `style` | string | `auto` | Visual style: `auto`, `studio`, `lifestyle`, `premium`, `minimal`, `vibrant`, `tech`, `organic`, or `custom` |
| `customStyle` | string | — | Free-text style description, used when `style=custom` |

## Scene Presets

| Preset | Best For |
|--------|----------|
| `auto` | Let the model infer the most natural scene from product category and brief |
| `kitchen` | Food, cookware, cleaning, home utility products |
| `outdoor` | Travel, sports, garden, pet, and rugged products |
| `cafe` | Beverage, snack, stationery, lifestyle accessories |
| `bedroom` | Sleep, wellness, fragrance, textile, home comfort products |
| `office` | Electronics, stationery, productivity, desk accessories |
| `gym` | Fitness, supplement, sports, recovery products |
| `beach` | Summer, travel, swim, sunscreen, outdoor leisure products |
| `gallery` | Design objects, luxury, artful or minimal products |
| `custom` | User provides a precise setting in `customScene` |

## Copy & Evidence Guidance

- The image model directly inspects uploaded product photos, logo, packaging, visible text, material, color, and the written brief during generation. No separate analysis step is required.
- Make the result a concrete use moment, not a generic product-on-table packshot.
- Supporting props should clarify category, use case, or buyer mood; omit props that imply unsupported ingredients, bundled accessories, or product claims.
- If people are enabled, hands or figures must feel natural and remain secondary to the product.
- Hard factual claims require explicit support from the brief or readable/visible evidence. Never invent specs, certifications, awards, ratings, compatibility, medical/safety claims, or regulated benefits.

## Recommended Defaults by Goal

| Goal | Suggested Options |
|------|-------------------|
| Safe lifestyle upgrade | `{"scenePreset":"auto","personMode":"none","style":"lifestyle"}` |
| Hand interaction shot | `{"scenePreset":"auto","personMode":"hand-only","propsEnabled":true}` |
| Premium interior mood | `{"scenePreset":"gallery","timeOfDay":"studio-light","style":"premium"}` |
| Food or beverage scene | `{"scenePreset":"cafe","timeOfDay":"morning","style":"lifestyle"}` |

## Examples

```bash
# Let the model infer the scene
vibesku generate -t lifestyle-scene \
  -n "Insulated Travel Mug" \
  -d "Leak-resistant lid, powder-coated finish, fits car cup holders" \
  -b "TrailCup" \
  -i mug-front.jpg mug-detail.jpg \
  -o '{"scenePreset":"auto","style":"lifestyle","personMode":"none"}'

# Hand interaction in a cafe scene
vibesku generate -t lifestyle-scene \
  -n "Ceramic Coffee Dripper" \
  -i dripper.jpg \
  -o '{"scenePreset":"cafe","personMode":"hand-only","timeOfDay":"morning","aspectRatio":"4:5"}'

# Custom scene direction
vibesku generate -t lifestyle-scene \
  -n "Minimal Desk Lamp" \
  -i lamp.jpg \
  -o '{"scenePreset":"custom","customScene":"quiet architect desk with walnut surface and soft evening light","style":"premium","aspectRatio":"16:9"}'
```

## Tips

- Use `scenePreset=auto` when the product category is clear and the user does not have a specific location in mind.
- Use `customScene` only for concise, concrete settings; keep it under 200 characters.
- Use `personMode=hand-only` for interaction or scale; use `full-figure` only when the user explicitly wants a person-led lifestyle image.
- Use `white-background` instead when marketplace compliance or clean catalog output matters more than context.
