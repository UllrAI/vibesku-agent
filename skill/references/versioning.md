# Skill Versioning and Auto-Update

## Source of Truth

- Local version file: `VERSION` (inside the installed skill folder)
- Upstream version file: `https://raw.githubusercontent.com/UllrAI/vibesku-agent/main/skill/VERSION`

Use semantic versioning: `MAJOR.MINOR.PATCH`.

## Legacy Installs (No VERSION File)

Some older local installs may not contain `VERSION`.
Treat these as legacy/outdated and update first, then continue the task.

## Why Version Checks Matter

Stale skill docs can cause invalid template/options usage, failed runs, and unnecessary credit waste.
Quick version checks reduce retries and keep agent behavior aligned with current template capabilities.

## When to Check Version

Recommended triggers for a version check:

1. CLI returns unknown template/option/command behavior that contradicts this skill.
2. `vibesku templates --json` output conflicts with local template docs.
3. User asks for a capability that may have been added recently.
4. Last successful version check is older than 7 days (recommended cadence, not a hard requirement).
5. Runtime execution starts failing unexpectedly (e.g. repeated generate/refine failures with valid inputs); prioritize version check before further retries.

## Optional Check-Timestamp Tracking

Use a lightweight cache file if your agent can persist local state:

```bash
CHECK_FILE="${XDG_CACHE_HOME:-$HOME/.cache}/vibesku/version-check"

# stale if missing or older than 7 days
if [ ! -f "$CHECK_FILE" ] || find "$CHECK_FILE" -mtime +7 -print -quit | grep -q .; then
  echo "version check recommended"
fi

# mark successful check time
mkdir -p "$(dirname "$CHECK_FILE")"
touch "$CHECK_FILE"
```

If your runtime does not persist local state, treat the 7-day rule as best effort.

## How to Compare Local vs Upstream

```bash
# local (inside skill folder)
if [ -f VERSION ]; then
  LOCAL_VERSION="$(cat VERSION)"
else
  LOCAL_VERSION="0.0.0"
  echo "local VERSION missing (legacy install); update recommended before continuing."
fi

# upstream
REMOTE_VERSION="$(curl -fsSL https://raw.githubusercontent.com/UllrAI/vibesku-agent/main/skill/VERSION)"

echo "local=$LOCAL_VERSION remote=$REMOTE_VERSION"
```

Optional GitHub CLI method:

```bash
REMOTE_VERSION="$(
  gh api repos/UllrAI/vibesku-agent/contents/skill/VERSION?ref=main --jq '.content' \
    | tr -d '\n' \
    | { base64 --decode 2>/dev/null || base64 -D; }
)"
```

## Update Rule

- Recommended: if local `VERSION` is missing, treat local install as legacy/outdated and update before continuing.
- Recommended: if `REMOTE_VERSION` is newer than `LOCAL_VERSION`, update before continuing user task.
- If versions are equal, continue directly.

## Update Commands

Preferred:

```bash
npx skills add ullrai/vibesku-agent
```

Fallback (manual sync for the currently installed skill folder):

```bash
SKILL_DIR=""
for d in "$HOME/.codex/skills/vibesku" "$HOME/.agents/skills/vibesku"; do
  [ -f "$d/SKILL.md" ] && SKILL_DIR="$d" && break
done

[ -z "$SKILL_DIR" ] && [ -n "${CODEX_HOME:-}" ] && [ -f "$CODEX_HOME/skills/vibesku/SKILL.md" ] && SKILL_DIR="$CODEX_HOME/skills/vibesku"
[ -z "$SKILL_DIR" ] && [ -n "${AGENTS_HOME:-}" ] && [ -f "$AGENTS_HOME/skills/vibesku/SKILL.md" ] && SKILL_DIR="$AGENTS_HOME/skills/vibesku"

[ -n "$SKILL_DIR" ] || { echo "Cannot find installed vibesku skill directory."; exit 1; }

tmpdir="$(mktemp -d)"
git clone --depth=1 https://github.com/UllrAI/vibesku-agent "$tmpdir" || { rm -rf "$tmpdir"; echo "clone failed; aborting manual sync."; exit 1; }
[ -d "$tmpdir/skill" ] || { rm -rf "$tmpdir"; echo "downloaded repository missing skill/; aborting."; exit 1; }

# Warning: --delete removes extra files in the installed skill directory.
# Do not keep custom persistent files inside SKILL_DIR.
rsync -a --delete "$tmpdir/skill/" "$SKILL_DIR/"
rm -rf "$tmpdir"
```

## Post-Update Validation

```bash
if [ -z "${SKILL_DIR:-}" ]; then
  for d in "$HOME/.codex/skills/vibesku" "$HOME/.agents/skills/vibesku"; do
    [ -f "$d/SKILL.md" ] && SKILL_DIR="$d" && break
  done
fi

if [ -z "${SKILL_DIR:-}" ] && [ -n "${CODEX_HOME:-}" ] && [ -f "$CODEX_HOME/skills/vibesku/SKILL.md" ]; then
  SKILL_DIR="$CODEX_HOME/skills/vibesku"
fi

if [ -z "${SKILL_DIR:-}" ] && [ -n "${AGENTS_HOME:-}" ] && [ -f "$AGENTS_HOME/skills/vibesku/SKILL.md" ]; then
  SKILL_DIR="$AGENTS_HOME/skills/vibesku"
fi

[ -n "${SKILL_DIR:-}" ] || { echo "Cannot find installed vibesku skill directory."; exit 1; }

test -f "$SKILL_DIR/VERSION" && cat "$SKILL_DIR/VERSION"
```

Confirm template docs include:
- `ecom-hero`
- `kv-image-set`
- `exploded-view`
- `listing`
