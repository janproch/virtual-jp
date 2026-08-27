# Night worker

Status: agreed
Date: 2026-08-27
Area: skills/vjp-night-worker (new), interacts with vjp-implement-spec and the repository's main branch

## Context of the change

This repository ships Claude Code skills as a plugin; there is no application code
(`CLAUDE.md`). The skills split a change into two explicit phases:
`vjp-brainstorming` writes `docs/specs/YYYY-MM-DD-feature-name.md`, and
`vjp-implement-spec` turns exactly one such spec into code plus
`docs/impl/YYYY-MM-DD-feature-name.md`. `vjp-merge-claude-branches` and
`vjp-reintegrate-master` move the result between branches. All of them are invoked
explicitly and every one of them stops on an unanswered `AskUserQuestion`.

What does not exist today is anything that works a **queue** of specs. A user who
has brainstormed five features has to sit through five separate implement-spec
sessions, each of which starts by asking which spec to take, and each of which
leaves its branch for the user to land afterwards. `vjp-implement-spec` step 1
already knows how to find the specs that have no implementation notes yet, but it
offers a single-select of at most four and implements exactly one.

The new `vjp-night-worker` skill is that queue: pick the unimplemented specs once,
up front, then implement and land them one after another without further input -
the work a developer would leave running overnight.

## User request

Create a new skill, `vjp-night-worker`, invoked explicitly ("run night worker").
The skill first calls `AskUserQuestion` with checkboxes listing the specs that are
not implemented yet; the user ticks the ones to implement. Each checked spec is then
implemented, one by one, with the `vjp-implement-spec` skill, and once a spec is
completely implemented it is merged to master. Specs are implemented in ascending
order by the date of their first commit.

## Decisions

### A spec turns out to need a decision from you mid-implementation (two decisions contradict in code, or the repo drifted so a decision no longer applies). Nobody is awake to answer. What does the night worker do?

| Option | What it means |
|---|---|
| Skip it, keep going (Recommended) | Abandon that spec: its branch is left unmerged with whatever was built, the open question goes in the run report, and the worker moves to the next spec. Nothing half-decided reaches master, and one ambiguous spec does not cost the whole night. |
| Assume and continue | Pick the most defensible reading, implement it, and record the assumption in the impl notes' Known problems, then merge as normal. Gets more done per night, but master gains a decision you never made and unpicking it is a later change. |
| Stop the whole run | End the night at the first blocking question; the remaining checked specs are left untouched for the morning. Safest and simplest to reason about, but one bad spec early in the order wastes every spec behind it. |

**Answer: Assume and continue** - the worker never stops on a question. It picks the
most defensible reading, implements it, and records the assumption in the
implementation notes' *Known problems*, then merges as normal.

### A spec is implemented but the repository's own checks fail (or the merge into master conflicts in a way the worker cannot resolve). What then?

| Option | What it means |
|---|---|
| Leave branch, keep going (Recommended) | Do not merge: the branch stays as it is with the failure recorded in the impl notes and the run report, and the worker starts the next spec from an unchanged master. Broken work never lands, the rest of the night still runs. |
| Retry, then leave it | Try a bounded number of fix-and-recheck rounds before giving up on that spec, then leave the branch as above. More specs land per night, but a spec that is fundamentally wrong burns time the specs behind it needed. |
| Stop the whole run | Treat a red check as a stop condition for the night: nothing further is attempted. Strongest signal in the morning, at the cost of everything queued behind it. |

**Answer: Leave branch, keep going (Recommended)** - a failing spec is not merged,
its branch is left as it stands with the failure recorded, and the next spec starts
from an unchanged main branch.

### How does a finished spec reach master?

| Option | What it means |
|---|---|
| Branch per spec, merge back (Recommended) | Each spec gets its own branch containing the feature name (implement-spec already requires that), master is merged into it and the checks run there, then it lands on master as one --no-ff merge commit. Isolation per spec, one identifiable merge each, and a failing spec leaves master untouched. |
| Commit straight on master | The worker stays on master and commits each spec's work there directly. Simplest history and no merge step, but a spec that fails checks has already dirtied master and has to be reverted, and implement-spec's own branch-naming rule has to be waived. |
| Branch per spec, no merge | Implement each spec on its own branch and stop there, leaving every branch for the user to land in the morning (with vjp-merge-claude-branches). Safest, but it is not what "merged to master" asked for and the morning is back to manual work. |

