# Template: ugc-video

**Purpose**: Turn product photos into a short vertical UGC-style shopping video with a spoken script — the kind of clip a creator would post to TikTok, Reels, or 抖音.

**When to use**: User wants a short-form product *video* (unboxing, try-on, demo, testimonial) rather than a still image. This is the only template that outputs VIDEO.

**Output type**: VIDEO | **Supports analysis**: No | **Cost**: **billed per second** — 480p = 3 credits/s, 720p = 5 credits/s

> ⚠️ **This template is far more expensive than any image template.** A 15-second 720p clip costs **75 credits**, versus 1-2 credits for a still. Always confirm duration and resolution with the user, and state the total cost, before running `vibesku generate`.
>
> Cost = `durationSeconds × rate(resolution)`. Credits are reserved before the job is submitted and refunded automatically if it fails.

## Model Limits (Prism MiniMax H3)

These are hard limits of the underlying model, not product choices:

- Duration: **1-15 whole seconds** (values outside the range are rejected)
- Resolution: **`480p` or `720p` only** — there is no 1080p tier
- Reference images: **at most 9** across PRODUCT + LOGO combined
- Audio is generated natively; the clip always has a soundtrack and there is no way to turn it off
- Video outputs **cannot be refined**. `vibesku refine` rejects them — generate a new clip instead

## Assets

| Role | Min | Max | Required |
|------|-----|-----|----------|
| PRODUCT (product images) | 1 | 8 | Yes |
| LOGO (brand mark) | 0 | 1 | No |

If more images are supplied than the model's nine-image budget allows, the logo is kept and the extra product angles are dropped (a truncation warning is attached to the run).

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `videoAngle` | string | `unboxing` | The creator angle the clip is shot from (see below) |
| `presenter` | string | `on-camera` | Who appears on screen (see below) |
| `tone` | string | `auto` | Delivery tone of the spoken script (see below) |
| `spokenLang` | string | `en` | Language the creator speaks |
| `hookLine` | string | – | Opening hook to build the first line around (≤200 chars) |
| `callToAction` | string | – | Closing call to action (≤120 chars) |
| `durationSeconds` | number | `10` | Clip length, 1-15 whole seconds. **Multiplies the cost.** |
| `resolution` | string | `720p` | `480p` (3 cr/s) or `720p` (5 cr/s) |
| `aspectRatio` | string | `9:16` | `9:16` (vertical, default), `1:1`, or `16:9` |

## Video Angle Options

| Value | Description | Best For |
|-------|-------------|----------|
| `unboxing` | Opens the packaging and reveals the product on camera | New launches, gift-able products, packaging that sells |
| `try-on` | Wears or uses the product and reacts to it | Apparel, beauty, wearables, anything worn |
| `demo` | Shows one concrete feature working, step by step | Gadgets, tools, appliances with a provable function |
| `testimonial` | Speaks to camera about the result they got | Supplements, skincare, services — outcome-led categories |
| `problem-solution` | Names a pain point, then the fix | Problem-aware categories: storage, cleaning, organisation |
| `street-style` | Handheld, on-location, caught-in-the-moment | Lifestyle goods, drinks, accessories, impulse buys |

## Presenter Options

| Value | Description | Best For |
|-------|-------------|----------|
| `on-camera` | A person speaks directly to the lens | Highest-trust format; testimonials and try-ons |
| `hands-only` | Hands operate the product, voice-over narrates | Unboxing and demos where the product is the star |
| `product-only` | No people, voice-over over b-roll | Brands that avoid depicting people, or ambiguous fit/skin tone |

## Tone Options

| Value | Description | Best For |
|-------|-------------|----------|
| `auto` | Match the tone to the product category and buyer | Default when the user has no preference |
| `energetic` | Fast, excited, high-tempo | Impulse buys, younger audiences |
| `warm` | Friendly, unhurried, like a friend's recommendation | Home, food, wellness |
| `expert` | Measured, specific, credibility-first | Technical products, higher price points |
| `deadpan` | Dry, understated, lets the product do the talking | Design-led goods, ironic/meme-aware audiences |

## Copy & Evidence Guidance

- The spoken script is written from the brief and the reference images. It will **not** state prices, discounts, delivery times, ratings, certifications, medical claims, or numeric performance figures unless those appear in the product details.
- No on-screen captions, subtitles, price tags, platform watermarks, or UI chrome are rendered.
- The product is reproduced from the references exactly; a logo is never invented. Supply the LOGO asset if branding must appear.

## Recommended Defaults by Goal

| Goal | Suggested Options |
|------|-------------------|
| Cheapest usable test clip | `{"durationSeconds":3,"resolution":"480p"}` — 9 credits |
| Standard TikTok/Reels post | `{"durationSeconds":10,"resolution":"720p","aspectRatio":"9:16"}` — 50 credits |
| Full-length hero clip | `{"durationSeconds":15,"resolution":"720p"}` — 75 credits |
| Budget-conscious full length | `{"durationSeconds":15,"resolution":"480p"}` — 45 credits |

## Examples

```bash
# Cheap 3-second test before committing to a full clip (9 credits)
vibesku generate -t ugc-video \
  -n "Stainless Steel Water Bottle" \
  -d "500ml insulated bottle, leak-proof cap, brushed metal finish" \
  -i bottle-front.jpg \
  -o '{"durationSeconds":3,"resolution":"480p"}'

# Standard vertical unboxing for TikTok (50 credits)
vibesku generate -t ugc-video \
  -n "Ceramic Aroma Diffuser" \
  -d "Ultrasonic diffuser, 8h runtime, matte ceramic shell" \
  -i diffuser-1.jpg diffuser-2.jpg -l brand-logo.png \
  -o '{"videoAngle":"unboxing","presenter":"hands-only","durationSeconds":10,"resolution":"720p","aspectRatio":"9:16"}'

# Chinese-language try-on with a specific hook (75 credits)
vibesku generate -t ugc-video \
  -n "羊毛混纺围巾" \
  -d "80% 羊毛，米色格纹，180cm" \
  -i scarf.jpg \
  -o '{"videoAngle":"try-on","presenter":"on-camera","tone":"warm","spokenLang":"zh-Hans","hookLine":"这条围巾我戴了一整个冬天","durationSeconds":15,"resolution":"720p"}'

# Problem-solution demo, no people on screen (30 credits)
vibesku generate -t ugc-video \
  -n "Under-Sink Organizer" \
  -i organizer.jpg \
  -o '{"videoAngle":"problem-solution","presenter":"product-only","tone":"expert","durationSeconds":10,"resolution":"480p"}'
```

## Tips

- **Quote the cost before running.** Multiply `durationSeconds` by 3 (480p) or 5 (720p) and tell the user the total.
- Prototype at `480p` and short durations, then re-run the settings that work at `720p`.
- `9:16` is the default because the output is aimed at vertical feeds; only switch to `16:9` if the user names a landscape destination.
- `hookLine` is the highest-leverage field — short-form viewers leave within the first second. Supply one when the user has a known selling angle.
- Generation takes roughly 4 minutes regardless of clip length; use `--watch` rather than polling by hand.
- If the user wants to tweak a finished clip, there is no refine path — adjust the options and generate again (which costs full price).
