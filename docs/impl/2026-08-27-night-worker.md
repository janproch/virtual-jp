# Night worker

Spec: docs/specs/2026-08-27-night-worker.md
Date: 2026-08-27
Status: implemented
Area: skills/vjp-night-worker, README.md, index.json

## What was done

`skills/vjp-night-worker/SKILL.md` is the new skill, all four phases of the spec in
one document:

- **Prepare** - resolve the main branch from `origin/HEAD`, refuse a dirty tree or an
  in-progress merge, fetch and fast-forward, take the build and test commands from the
  repository's own instructions, and check what pushing the main branch triggers so a
  deploy is stated before the question is asked.
- **Queue** - the candidates are the specs with no `docs/impl/` notes carrying the same
  feature name, ordered by `git log --diff-filter=A -1 --format=%cI` on the spec file;
  a spec never committed sorts last.
- **The one question** - a `multiSelect` `AskUserQuestion`, oldest first so the options
  read in build order, up to 4 questions of 4 options, drafts flagged, and an explicit
  hard rule that the run never asks again.
- **Per spec** - branch cut from the main branch carrying the feature-name slug, one
  fresh subagent per spec following `vjp-implement-spec` with the "never continue past
  an unanswered question" rule replaced by assume-and-record, then a gate the worker
  checks itself (clean tree, notes present, commits on the branch, checks reported
  green) before `--no-ff` merging and pushing branch and main. A failure leaves the
  branch pushed and unmerged and moves on.
- **Report** - one line per spec, then the assumptions the subagents made, what was
  pushed and what it triggered, and the unticked candidates.

`README.md` gained the skill-table row (phase `batch`) and a night-worker line in the
Use example; `index.json` was regenerated and now ships six files.

Checks run, all green: the three JSON files parse; every `SKILL.md` frontmatter `name`
equals its directory name; `README.md` links exactly the skills present in `skills/`;
`python3 scripts/build-index.py --check` reports the manifest current. The skill is
instructions rather than code, so its shell fragments were run against this repository:
the queue snippet correctly drops `virtual-jp-update-skill` (it has notes) and returns
`night-worker` alone with its first-commit timestamp.

## What is missing

Nothing - the spec is implemented in full.

## Known problems

- The implemented-or-not test is a glob, `ls docs/impl/*-<feature>.md`, so a feature
  name that is a suffix of an already-implemented one (`import` against
  `csv-import`) reads as implemented and silently never reaches the queue. Inherited
  from `vjp-implement-spec` step 1 on purpose - the two must agree - but it is wrong
  in both places.
- "Checks green" is the subagent's word. The worker verifies the notes exist, the tree
  is clean and the branch has commits, but it does not re-run the suite before merging,
  so a subagent that misreports its own verification lands broken work on the main
  branch.
- The spec's own risk stands unmitigated by design: an assumption made at 3am is
  pushed to the main branch and only surfaces in the morning report and the notes'
  *Known problems*.
- Nothing bounds the run - no time limit, no spec cap, no way to stop it short of
  interrupting the session.
- Only a real overnight run against a multi-spec queue will exercise step 4 end to
  end; here it was verified fragment by fragment against a repository with one
  candidate.

## Recommended follow-ups

- Replace the suffix-prone glob with an exact feature-name match in both this skill
  and `vjp-implement-spec`, so a short feature name cannot be swallowed by a longer
  one.
- Have the worker re-run the repository's fast checks on the branch before merging -
  cheap next to a spec implementation, and it closes the "takes the subagent's word"
  gap.
- Give the run a budget (a spec cap or a wall-clock cut-off) and report what it did
  not reach, once a real run shows how long a spec takes.

## Changelog

- Run a queue of specifications unattended with the night worker: tick the specs to
  build once, and each is implemented on its own branch and landed on the main branch,
  oldest spec first
