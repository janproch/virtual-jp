---
name: vjp-night-worker
description: Work a queue of specifications unattended - ask once which of the not-yet-implemented specs under docs/specs/ to build, then implement them one by one in ascending order of their first commit, each on its own branch, landing and pushing every finished one on the main branch before starting the next. Use ONLY when the user explicitly asks for it ("run night worker", "run the night worker", "use the night worker skill", "work through the specs overnight"). A request to implement one named spec, a bare "implement this", and a request to land existing branches are not invocations.
---

# Work the spec queue overnight

This skill runs a **whole queue** of already-written specifications without the user
present. It asks one question - which specs to build - and after that decides
everything by rule, because there is nobody awake to answer.

Each spec is implemented exactly as `vjp-implement-spec` prescribes, on its own
branch cut from the main branch as it stands, and lands on the main branch before the
next spec starts. The queue is strictly sequential; that is what keeps every merge
conflict-free.

Nothing here assumes a particular project, branch name, build tool or CI setup - take
those from the repository's own instructions.

## Hard rules

- **Explicit invocation only.** The user must name the night worker. "Implement the
  specs", "implement this" or a plain feature request is not an invocation.
- **One question, and only one.** After the checkbox round the run never asks again.
  A choice that would have been an `AskUserQuestion` is made on the most defensible
  reading and written into the implementation notes' *Known problems*.
- **Never merge unverified work.** A spec lands only when its own checks passed in
  its branch and its `docs/impl/` notes exist. Never skip, disable or narrow a test
  to get there.
- **Never resolve a merge-back conflict blind.** The branch was cut from the main
  branch, so a conflict means something moved underneath the run. Abort and report.
- **One spec's failure never stops the run.** The only whole-run stop conditions are
  a dirty checkout at the start and an empty answer to the question.
- **Sequential only.** Never implement two specs at the same time, and never cut the
  next branch before the previous spec has landed or been abandoned.
- **Never force-push, never rewrite published history.**

## 1. Prepare the run

```bash
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
git status --porcelain                  # must be empty
git rev-parse -q --verify MERGE_HEAD    # must print nothing
git fetch origin --prune
git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
```

If `$MAIN` comes back empty, try `git remote set-head origin --auto`, else fall back
to whichever of `origin/main` / `origin/master` exists - and ask the user if both do.
Use whatever `git remote` reports if it is not `origin`.

Stop and report if the tree is dirty, a merge or rebase is in progress, or the
fast-forward is refused. Never stash, reset or force on your own initiative.

Take the build and test commands from the repository's own instructions
(`CLAUDE.md`, `AGENTS.md`, `README`, `package.json`, `Makefile`, CI workflows) and
its own package manager; the subagents need them, and a repository that documents
none is said so in the report rather than invented for. Check the CI config for what
pushing `$MAIN` triggers: **if it deploys, say so in the message that carries the
question** - a night run pushes the main branch once per landed spec, so a tick is a
deploy.

## 2. Build the queue

A spec is implemented when a file in `docs/impl/` carries the **same feature name**,
whatever its date prefix. The candidates are the rest, oldest first by the date their
spec was **first committed** - not by the date in the filename, which is the day the
spec was written and not the order the user queued them in:

```bash
for spec in docs/specs/[0-9][0-9][0-9][0-9]-*.md; do
  feature=$(basename "$spec" .md | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//')
  ls docs/impl/*-"$feature".md >/dev/null 2>&1 && continue
  added=$(git log --diff-filter=A -1 --format=%cI -- "$spec")
  echo "${added:-9999}  $spec"
done | sort
```

A spec that has never been committed has no such date and sorts last. Read the
`Status:` and `#` title line of each candidate - the option descriptions need them.
If nothing survives, say so and stop.

## 3. Ask once, then stop asking

