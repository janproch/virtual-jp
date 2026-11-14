---
name: vjp-cloud-session
description: Make sure a Claude Code cloud session does not start working on a stale checkout - fetch the remote, check whether the local branch is behind its remote counterpart (or behind the branch the work is based on), fast-forward it when that is safe, and report the state before handling the first prompt. Use at the start of EVERY Claude Code cloud (remote) session - the environment variable CLAUDE_CODE_REMOTE is "true" - before acting on the first user prompt, whatever that prompt asks, and again whenever the user asks to "check the branch", "is this branch up to date", "use the cloud session skill". Do not use in a local session.
---

# Cloud session start: refuse to work on a stale branch

Start your first reply with the line `Invoking VJP cloud session skill, version 0.6.0`.

Run this before touching the first prompt's task. Fast-forward only: never merge, rebase,
reset over own commits, stash or force. Afterwards carry on with the first prompt.

## 1. Preconditions

```bash
[ "$CLAUDE_CODE_REMOTE" = true ] || echo local     # local - say so in one line and skip this skill
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
B=$(git branch --show-current)
git fetch origin --prune
```

`$MAIN` empty - `git remote set-head origin --auto`, else whichever of main/master exists.
Detached HEAD, or no `origin` - report it and skip to the first prompt.

## 2. Pick the reference

- `REF=origin/$B` when that remote branch exists (a resumed or user-named branch).
- Otherwise the base the work is meant to start from: the branch the first prompt names
  ("on next", "based on release-2") as `origin/<name>`, else `origin/$MAIN`.
- The first prompt names a branch to work on, `$B` is a different one that has no own
  commits (`git log --oneline origin/<name>..HEAD` empty) and the session rules do not pin
  the development branch - `git switch -C <name> --track origin/<name>` instead, then `REF`
  is `origin/<name>`. When the session pins its own branch, keep it and take
  `origin/<name>` as `REF`.

## 3. Compare and catch up

```bash
git rev-list --left-right --count "HEAD...$REF"   # "<ahead> <behind>"
git log -1 --format='%h %cs %s' HEAD; git log -1 --format='%h %cs %s' "$REF"
```

- behind 0 - up to date, nothing to do.
- ahead 0, behind > 0, clean tree (`git status --porcelain` empty) -
  `git merge --ff-only "$REF"`.
- ahead 0, behind > 0, dirty tree - stop and ask the user before doing anything else.
- ahead > 0 and behind > 0 - diverged: do not merge; tell the user and ask whether to
  catch up (the `vjp-reintegrate-master` skill does that for the main branch) or to work on
  the old base on purpose.
- When `REF` is the work branch itself, also report how far behind `origin/$MAIN` it is,
  without merging.

## 4. Report

One short block before the answer to the first prompt: branch, `REF`, ahead/behind counts,
the commit and date HEAD was at and is at now, and what was done (nothing, fast-forwarded,
or waiting for the user).
