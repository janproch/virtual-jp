---
name: vjp-update-virtual-jp
description: Refresh this repository's vendored copies of JP's virtual-jp skills - clone janproch/virtual-jp, remove the vjp-* entries under .claude/, copy in what its manifest.json lists, then commit and push the result on the repository's main branch. Use ONLY when the user explicitly asks for it ("update virtual JP", "update the virtual-jp skills", "use the virtual-jp update skill"). A request to update dependencies, packages or the project's own documentation is not an invocation, and neither is a complaint about how a vjp-* skill behaves.
---

# Update the vendored virtual-jp skills

Wholesale replacement from `https://github.com/janproch/virtual-jp`: delete every `vjp-*`
entry under `.claude/`, copy in what its `manifest.json` lists. There is no record of the
previous install - removal works purely by the `vjp-` name, so a dropped skill disappears.

## Rules

- Write only under `.claude/`, only paths the manifest names. Validate every entry before
  deleting anything; reject the whole manifest on any bad entry.
- Never run against a dirty, untracked or ignored `.claude/` - git is the only undo.
- Copy bytes as-is; never edit a copied file.
- One commit containing only `.claude/`, on the main branch, pushed. No `claude/*` branch,
  no PR, no amend, no force.
- This skill overwrites itself mid-run; the loaded instructions finish the run.

## 1. Main branch, clean `.claude/`

```bash
git rev-parse --show-toplevel        # not a repo - stop
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git status --porcelain               # must be empty to switch
git fetch origin --prune && git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
git status --porcelain --untracked-files=all -- .claude   # must be empty
git check-ignore --no-index -q .claude && echo IGNORED
git ls-files -- .claude | wc -l
```

`$MAIN` empty - `git remote set-head origin --auto`, else whichever of main/master exists
(ask if both); no remote - stay on the current branch, nothing to push. Never stash, reset
or force. Any `.claude/` output - list it and stop (a freshly bootstrapped, uncommitted copy
of this skill lands here: tell the user to commit it). `IGNORED` with 0 tracked files - stop,
`.claude/` must be tracked. (`--no-index` is required, else tracked paths hide the ignore.)

## 2. Clone and validate

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/janproch/virtual-jp "$tmp/virtual-jp"
git -C "$tmp/virtual-jp" rev-parse --short HEAD
```

Each `install` entry in `manifest.json` (`source` in the clone, `target` in this repo) must:
- `source`: relative, no `..`, exists;
- `target`: relative, starts with `.claude/`, no `..`;
- land every file under a `vjp-*` component directly inside a `.claude/` directory
  (`.claude/vjp-x` or `.claude/<dir>/vjp-x`): for target `.claude/<dir>` every immediate
  child of source is `vjp-*`; otherwise the target itself is `.claude/vjp-*` /
  `.claude/<dir>/vjp-*`.

Any failure - remove `$tmp`, report the entry, stop.

## 3. Sweep and copy

```bash
find .claude -maxdepth 2 -name 'vjp-*' -exec rm -rf {} +
mkdir -p "$(dirname <target>)"
cp -R "$tmp/virtual-jp/<source>/." "<target>/"   # directory entry
cp "$tmp/virtual-jp/<source>" "<target>"         # file entry
```

Remove `$tmp`; keep the list of files written.

## 4. Commit and push

```bash
git add -A -- .claude
git status --porcelain -- .claude
```

Empty output: run `git ls-files --error-unmatch -- <every written file>`. All tracked -
already up to date, no commit. Some unmatched - those paths are gitignored; stop and report
them. Otherwise:

```bash
git commit -m "chore: update virtual-jp skills to <short-sha>"
git push origin "$MAIN"
```

Rejected - fetch, `--ff-only`, push again; refused - stop and report.

## 5. Report

Installed virtual-jp commit; added/updated/removed paths (from the porcelain `A`/`M`/`D`)
and the unchanged count; the commit and that it was pushed, or "already up to date". If this
skill changed, the new version applies from the next run.
