# Skill Versioning and Auto-Update

## Source of Truth

- Local version file: `VERSION`
- Upstream version file: `https://raw.githubusercontent.com/UllrAI/vibesku-agent/main/skill/VERSION`

Use semantic versioning: `MAJOR.MINOR.PATCH`.

## When to Check Version

Run a version check when any of the following is true:

1. CLI returns unknown template/option/command behavior that contradicts this skill.
2. `vibesku templates --json` output conflicts with local template docs.
3. User asks for a capability that may have been added recently.
4. Last successful version check is older than 7 days.

## How to Compare Local vs Upstream

```bash
# local (inside skill folder)
LOCAL_VERSION="$(cat VERSION)"

# upstream
REMOTE_VERSION="$(curl -fsSL https://raw.githubusercontent.com/UllrAI/vibesku-agent/main/skill/VERSION)"

echo "local=$LOCAL_VERSION remote=$REMOTE_VERSION"
```

Optional GitHub CLI method:

```bash
REMOTE_VERSION="$(gh api repos/UllrAI/vibesku-agent/contents/skill/VERSION?ref=main --jq '.content' | base64 --decode)"
```

## Update Rule

- If `REMOTE_VERSION` is newer than `LOCAL_VERSION`, update first, then continue user task.
- If versions are equal, continue directly.

## Update Commands

Preferred:

```bash
npx skills add ullrai/vibesku-agent
```

Fallback (manual sync for local skill folder):

```bash
tmpdir="$(mktemp -d)"
git clone --depth=1 https://github.com/UllrAI/vibesku-agent "$tmpdir"
rsync -a --delete "$tmpdir/skill/" "$HOME/.codex/skills/vibesku/"
```

## Post-Update Validation

```bash
test -f "$HOME/.codex/skills/vibesku/VERSION" && cat "$HOME/.codex/skills/vibesku/VERSION"
```

Confirm template docs include:
- `ecom-hero`
- `kv-image-set`
- `exploded-view`
- `listing`
