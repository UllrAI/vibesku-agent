# Template: creative-ad-video

Create a short absurdist commercial built around a real brand trait. The first call drafts a script and renders a storyboard. Review the panels and script before submitting the final MiniMax H3 video.

[Watch the VibeSKU example, Product Page ER](https://vibesku.com/examples/creative-ad-video/vibesku.mp4).

## Inputs and cost

- Provide a brand name and description, or at least one reference image or logo. Up to four product or style references and one logo are supported.
- Use `creativeDirection` for an optional creative premise, setting, or visual style. Avoid unsupported product claims.
- Script: 1 credit. Storyboard: 1 credit for each image.
- Video: 1–15 seconds, at 3 credits/second for 480p or 5 credits/second for 720p. Supports 9:16, 16:9, and 1:1 with native audio. Confirm the video cost before rendering.

## CLI workflow

```bash
vibesku generate -t creative-ad-video \
  -b "Example brand" -d "An insulated travel bottle that keeps drinks cool" \
  -o '{"creativeDirection":"An oddly formal award ceremony","durationSeconds":10,"resolution":"480p","aspectRatio":"9:16","spokenLang":"en"}' --json

vibesku status <job-id> --json
vibesku export <job-id> --output-dir ./storyboard-review

vibesku generate -t creative-ad-video --job <job-id> \
  -o '{"stage":"video","storyboardId":"<reviewed-image-output-id>"}' --json
```

Wait for the first run to succeed. The job contains `job.videoScript` and an IMAGE output whose `meta.storyboardKey` identifies its storyboard. Review the actual image and the script with the user. Use the image output ID as `storyboardId`, then track the second run to completion and export its VIDEO output. The API equivalent calls `POST /api/v1/generate` first with the brief or assets and then with the same `templateId` and `jobId`, omitting the brief and assets.

The continuation uses the saved script and the latest matching storyboard's render settings when omitted. Specify `aspectRatio` explicitly if reviewing an older storyboard for a different frame. Changing the frame requires a matching storyboard, and changing the brief, sources, duration, spoken language or direction requires a new script. To edit a script interactively, open the job in VibeSKU and redraw its storyboard before rendering. Redraw a storyboard for the same script via `--job <job-id> -o '{"stage":"storyboard"}'`.
