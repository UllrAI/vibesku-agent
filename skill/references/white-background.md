# Template: white-background

**Purpose**: Generate a single clean product packshot on a seamless white background for ecommerce listings, catalogs, and marketplace main images.

**When to use**: User needs a clean white-background product image with minimal styling and no extra scene context.

**Output type**: IMAGE | **Supports analysis**: No | **Cost**: 1K/2K = 1 credit, 4K = 2 credits

## Assets

| Role | Min | Max | Required |
|------|-----|-----|----------|
| PRODUCT (product images) | 1 | 10 | Yes |

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backgroundTone` | string | `pure-white` | White background treatment (see below) |
| `shadowStyle` | string | `soft` | Grounding shadow intensity (see below) |
| `cropMode` | string | `full-product` | Product framing strategy (see below) |
| `aspectRatio` | string | `1:1` | Output ratio, typically `1:1`, `4:5`, or `3:4` |
| `imageSize` | string | `2K` | Resolution: `1K`, `2K`, or `4K` |

## Background Tone Options

| Value | Description | Best For |
|-------|-------------|----------|
| `pure-white` | Crisp seamless white background with even lighting | Marketplace main images, strict catalog standards |
| `soft-white` | Soft white backdrop with faint tonal falloff | Premium packshots that still need clean listing compliance |

## Shadow Style Options

| Value | Description | Best For |
|-------|-------------|----------|
| `none` | Minimal or no visible shadow | Very strict marketplace crops or flat catalog looks |
| `soft` | Soft grounding shadow | Default choice for most ecommerce packshots |
| `natural` | Stronger studio shadow with realistic depth | Premium catalog visuals that need more dimensionality |

## Crop Mode Options

| Value | Description | Best For |
|-------|-------------|----------|
| `full-product` | Keep the whole product comfortably in frame | Marketplace main image compliance |
| `balanced` | Product fills more of the canvas with clean margins | Standard catalog use |
| `close-up` | Tighter framing while preserving key details | Secondary listing images or tighter thumbnail crops |

## Recommended Defaults by Goal

| Goal | Suggested Options |
|------|-------------------|
| Marketplace main image | `{"backgroundTone":"pure-white","shadowStyle":"soft","cropMode":"full-product"}` |
| Premium catalog packshot | `{"backgroundTone":"soft-white","shadowStyle":"natural","cropMode":"balanced"}` |
| Tight thumbnail crop | `{"backgroundTone":"pure-white","shadowStyle":"none","cropMode":"close-up"}` |

## Examples

```bash
# Default white-background packshot
vibesku generate -t white-background \
  -n "Stainless Steel Water Bottle" \
  -d "500ml insulated bottle, leak-proof cap, brushed metal finish" \
  -i bottle-front.jpg bottle-side.jpg

# Strict marketplace main image
vibesku generate -t white-background \
  -n "Wireless Mouse" \
  -i mouse.jpg \
  -o '{"backgroundTone":"pure-white","shadowStyle":"soft","cropMode":"full-product","aspectRatio":"1:1"}'

# Softer premium packshot
vibesku generate -t white-background \
  -n "Ceramic Aroma Diffuser" \
  -i diffuser.jpg \
  -o '{"backgroundTone":"soft-white","shadowStyle":"natural","cropMode":"balanced","aspectRatio":"4:5"}'

# Tight thumbnail-style crop
vibesku generate -t white-background \
  -n "Lip Balm Set" \
  -i lip-balm.jpg \
  -o '{"backgroundTone":"pure-white","shadowStyle":"none","cropMode":"close-up","aspectRatio":"3:4"}'
```

## Tips

- Use this template when the user explicitly wants white-background listing images rather than styled hero visuals.
- It does **not** run an analysis step, so generation starts immediately after upload.
- `pure-white` is the safest default for marketplace compliance.
- `soft-white` helps avoid a sterile look while keeping the image catalog-ready.
- Provide multiple product angles in `-i` when reflections, labels, or packaging details must stay precise.
