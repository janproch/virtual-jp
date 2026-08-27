---
name: jp-merge-claude-branches
description: Find unmerged claude/* branches with commits in the last two weeks, ask the user which ones to land, then for each chosen branch merge the main branch into it, verify it, and merge it back. Use ONLY when the user explicitly asks for it ("merge claude branches", "use the merge claude branches skill", "land the claude branches", "clear the claude/* backlog"). A request to merge one named branch, to open or update a pull request, or to catch the current branch up with master is not an invocation.
---

# Merge claude/* branches into the main branch

For every branch the user picks, the direction is always **main -> branch, then
branch -> main**: the branch is first brought up to date and made to pass, and only
then does it reach the main branch. Both are pushed at the end.

Nothing here assumes a particular project, branch name, build tool or CI setup - take
those from the repository's own instructions.

## 1. Learn the repository

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
```

If that is empty, try `git remote set-head origin --auto`, else fall back to whichever
of `origin/main` / `origin/master` exists - and ask the user if both do. Use whatever
`git remote` reports if it is not `origin`.

Take the build and test commands from the repository's own instructions (`CLAUDE.md`,
`AGENTS.md`, `README`, `package.json`, `Makefile`, CI workflows) and its own package
manager. If it has neither, say so in the report instead of inventing one. Check the
CI config for what pushing `$MAIN` triggers; if it deploys to production, tell the
user before step 6.

## 2. Refresh, on a clean checkout

```bash
git status --porcelain          # must be empty
git rev-parse -q --verify MERGE_HEAD    # must print nothing
git fetch origin --prune
git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
```

Stop and report if the tree is dirty, a merge/rebase is in progress, or the
fast-forward is refused. Never stash, reset or force on your own initiative.

## 3. List the candidates

```bash
for b in $(git branch -r --no-merged "$MAIN" --list 'origin/claude/*' --format='%(refname:short)'); do
  echo "$(git log -1 --format=%cI "$b")  $b  $(git rev-list --count "$MAIN".."$b") commits"
done | sort -r
```

`--no-merged "$MAIN"` is evaluated against the branch just refreshed in step 2, not a
stale ref. Drop everything older than two weeks, computing the cutoff from today's
date rather than eyeballing it. If nothing survives, say so and stop. For each
survivor, `git log --oneline "$MAIN"..<branch>` gives the context to show the user.

## 4. Ask which branches to merge

`AskUserQuestion` with `multiSelect: true`. A question holds 4 options and a call
holds 4 questions: up to 4 candidates is one question; 5 to 16 split across up to 4
questions, newest first; beyond that, offer the 16 most recent and say how many were
left out. Each option's `label` is the branch name without `origin/`, its
`description` the commit date and newest subject.

**Then end the turn.** No default, no guess, no merging. Silence, a timeout or an
empty answer means merge nothing - report that and stop. Only branches the user
explicitly ticked get merged.

## 5. Merge each selected branch, one at a time

**Sequentially** - each merge moves `$MAIN`, so a later branch must be reintegrated
against the one that already contains the earlier ones. Never batch 5a for all
branches and then batch 5b.

### 5a. Main into the branch

```bash
git switch <branch>                     # or: git switch -c <branch> --track origin/<branch>
git merge --ff-only origin/<branch>     # only if the local branch already existed
git merge --no-ff --no-edit "$MAIN"
```

Merge the **local** `$MAIN`, not `origin/$MAIN` - after the first landing the remote
ref is already out of date. Resolve every conflict by hand, keeping both sides'
intentions rather than taking one wholesale; regenerate lockfiles and other generated
artifacts from the resolved inputs instead of hand-merging them; leave no conflict
marker behind (`git diff --check`); and honour the invariants the repository's own
docs state for the files touched. The `jp-reintegrate-master` skill spells the same
rules out in more detail if it is installed. Then run the build and test commands
from step 1.

If it cannot be made to pass, **abort this branch** (`git merge --abort`, or reset the
merge commit), leave `$MAIN` untouched, continue with the next selected branch, and
report it at the end.

### 5b. Branch back into main

```bash
git switch "$MAIN"
git merge --no-ff --no-edit <branch>
git push origin <branch>
```

This must not conflict - 5a made `$MAIN` an ancestor. If it does, something moved
underneath: `git merge --abort` and report rather than resolving blind. Keep `--no-ff`
so each feature stays one identifiable merge commit, unless the repository's history
clearly says otherwise. Push the branch only; `$MAIN` goes once, at the end, so five
branches trigger one CI run instead of five.

## 6. Push the main branch

```bash
git log --oneline "origin/$MAIN".."$MAIN"
git push origin "$MAIN"
```

Show the log first - last chance to see what is about to be published. Never
`--force`. If rejected, `git fetch origin` and `git merge --ff-only "origin/$MAIN"`,
then push again; if that fast-forward is refused, stop and report. Confirm with the
user first if step 1 found this deploys to production. If no branch survived 5a, there
is nothing to push.

## 7. Report

Which branches merged and how many commits each brought; what conflicted and how it
was resolved; the build and test result per branch; which selected branches were
aborted and why; which candidates the user left unticked; what was pushed and what it
triggered, or which ref is still only local.