`AskUserQuestion` with `multiSelect: true`. Each option's `label` is the feature
name, its `description` the spec's title, its first-commit date, and the words
`Status: draft` where the spec was never marked agreed. A question holds 4 options
and a call holds 4 questions: up to 4 candidates is one question; 5 to 16 split
across up to 4 questions, **oldest first**, so the queue reads in the order it will
be built; beyond 16, offer the 16 oldest and say how many were left out.

Alongside the question, state what the run will do: how many pushes of the main
branch it implies, what those pushes trigger, and that from the answer on nothing
else will be asked.

**Then end the turn.** No default, no guess, no implementing. Silence, a timeout or
an empty answer means build nothing - report that and stop. Only ticked specs are
built, in the queue order of step 2, never in the order the answer came back.

## 4. Implement and land each spec, one at a time

For each spec in turn, from a main branch that already carries every spec landed
before it:

### 4a. Cut the branch

```bash
git switch "$MAIN"
git switch -c <branch>
```

The branch is **`claude/<feature-name>`**, the spec's own slug - that is
`vjp-implement-spec`'s rule, and a name describing the activity rather than the
feature (`claude/spec-implementation-a1b2c3` and the like) is not it. Follow the
repository's branch naming convention instead where it has one that says otherwise.
If the name is taken, add a numeric suffix and say so in the report.

### 4b. Hand the spec to a subagent

One fresh subagent per spec, so a long queue does not fill the run's own context.
Give it, in the prompt and without relying on anything it cannot see:

- the spec path, and that it follows `vjp-implement-spec` end to end - read the ground
  the spec stands on, work the plan phase by phase, verify with the repository's own
  checks, write `docs/impl/YYYY-MM-DD-feature-name.md`, commit on the branch
- the branch it is on, that it stays there, and that it never merges into or touches
  the main branch
- **the replacement for one hard rule**: nobody is available to answer, so an
  `AskUserQuestion` it would have asked is instead resolved on the most defensible
  reading, implemented, and recorded in the notes' *Known problems* named as an
  assumption. Every other hard rule of `vjp-implement-spec` stands - above all, never
  re-deciding what the spec decided, never implementing what the spec puts out of
  scope, and never reporting done on unverified work
- what to report back, in a few lines: implemented in full or partially, the notes
  path, the exact result of each check it ran, every assumption it made, and whether
  it pushed the branch

Wait for it to finish before doing anything else. A subagent that dies or comes back
empty is a failed spec - do not retry it.

### 4c. Decide, then land or leave

The spec lands only if all of these hold. Verify them yourself; do not take the
report's word for it:

```bash
git status --porcelain                       # clean
ls docs/impl/*-<feature-name>.md             # the notes exist
git log --oneline "$MAIN"..HEAD              # there is work on the branch
```

plus the subagent reporting the repository's own checks green. If any fails, leave
the branch exactly as it stands, push it so the night is not lost, record the spec as
not landed with the reason, and go to the next spec - the main branch has not moved,
so the next branch is cut from unchanged ground.

Otherwise land it:

```bash
git push -u origin <branch>
git switch "$MAIN"
git merge --no-ff --no-edit <branch>
git push origin "$MAIN"
```

`--no-ff` keeps each spec one identifiable merge commit. The merge cannot conflict -
the branch was cut from `$MAIN` and nothing else has moved it. If it does, or if
either push is rejected, someone else advanced the main branch during the run:
`git merge --abort`, leave the branch pushed, record it as not landed, and carry on
with the next spec from a re-fetched main branch. Never force, never resolve blind.

Retry a push that failed on a network error up to 4 times, backing off 2s, 4s, 8s,
16s. A rejected push is not a network error.

## 5. Report

One line per spec of the queue, in build order: landed with the merge commit and the
notes path, or not landed with the branch it is on and what stopped it. Then, once:

- every assumption the subagents made, and which spec each belongs to - this is where
  the morning starts reading
- what was pushed, and what those pushes triggered
- the candidates the user left unticked

Do not restate the implementation notes. They are in `docs/impl/`, one file per spec,
and they are the record of what was built.
