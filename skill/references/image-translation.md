# Template: image-translation

**Purpose**: Translate visible text inside an existing product image, poster, or marketing graphic while preserving the original layout and visual style.

**When to use**: User already has a finished image/poster and wants the text localized into another language without redesigning the asset from scratch.

**Output type**: IMAGE | **Supports analysis**: No | **Cost**: 1K/2K = 1 credit, 4K = 2 credits

## Assets

| Role | Min | Max | Required |
|------|-----|-----|----------|
| PRODUCT (source image/poster) | 1 | 1 | Yes |

Use `-i` for the source image. Do not pass a separate logo unless the API template metadata later adds a LOGO role.

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `targetLang` | string | `en` | Target language code, such as `zh-Hans`, `ja`, `ko`, `en`, `fr`, `de`, `es`, `pt`, or `it` |
| `translationMode` | string | `faithful` | Translation style: `faithful` or `polished` |
| `brandTextMode` | string | `preserve` | Brand-side text handling: `preserve` or `translate` |
| `aspectRatio` | string | `auto` | Output ratio. Use `auto` to preserve source shape when supported |
| `imageSize` | string | `2K` | Resolution: `1K`, `2K`, or `4K` |

## Translation Mode Options

| Value | Description | Best For |
|-------|-------------|----------|
| `faithful` | Translate text as directly as possible while preserving meaning, hierarchy, numbers, and layout | Compliance-sensitive posters, claims, labels |
| `polished` | Translate and lightly polish copy so it reads naturally in the target language | Marketing posters, social creatives, ads |

## Brand Text Mode Options

| Value | Description | Best For |
|-------|-------------|----------|
| `preserve` | Keep brand names, logo artwork, trademarks, model numbers, SKU codes, barcodes, QR codes, certifications, and legal marks unchanged | Default and safest choice |
| `translate` | Translate normal readable brand-side marketing copy while preserving logos/trademarks and machine-readable codes | Posters where brand-side slogans also need localization |

## Examples

```bash
# Translate a poster to Simplified Chinese, preserving brand text
vibesku generate -t image-translation \
  -i poster-en.jpg \
  -o '{"targetLang":"zh-Hans","translationMode":"faithful","brandTextMode":"preserve","aspectRatio":"auto"}'

# Translate a Japanese product image to English with polished marketing copy
vibesku generate -t image-translation \
  -i product-ja.jpg \
  -o '{"targetLang":"en","translationMode":"polished","brandTextMode":"preserve"}'

# Translate normal brand-side copy, while still preserving logos and codes
vibesku generate -t image-translation \
  -i campaign.jpg \
  -o '{"targetLang":"fr","translationMode":"polished","brandTextMode":"translate","imageSize":"4K"}'
```

## Tips

- Use this template only when the source image already contains text that needs localization.
- For new posters from product photos, use `ecom-hero` or `kv-image-set` instead.
- Keep `brandTextMode: preserve` unless the user explicitly asks to translate brand-side slogans or campaign copy.
- Use `aspectRatio: auto` for existing posters/screenshots so the output keeps the source shape.
- Use `translationMode: faithful` for packaging claims, measurements, prices, or regulated text.
