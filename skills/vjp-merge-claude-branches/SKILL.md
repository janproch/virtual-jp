---
name: vjp-merge-claude-branches
description: Find unmerged claude/* branches with commits in the last two weeks, ask the user which ones to land, then for each chosen branch merge the main branch into it, verify it, and merge it back. Use ONLY when the user explicitly asks for it ("merge claude branches", "use the merge claude branches skill", "land the claude branches", "clear the claude/* backlog"). A request to merge one named branch, to open or update a pull request, or to catch the current branch up with master is not an invocation.
---

# Merge claude/* branches into the main branch

Per chosen branch: main -> branch (resolve, verify), then branch -> main. One at a time.

## 1. Prepare

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git status --porcelain && git rev-parse -q --verify MERGE_HEAD   # both must print nothing
git fetch origin --prune && git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
```

`$MAIN` empty - `git remote set-head origin --auto`, else whichever of main/master exists
(ask if both). Stop on a dirty tree, merge in progress or refused fast-forward; never stash,
reset or force. Take build/test commands from the repo's docs and manifest. If pushing
`$MAIN` deploys to production, confirm with the user before the final push.

## 2. Candidates and selection

```bash
for b in $(git branch -r --no-merged "$MAIN" --list 'origin/claude/*' --format='%(refname:short)'); do
  echo "$(git log -1 --format=%cI "$b")  $b  $(git rev-list --count "$MAIN".."$b") commits"
done | sort -r
```

Keep those with commits in the last 14 days (compute the cutoff). None - stop.
`AskUserQuestion`, `multiSelect: true`, label = branch without `origin/`, description =
date + newest subject; 4 options per question, 4 questions per call, newest first; beyond
16 say how many were omitted. End the turn. Merge only ticked branches.

## 3. Per branch, sequentially

```bash
git switch <branch>      # or: git switch -c <branch> --track origin/<branch>
git merge --ff-only origin/<branch>
git merge --no-ff --no-edit "$MAIN"          # local $MAIN - it carries earlier landings
```

Resolve conflicts keeping both intentions, regenerate lockfiles/generated files, check
`git diff --check`, respect the repo's documented invariants (`vjp-reintegrate-master`
details this). Run build and tests. Cannot pass - abort this branch, leave `$MAIN`
untouched, continue.

```bash
git switch "$MAIN" && git merge --no-ff --no-edit <branch>
git push origin <branch>
```

A conflict here means something moved - `git merge --abort` and report.

## 4. Push main once

Show `git log --oneline "origin/$MAIN".."$MAIN"`, then `git push origin "$MAIN"`. Never
force; if rejected, fetch, `--ff-only`, retry; refused - stop and report.

## 5. Report

Per branch: merged (commits brought, conflicts and resolutions, test results) or aborted
(why); unticked candidates; what was pushed and triggered.
