---
name: vjp-reintegrate-master
description: Merge the freshly fetched main branch (master/main, whatever the repository uses) into the current feature branch, resolve the conflicts, verify the result and commit the merge. Never pushes. Use ONLY when the user explicitly asks for it ("reintegrate master", "reintegrate the main branch", "catch this branch up with master", "sync with master", "use the reintegrate master skill"). A branch that merely looks behind, a pull request that needs updating, or a request to rebase, squash or push is not an invocation.
---

# Reintegrate the main branch into the current branch

This skill brings the current feature branch up to date with the **freshly fetched**
main branch, resolves whatever conflicts that produces, and lands it as a merge
commit on the feature branch.

The direction is always `main -> current branch`. This skill never pushes and never
commits to the main branch itself.

Nothing here assumes a particular project, branch name or build tool - take those
from the repository's own instructions.

## 1. Find the main branch, on a clean checkout

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git rev-parse --abbrev-ref HEAD
git status --porcelain                  # must be empty
git rev-parse -q --verify MERGE_HEAD    # must print nothing
```

If `$MAIN` comes back empty, try `git remote set-head origin --auto`, else fall back
to whichever of `origin/main` / `origin/master` exists - and ask the user if both do.
Use whatever `git remote` reports if it is not `origin`.

Stop and report if the tree is dirty, or a merge/rebase/cherry-pick is already in
progress (`MERGE_HEAD`, `.git/rebase-merge`, `.git/rebase-apply`). Do not stash on
your own initiative - a half-finished edit folded into a merge resolution is
unrecoverable. If HEAD **is** the main branch or a release branch, stop: there is
nothing to reintegrate.

## 2. Fetch, so "main" means the updated main

```bash
git fetch origin "$MAIN"
git log --oneline "HEAD..origin/$MAIN"
```

Always merge `origin/$MAIN`, never the local ref - the local one is usually stale and
produces a branch that looks reintegrated but is not. (The exception is a caller like
`vjp-merge-claude-branches` that has just advanced the local branch itself; then merge
that.) If the log is empty the branch is already up to date - say so and stop.

## 3. Merge and resolve

```bash
git merge --no-ff --no-edit "origin/$MAIN"
git diff --name-only --diff-filter=U
```

No conflicts means the merge commit already exists - go to step 4. Otherwise resolve
each file by hand:

- **Keep both intentions.** A conflict is two real changes meeting; the resolution is
  almost never "take ours" or "take theirs" wholesale. Read the commits behind each
  side (`git log --oneline "HEAD..origin/$MAIN" -- <file>` and the reverse) when the
  hunk alone does not explain the intent.
- **Never leave a conflict marker.** After resolving, run `git diff --check` and grep
  the resolved files for leftover marker lines.
- **Regenerate generated files** - lockfiles, bundled or code-generated artifacts,
  extracted string catalogs - from the resolved inputs rather than hand-merging them,
  then stage the result.
- **Honour the invariants this repository documents.** A conflict is exactly where
  paired or generated definitions drift apart, so re-read the project's `CLAUDE.md` /
  `AGENTS.md` / contributing docs for the rules covering the files you just touched.
- `git checkout --ours/--theirs <file>` is fine for a file wholly owned by one side,
  never as a shortcut for source code.

Stage each file as it is resolved: `git add <file>`.

## 4. Verify, then commit

Run the repository's own build and test commands - take them from its instructions
(`CLAUDE.md`, `AGENTS.md`, `README`, `package.json`, `Makefile`, CI workflows) and
use its own package manager. If it documents none, say so in the report instead of
inventing one. Fix whatever the merged combination broke; that is what a
reintegration is for. If a failure is pre-existing on the main branch itself, say so
rather than fixing it here.

```bash
git commit --no-edit
git log --oneline -1
git status --porcelain   # must be empty
```

`--no-edit` keeps git's generated merge message, matching most repositories' history.
If conflicts were resolved, append a one-line summary per resolved file to the
message instead.

## 5. Report

How many commits came in; which files conflicted and how each was resolved; the build
and test result; and that nothing was pushed - pushing stays the user's call.
