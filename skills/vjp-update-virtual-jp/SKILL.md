---
name: vjp-update-virtual-jp
description: Refresh this repository's vendored copies of JP's virtual-jp skills - clone janproch/virtual-jp, remove the vjp-* entries under .claude/, copy in what its manifest.json lists, then commit and push the result on the repository's main branch. Use ONLY when the user explicitly asks for it ("update virtual JP", "update the virtual-jp skills", "use the virtual-jp update skill"). A request to update dependencies, packages or the project's own documentation is not an invocation, and neither is a complaint about how a vjp-* skill behaves.
---

# Update the vendored virtual-jp skills

This skill refreshes the copies of JP's `vjp-*` skills that live in **this** repository's
`.claude/` directory, from `https://github.com/janproch/virtual-jp`.

The update is a wholesale replacement, not a merge: clone the repository, delete every
`vjp-*` entry under `.claude/`, then copy in what `manifest.json` lists. That manifest
names the directories and files to copy and where each one lands - nothing else. It
carries no checksums and no file inventory, so a skill added or renamed in virtual-jp
needs no change to it.

The calling repository keeps **no record** of a previous update - no lock file, no
receipt. Removal works by name instead: everything virtual-jp ships is named `vjp-*`
directly inside a `.claude/` directory, so sweeping those entries and copying the
manifest's sources back is what makes a dropped skill disappear.

## Hard rules

- **Explicit invocation only.** The user names virtual-jp and asks for it to be updated.
  A stale skill you happened to notice is not an invocation.
- **Copy only what the manifest lists**, and never write outside `.claude/`. Validate
  every entry before deleting anything, and reject the manifest as a whole rather than
  skipping a bad entry.
- **Never run against a dirty, untracked or ignored `.claude/`.** The sweep deletes
  without asking and git is the only undo. No force flag - a user who wants to proceed
  commits or discards their work first.
- **Never edit a file after copying it.** What is written is what the clone holds, byte
  for byte. A problem with a skill's contents is a change to make in virtual-jp.
- **One commit, on the main branch.** The update is a single commit containing only
  `.claude/`, made and pushed on the repository's main branch - never a `claude/*`
  branch, never a pull request. Copying files out of a clone is not a change anybody
  reviews, and a branch only delays skills the user has just asked for. Never amend,
  never force.

This skill is itself shipped by the manifest, so its own file is overwritten mid-run.
The instructions already loaded finish the run; a changed procedure takes effect the
next time the skill is invoked.

## 1. Establish the calling repository, on its main branch

```bash
git rev-parse --show-toplevel
```

Not a git repository - stop and say so. Git is a precondition, not a convenience: step 4
deletes files and `git checkout` is the only way back. Run every path below from that
root.

The update belongs on the repository's main branch, where every session that vendors
these skills reads them, so get there before anything is written:

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git fetch origin --prune
git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
```

If `$MAIN` comes back empty, try `git remote set-head origin --auto`, else fall back to
whichever of `origin/main` / `origin/master` exists - and ask the user if both do. Use
whatever `git remote` reports if it is not `origin`. A repository with no remote at all
has one branch to work on, the one it is on, and step 6 has nothing to push to.

Leaving another branch needs a clean tree: if `git status --porcelain` reports anything,
stop and say the update lands on the main branch and the checkout has work in progress.
Stop and report too if a merge or rebase is in progress or the fast-forward is refused.
Never stash, reset or force on your own initiative. If the session started on another
branch, say so in the report: it stays on the main branch afterwards.

## 2. Refuse unless `.claude/` is clean and tracked

```bash
git status --porcelain --untracked-files=all -- .claude
```

Any output at all - stop, list the paths, and explain that the update deletes and
overwrites `.claude/` and needs a clean tree so the change is reviewable and revertable.
Whether to commit or discard that work is the user's call; do not make it for them.

On a repository that has just been bootstrapped, the freshly downloaded copy of this
skill is itself untracked and lands here. Say so plainly and point at committing it -
the bootstrap command in the virtual-jp README does that in the same line.

A repository that ignores `.claude/` and has never committed it reports a **clean** tree
above - there is nothing for git to report - so that check passes and this one is what
stands between the sweep and an unrecoverable delete:

```bash
git check-ignore --no-index -q .claude && echo IGNORED
git ls-files -- .claude | wc -l
```

Ignored **and** nothing tracked - stop. The sweep would still delete, but git holds no
copy, the commit would be empty and there is no way back. Say that `.claude/` is
gitignored and that the update needs it tracked.

Ignored but with tracked files under it - proceed. The tracked files keep being tracked
whatever `.gitignore` says, so the undo exists; step 6 catches what the ignore rule would
swallow.

`--no-index` is not optional here: without it git stays silent about any path that is
already tracked, which hides exactly the repositories this check exists for.

## 3. Clone virtual-jp and read its manifest

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/janproch/virtual-jp "$tmp/virtual-jp"
git -C "$tmp/virtual-jp" rev-parse --short HEAD
```

