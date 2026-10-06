---
name: vjp-night-worker
description: Work a queue of specifications unattended - ask once which of the not-yet-implemented specs under docs/specs/ to build, then implement them one by one in ascending order of their first commit, each on its own branch, landing and pushing every finished one on the main branch before starting the next. Use ONLY when the user explicitly asks for it ("run night worker", "run the night worker", "use the night worker skill", "work through the specs overnight"). A request to implement one named spec, a bare "implement this", and a request to land existing branches are not invocations.
---

# Work the spec queue overnight

One question up front, then no more - nobody is awake to answer. Specs are built strictly
sequentially, each on its own branch cut from the current main branch and landed before
the next starts.

## Rules

- After the selection question, never ask again: resolve on the most defensible reading
  and record it as an assumption in the notes' *Known problems*.
- Land only verified work (checks green, notes exist). Never skip or weaken tests.
- Never resolve a merge-back conflict; abort and move on.
- One spec failing never stops the run. Whole-run stops: dirty checkout, failed push
  probe, empty answer.
- Never force-push or rewrite published history.

## 1. Prepare

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git status --porcelain && git rev-parse -q --verify MERGE_HEAD   # both must print nothing
git fetch origin --prune && git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
git push origin "$MAIN"     # push probe: must say "Everything up-to-date"
```

`$MAIN` empty - `git remote set-head origin --auto`, else whichever of main/master exists
(ask if both). If the push probe is refused, build nothing: report what refused it and what
would clear it (an agent settings rule pre-approving push and merge with no ask/deny rule
for them; pushes named explicitly in the user's request; missing credentials).

Find the build/test commands in the repo's own docs and manifest. Check whether CI deploys
on a push to `$MAIN`.

## 2. Build the queue

Unimplemented specs (no `docs/impl/` file with the same slug), oldest **first commit** first
(not the filename date); uncommitted specs sort last:

```bash
for spec in docs/specs/[0-9][0-9][0-9][0-9]-*.md; do
  feature=$(basename "$spec" .md | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//')
  ls docs/impl/*-"$feature".md >/dev/null 2>&1 && continue
  added=$(git log --diff-filter=A -1 --format=%cI -- "$spec")
  echo "${added:-9999}  $spec"
done | sort
```

None - say so and stop.

## 3. Ask once

`AskUserQuestion`, `multiSelect: true`; label = slug, description = title, first-commit
date, `Status: draft` if not agreed. Up to 4 options per question, 4 questions per call,
oldest first; beyond 16, say how many were omitted. In the same message state how many
pushes to `$MAIN` the run implies, what they trigger (deploys!), that nothing else will be
asked, and ask the user to confirm the pushes in their answer. End the turn. Build only
ticked specs, in queue order.

## 4. Per spec

1. `git switch "$MAIN" && git switch -c "claude/<slug>-$(openssl rand -hex 3)"`.
2. Hand it to a **fresh subagent** with: the spec path; follow `vjp-implement-spec` end to
   end (notes in `docs/impl/`, commits on this branch); stay on the branch, never touch
   `$MAIN`; instead of asking, decide and record assumptions in *Known problems* (all other
   rules stand); report status, notes path, exact check results, assumptions. A dead or
   empty subagent is a failed spec - no retry.
3. Verify yourself: clean tree, notes file exists, `git log "$MAIN"..HEAD` non-empty,
   checks reported green. If not - push the branch, record not landed, next spec.
4. Land:
   ```bash
   git push -u origin <branch>
   git switch "$MAIN" && git merge --no-ff --no-edit <branch>
   git push origin "$MAIN"
   ```
   Conflict or rejected push - `git merge --abort`, leave branch pushed, record not landed,
   re-fetch `$MAIN`, continue. Retry only network failures (4x: 2s, 4s, 8s, 16s).

## 5. Report

Per spec in build order: landed (merge commit, notes path) or not (branch, reason). Then
every assumption made per spec, what was pushed and triggered, and the unticked candidates.
