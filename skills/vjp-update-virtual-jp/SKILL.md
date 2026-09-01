---
name: vjp-update-virtual-jp
description: Refresh this repository's vendored copies of JP's virtual-jp skills - clone janproch/virtual-jp, install every file its index.json ships into .claude/, remove the vjp-* entries it no longer ships, then commit and push the result on the main branch. Use ONLY when the user explicitly asks for it ("update virtual JP", "update the virtual-jp skills", "use the virtual-jp update skill"). A request to update dependencies, packages or the project's own documentation is not an invocation, and neither is a complaint about how a vjp-* skill behaves.
---

# Update the vendored virtual-jp skills

This skill refreshes the copies of JP's `vjp-*` skills that live in **this** repository's
`.claude/` directory, from `https://github.com/janproch/virtual-jp`.

`index.json` in that repository is the only authority on what gets installed and where.
A file that is in the clone but not in the manifest is not installed; a file that is in
the manifest is installed exactly at the target path the manifest gives it.

The calling repository keeps **no record** of a previous update - no lock file, no
receipt. Removal works by name instead: everything virtual-jp ships is named `vjp-*`
directly inside a `.claude/` directory, so sweeping those entries - and the `jp-*` ones
an older virtual-jp shipped under - and writing the manifest back is what makes a dropped
skill disappear.

## Hard rules

- **Explicit invocation only.** The user names virtual-jp and asks for it to be updated.
  A stale skill you happened to notice is not an invocation.
- **Never install a file the manifest does not name**, and never write outside `.claude/`.
  Validate the whole manifest before deleting anything, and reject it as a whole rather
  than skipping a bad entry.
- **Never run against a dirty, untracked or ignored `.claude/`.** The sweep deletes
  without asking and git is the only undo. No force flag - a user who wants to proceed
  commits or discards their work first.
- **Never edit a file after installing it.** What is written is what the manifest ships,
  byte for byte. A problem with a skill's contents is a change to make in virtual-jp.
- **The main branch, and nothing else.** The update runs on the main branch and pushes
  there - never a `claude/*` branch, never a pull request. Installing files the manifest
  hashes is not a change anybody reviews, and a branch only delays skills the user has
  just asked for. Never amend, never force-push.

This skill is itself shipped by the manifest, so its own file is overwritten mid-run.
The instructions already loaded finish the run; a changed procedure takes effect the
next time the skill is invoked.

## 1. Establish the calling repository

```bash
git rev-parse --show-toplevel
```

Not a git repository - stop and say so. Git is a precondition, not a convenience: step 5
deletes files and `git checkout` is the only way back. Run every path below from that
root.

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
whatever `.gitignore` says, so the undo exists; step 8 catches what the ignore rule would
swallow.

`--no-index` is not optional here: without it git stays silent about any path that is
already tracked, which hides exactly the repositories this check exists for.

## 3. Get on the main branch

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git switch "$MAIN"
git pull --ff-only
```

Empty `MAIN` - try `git remote set-head origin --auto`, else fall back to whichever of
`origin/main` / `origin/master` exists, and ask the user if both do. Use whatever
`git remote` reports if it is not `origin`.

Switch or fast-forward refused - stop and say why. Never stash, reset or force to get
there. If the session was on another branch, say so in the report: it stays on the main
branch afterwards.

## 4. Fetch the manifest

```bash
tmp=$(mktemp -d)
git clone --depth 1 https://github.com/janproch/virtual-jp "$tmp/virtual-jp"
git -C "$tmp/virtual-jp" rev-parse --short HEAD
```

Always the default branch, always the latest commit on it. There is no ref argument and
no pinning; the short commit is what the commit message records.

Read `$tmp/virtual-jp/index.json` and check **every** entry before touching anything:

- `target` starts with `.claude/`, is relative, and has no `..` component
- `target` has a `vjp-` prefixed component directly inside a `.claude/` directory - that
  is `.claude/vjp-<something>` or `.claude/<dir>/vjp-<something>`
- `source` exists in the clone

Anything fails - remove `$tmp`, stop, and report which entry and why. Nothing has been
deleted at that point, which is the reason this check comes first.

## 5. Sweep

```bash
find .claude -maxdepth 2 \( -name 'vjp-*' -o -name 'jp-*' \)
```

Remove every result. Depth 1 and 2 only, which is exactly the range the naming rule
covers. This is the whole removal mechanism: a skill virtual-jp has dropped is not in the
manifest, so it is not written back, so it is gone.

The `jp-*` half of that pattern is the legacy namespace: virtual-jp shipped these skills
under `jp-*` before the rename to `vjp-*`. A repository vendored back then still carries
those directories, and nothing in the new manifest overwrites them, so the sweep is the
only thing that stops the old copy of a skill sitting beside its renamed twin. Keep the
pattern until no vendored repository can still be on the old names.

## 6. Install

For each manifest entry, create the target's parent directory and copy `source` to
`target`. Preserve the bytes; do not reformat, re-indent or fix anything on the way.

## 7. Verify what was written

Hash each installed target and compare it to the entry's `sha256`. A mismatch or a
missing file stops the run: report it and leave the working tree as it is so the user
can look, noting that `git checkout -- .claude` restores the previous state. Remove
`$tmp` either way.

## 8. Commit and push

```bash
git add -A -- .claude
git status --porcelain -- .claude
```

Empty output has two meanings, so separate them before believing it. Check that git
actually tracks what was installed, passing every target from the manifest:

```bash
git ls-files --error-unmatch -- <target> [<target>...]
```

All tracked - the manifest matched what was already installed. Report "already up to
date" at the source commit and stop; no commit is made.

Any target unmatched - `.claude/` is partly ignored. The file is on disk and git will
never record it, so the update is not recoverable and not reviewable. Stop and report
which targets are ignored. Do not report the repository as up to date.

Otherwise commit that path alone:

```bash
git commit -m "chore: update virtual-jp skills to <short-sha>"
git push
```

Nothing else goes into that commit, and it goes to the main branch as it is - no branch,
no pull request, nothing to confirm. Push rejected because the main branch moved:
`git pull --ff-only` and push again. Rejected because the repository protects its main
branch: say so and leave the commit local.

## 9. Report

Read the statuses from the `git status --porcelain` output of step 8 - `A` added, `M`
updated, `D` removed - and report:

- the virtual-jp commit installed, and the manifest version
- what was added, updated and removed, by path, and how many files were unchanged
- the commit that was made and pushed, or that the repository was already up to date

If this skill's own file is among the changes, say that the new version of the update
procedure applies from the next invocation, not this one.