Always the default branch, always the latest commit on it. There is no ref argument and
no pinning; the short commit is what the commit message records.

Read `$tmp/virtual-jp/manifest.json`. Its `install` list holds one entry per directory or
file to copy, each with a `source` relative to the clone and a `target` relative to the
calling repository. Check **every** entry before touching anything:

- `source` is relative, has no `..` component, and exists in the clone
- `target` starts with `.claude/`, is relative, and has no `..` component
- copying `source` to `target` puts every file under a `vjp-` prefixed component directly
  inside a `.claude/` directory - that is `.claude/vjp-<something>` or
  `.claude/<dir>/vjp-<something>`. For a directory entry that means each of its immediate
  children is named `vjp-*` when `target` is `.claude/<dir>`, or the directory itself is
  when `target` is `.claude/vjp-<dir>`.

That last rule is what keeps the next update able to remove what this one writes: step 4
sweeps by name and by name alone, so a file landing outside a `vjp-*` entry could never
be removed again.

Anything fails - remove `$tmp`, stop, and report which entry and why. Nothing has been
deleted at that point, which is the reason this check comes first.

## 4. Sweep

```bash
find .claude -maxdepth 2 -name 'vjp-*'
```

Remove every result. Depth 1 and 2 only, which is exactly the range the naming rule
covers. This is the whole removal mechanism: a skill virtual-jp has dropped is not in the
clone, so it is not copied back, so it is gone.

## 5. Copy

For each manifest entry, create the target's parent directory and copy `source` to
`target` - a directory entry with everything under it:

```bash
mkdir -p "$(dirname <target>)"
cp -R "$tmp/virtual-jp/<source>/." "<target>/"   # directory entry
cp "$tmp/virtual-jp/<source>" "<target>"         # file entry
```

Preserve the bytes; do not reformat, re-indent or fix anything on the way. Skip nothing
in the source directory - what the clone holds under it is what the repository ships.

Remove `$tmp` once every entry is copied. Keep the list of files written: step 6 needs it.

## 6. Commit and push

```bash
git add -A -- .claude
git status --porcelain -- .claude
```

Empty output has two meanings, so separate them before believing it. Check that git
actually tracks what was copied, passing every file written in step 5:

```bash
git ls-files --error-unmatch -- <file> [<file>...]
```

All tracked - the clone matched what was already installed. Report "already up to date"
at the source commit and stop; no commit is made.

Any file unmatched - `.claude/` is partly ignored. The file is on disk and git will never
record it, so the update is not recoverable and not reviewable. Stop and report which
paths are ignored. Do not report the repository as up to date.

Otherwise commit that path alone:

```bash
git commit -m "chore: update virtual-jp skills to <short-sha>"
```

Nothing else goes into this commit. Then put it where the repositories that vendor
these skills will read it:

```bash
git push origin "$MAIN"
```

Rejected - `git fetch origin`, `git merge --ff-only "origin/$MAIN"`, then push again; if
that fast-forward is refused, stop and report, leaving the commit where it is. Never
force. Where there is no remote, the commit is the end of the run and the report says so.

## 7. Report

Read the statuses from the `git status --porcelain` output of step 6 - `A` added, `M`
updated, `D` removed - and report:

- the virtual-jp commit installed
- what was added, updated and removed, by path, and how many files were unchanged
- the commit that was made and that it was pushed, or that the repository was already
  up to date

If this skill's own file is among the changes, say that the new version of the update
procedure applies from the next invocation, not this one.