**Answer: Branch per spec, merge back (Recommended)**, with the user's correction:
the specs are implemented **sequentially and each branch is cut from the main branch
as it stands at that moment**, so there is nothing to reintegrate and no conflict to
expect. The `main -> branch` half of the usual dance is therefore dropped; a conflict
on the way back means something moved underneath the run and is reported, not
resolved blind.

### When does the run push?

| Option | What it means |
|---|---|
| Push each spec as it lands (Recommended) | After each successful merge, push the spec branch and master. A run that dies at 3am has still published everything finished before it, and each spec is visible in the morning even if the session never reported back. |
| Push once at the end | Keep everything local until the last spec, then push master and the branches in one go - one CI run for the whole night instead of one per spec, but a crashed or interrupted run publishes nothing. |
| Never push | Land everything on the local master and leave publishing to the user. Matches vjp-reintegrate-master's rule that pushing stays the user's call, but a remote session's container is thrown away, so the night's work would be lost. |

**Answer: Push each spec as it lands (Recommended)** - the spec branch and the main
branch are both pushed as soon as that spec has landed.

### Which specs go on the checkbox list?

| Option | What it means |
|---|---|
| Every spec without impl notes (Recommended) | Exactly what vjp-implement-spec step 1 finds: any docs/specs/*.md with no docs/impl/ file carrying the same feature name. Options whose spec is still Status: draft are flagged as such in the description, and the user decides whether to tick them. |
| Only specs marked agreed | Drafts are listed in the message but not offered as options - a night of unattended work only ever builds specs the user signed off. Safer, but a spec the user forgot to mark agreed silently never gets built. |
| Every spec without impl notes, drafts included silently | No distinction in the list at all. Shortest options, but the user cannot see which of the ticked specs was never agreed. |

**Answer: Every spec without impl notes (Recommended)** - the same rule
`vjp-implement-spec` step 1 uses, with `Status: draft` flagged in the option's
description.

### How is each spec implemented within the run?

| Option | What it means |
|---|---|
| One subagent per spec (Recommended) | The worker keeps only the queue and the outcomes; each spec is implemented by a fresh subagent following vjp-implement-spec, which reports back a short summary. The night's context does not fill up, so spec ten gets the same attention as spec one. Requires the Task/Agent tool. |
| Inline, in the session's own context | The worker itself follows vjp-implement-spec for each spec in turn. Simplest and works anywhere, but every spec's reading, edits and check output stays in context, so a long queue degrades or runs out before it finishes. |
| Subagent when available, inline otherwise | Prefer a subagent, fall back to inline where the tool is absent. Most portable, at the cost of two code paths in the skill and a run whose behaviour depends on the harness. |

**Answer: One subagent per spec (Recommended)** - a fresh subagent per spec, given
the spec path and the branch to work on, reporting back a short structured summary.

### What does the run leave behind besides the code?

| Option | What it means |
|---|---|
| Chat report only (Recommended) | Each spec already writes docs/impl/YYYY-MM-DD-feature-name.md, so the run adds only a final summary in the session: what landed, what was left unmerged and why, what was skipped. Nothing extra is committed. |
| Also commit a run log | Write docs/night/YYYY-MM-DD-run.md listing the queue and each spec's outcome, and commit it at the end. A record that survives the session, at the cost of a new document type that duplicates the impl notes. |

**Answer: Chat report only (Recommended)** - the implementation notes are the record;
the run adds a final summary in the session and commits nothing extra.

## High-level plan

**Phase 1 - the queue.** Establish the run's preconditions and build the ordered
queue: a clean checkout with no merge in progress, the main branch identified from
the remote and fast-forwarded to it, then the specs that carry no implementation
notes, sorted ascending by the date of their first commit. Delivers the candidate
list and the facts each option needs (title, status, date).

**Phase 2 - the one question.** Put the candidates to the user as a multi-select
`AskUserQuestion`, split across questions where there are more candidates than a
single question holds, and end the turn. This is the only question of the run: what
comes back is the queue, in the order phase 1 established, and an empty answer ends
the run.

**Phase 3 - the per-spec cycle.** For each spec in turn: cut a branch carrying the
feature name from the main branch as it stands, hand the spec to a subagent that
follows `vjp-implement-spec` end to end, then take the subagent's outcome and either
land the branch on the main branch and push both, or leave the branch alone and
record why. Each spec starts from a main branch that already carries every spec that
landed before it. Depends on phases 1 and 2.

**Phase 4 - the report and the repository's own housekeeping.** Summarise the run in
the session, and carry the change through this repository's own rules for a new
skill: `README.md`, the regenerated `index.json`, and the checks in `CLAUDE.md`.

## Architecture decisions

**The skill never asks a second question.** Everything after the checkbox round is
decided by rule, because there is nobody to answer. This inverts
`vjp-implement-spec`'s "never continue past an unanswered question", so the subagent
is told explicitly that the rule is replaced for this run: it assumes the most
defensible reading, records the assumption under *Known problems* in the notes, and
continues. That instruction lives in the night worker's prompt to the subagent, not
in `vjp-implement-spec` - the implement skill keeps its own hard rule for the
interactive case.

**Ordering key is the spec's first commit, from git, not the filename.** The date in
`docs/specs/YYYY-MM-DD-*.md` is the day the spec was written, which is not
necessarily the order the user queued them in;
`git log --diff-filter=A -1 --format=%cI -- <spec>` is. A spec that has never been
committed has no such date and sorts last, after every committed one.

**Branch per spec, cut fresh from the main branch, landed with `--no-ff`.** Because
the queue is strictly sequential and every branch starts from the current main
branch, the main branch is already an ancestor: the merge back cannot conflict, and
the `main -> branch` reintegration other skills perform is unnecessary. A conflict at
that point therefore means something moved underneath the run (a push by someone
else); it is aborted and reported, never resolved blind.

**Landing is gated on the subagent's own verification.** A spec lands only when its
notes say the repository's checks passed. The worker does not re-run the checks
itself before merging - the subagent already did, in the branch, and a second run
buys nothing - but it does verify that a `docs/impl/` file for the feature exists,
because that file is what makes the spec count as implemented for every later run.

**Failure is per spec, never per run.** A spec that cannot be verified, or whose
merge conflicts, leaves its branch behind untouched and does not advance the main
branch; the next spec is cut from the main branch as if the failed one never
happened. The only whole-run stop conditions are a dirty checkout at the start and
an empty answer to the checkbox question.

**Push after each landing, branch first, then the main branch.** The night's work
survives a container that is reclaimed before the session reports back. A rejected
push (someone else advanced the main branch) is treated as the conflict case above:
report, do not force.

## Weaknesses and risks

- **A wrong assumption reaches the main branch.** The chosen answer to the blocking
  question means a spec whose decisions contradict each other is implemented anyway,
  on a reading the user never agreed to, and pushed. Likely enough over a long queue;
  the cost is a change that has to be unpicked in the morning. What reduces it: the
  assumption is written into *Known problems* in the notes, and the report names
  every spec that carried one, so the morning knows where to look.
- **A run this long is exactly where context runs out.** The subagent per spec is the
  mitigation, but the worker's own context still grows with each outcome, and a
  single very large spec can exhaust its subagent mid-implementation. What reduces
  it: the worker keeps only a one-line outcome per spec, and a subagent that dies is
  treated as a failed spec rather than retried.
- **Unattended pushes to the main branch trigger whatever the main branch triggers.**
  In a repository whose CI deploys from the main branch, a night run deploys - several
  times. The skill has to say so before the checkbox question, in the message that
  accompanies it, so the user ticking boxes knows what a tick costs.
- **The queue is only as good as the spec statuses.** Drafts are offered, flagged;
  a user who ticks everything gets never-agreed specs built overnight.
- **Nothing bounds the run.** No time limit, no spec limit: ten ticked specs is ten
  implementations, however long they take. Whether that needs a cap is left open
  until a real run shows how long a spec takes.

## Out of scope

- Running specs in parallel. The queue is strictly sequential; that is what makes the
  conflict-free merge argument hold.
- Creating or amending specs. The night worker only consumes `docs/specs/`; writing
  one stays `vjp-brainstorming`'s job.
- Landing branches the night worker did not create, or clearing an existing
  `claude/*` backlog - that is `vjp-merge-claude-branches`.
- Pull requests, reviews and CI babysitting. The worker pushes; it does not open,
  update or watch a pull request.
- Any scheduling. "Night" is when the user starts it; the skill installs no cron, no
  trigger and no wake-up.
