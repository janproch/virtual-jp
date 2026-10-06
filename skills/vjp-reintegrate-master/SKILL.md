---
name: vjp-reintegrate-master
description: Merge the freshly fetched main branch (master/main, whatever the repository uses) into the current feature branch, resolve the conflicts, verify the result and commit the merge. Use ONLY when the user explicitly asks for it ("reintegrate master", "reintegrate the main branch", "catch this branch up with master", "sync with master", "use the reintegrate master skill"). A branch that merely looks behind, a pull request that needs updating, or a request to rebase or squash is not an invocation.
---

# Reintegrate the main branch into the current branch

Direction is always main -> current branch, as a merge commit. Main itself is not touched.

## 1. Preconditions

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git status --porcelain && git rev-parse -q --verify MERGE_HEAD   # both must print nothing
```

`$MAIN` empty - `git remote set-head origin --auto`, else whichever of main/master exists
(ask if both). Stop on a dirty tree or a merge/rebase/cherry-pick in progress; never stash.
Stop if HEAD is the main or a release branch.

## 2. Merge the fetched main

```bash
git fetch origin "$MAIN"
git log --oneline "HEAD..origin/$MAIN"        # empty - already up to date, stop
git merge --no-ff --no-edit "origin/$MAIN"   # origin/, never the stale local ref
```

Resolving conflicts:
- Keep both sides' intentions; read the commits behind each side when the hunk is unclear.
  `--ours/--theirs` only for files wholly owned by one side.
- Regenerate lockfiles and generated artifacts from the resolved inputs.
- Re-read `CLAUDE.md`/`AGENTS.md` for invariants on the touched files.
- No markers left: `git diff --check`.

## 3. Verify and commit

Run the repo's own build and tests (from its docs/manifest). Fix what the combination broke;
report pre-existing main-branch failures without fixing them. `git commit --no-edit`, adding
a one-line note per resolved file when there were conflicts.

## 4. Report

Commits brought in, conflicted files and how each was resolved, build and test result.
