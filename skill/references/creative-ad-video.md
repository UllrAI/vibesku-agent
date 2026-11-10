# Template: creative-ad-video

Create a short absurdist commercial built around a real brand trait. The first call drafts a script and renders a storyboard. Review the panels and script before submitting the final MiniMax H3 video.

[Watch the VibeSKU example, Product Page ER](https://vibesku.com/templates/absurdist-brand-video).

## Inputs and cost

- Provide a brand name and description, or at least one reference image or logo. Up to four product or style references and one logo are supported.
- Leave `creativeDirection` blank for VibeSKU to invent the premise, or provide up to 500 characters of story and visual guidance. The script and storyboard both use this direction. For example, combine an emergency-room setup with plush stop-motion, colorful 2D animation, or a realistic live-action look. Avoid unsupported product claims.
- Script: 1 credit. Storyboard: 1 credit for each image.
- Video: 10–15 whole seconds, default 10, at 3 credits/second for 480p or 5 credits/second for 720p. Choose portrait (9:16, default), landscape (16:9), or square (1:1), all with native audio. Confirm the video cost before rendering.

In the web workspace, choose the video orientation under Look and output. The primary action advances from script to storyboard to video. The results area has separate Script, Storyboard, and Video tabs. It opens the running stage or the most recent output by default. Review the script and storyboard at each stage, and use the redraw action next to the storyboard preview to replace it.

## CLI workflow

```bash
vibesku generate -t creative-ad-video \
  -b "Example brand" -d "An insulated travel bottle that keeps drinks cool" \
  -o '{"creativeDirection":"An oddly formal award ceremony filmed with plush stop-motion characters","durationSeconds":12,"resolution":"480p","aspectRatio":"9:16","spokenLang":"en"}' --json

vibesku status <job-id> --json
vibesku export <job-id> --output-dir ./storyboard-review

vibesku generate -t creative-ad-video --job <job-id> \
  -o '{"stage":"video","storyboardId":"<reviewed-image-output-id>"}' --json
```

Wait for the first run to succeed. The job contains `job.videoScript` and an IMAGE output whose `meta.storyboardKey` identifies its storyboard. Review the actual image and the script with the user. Use the image output ID as `storyboardId`, then track the second run to completion and export its VIDEO output. The API equivalent calls `POST /api/v1/generate` first with the brief or assets and then with the same `templateId` and `jobId`, omitting the brief and assets.

The continuation uses the saved script and the latest matching storyboard's render settings when omitted. Specify `aspectRatio` explicitly if reviewing an older storyboard for a different frame. Changing the frame requires a matching storyboard, and changing the brief, sources, duration, spoken language or direction requires a new script. To edit a script interactively, open the job in VibeSKU and redraw its storyboard before rendering. Redraw a storyboard for the same script via `--job <job-id> -o '{"stage":"storyboard"}'`.
