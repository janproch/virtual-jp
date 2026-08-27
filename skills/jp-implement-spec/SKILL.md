---
name: jp-implement-spec
description: Implement an agreed specification from docs/specs/ - pick the spec, carry out its plan and its decisions in code, then write implementation notes to docs/impl/YYYY-MM-DD-feature-name.md. Use ONLY when the user explicitly points at a spec ("implement spec", "implement the spec", "implement the plan from the brainstorming session"). A bare "implement this" or "start implementation" with no spec named is not an invocation.
---

# Implement a specification

This skill runs the **execution phase** of a change that has already been planned.
The plan is a document under `docs/specs/`, normally written by the
`jp-brainstorming` skill. This skill turns exactly that document into code, and
records what really happened in `docs/impl/`.

The spec is the authority. Its **Decisions** and **Architecture decisions** were
settled with the user and are not reopened here.

## Hard rules

- **Explicit invocation only.** The user must point at a spec, or at the
  brainstorming session that produced one. "Implement this", "start implementing"
  or a plain feature request is not an invocation - do the work directly instead.
- **Never re-decide what the spec decided.** A decision you disagree with is
  implemented as written and questioned in the notes' *Known problems*, not
  quietly replaced.
- **Never implement what the spec puts out of scope.** A gap you notice on the way
  is a follow-up in the notes, not an extra commit.
- **Never continue past an unanswered question.** After an `AskUserQuestion` call
  your turn ends - no further tool calls, no edits. Silence is not an answer.
- **Never report done on unverified work.** The repo's own checks run before the
  notes are written, and their real outcome goes in the notes.
- **The notes file is part of the work, not an optional extra.** An implementation
  without `docs/impl/YYYY-MM-DD-feature-name.md` is unfinished.

## 1. Choose the spec

If the user named a spec, or this session just produced one, use it - no question.

Otherwise list the specs that have no implementation notes yet. A spec is
implemented when a file in `docs/impl/` carries the **same feature name**, whatever
its date prefix:

```bash
for spec in docs/specs/[0-9][0-9][0-9][0-9]-*.md; do
  feature=$(basename "$spec" .md | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//')
  ls docs/impl/*-"$feature".md >/dev/null 2>&1 || echo "$spec"
done
```

If nothing comes back, say so and stop. Otherwise read the `Status:` and `#` title
line of each candidate and put them to the user with `AskUserQuestion`: one
single-select question, up to 4 options, newest first, each option's `description`
naming what the change is and flagging `Status: draft` where the spec was never
marked agreed. More than 4 candidates: offer the 4 newest and list the rest in your
message so the user can name one through "Other". **Then end the turn.**

## 2. Read the ground the spec stands on

Before the first edit, read enough that the spec's decisions map onto real code:

- the whole spec - *Context of the change* names the files it is built on
- `CLAUDE.md`, and the `README.md` anchors it points at for the area involved
- the code each phase of the *High-level plan* touches, and the tests around it
- any other `docs/*.md` the spec cites

State back in a short paragraph what the spec asks for, and anything that has moved
in the repository since it was written. If the code has drifted so far that a
decision no longer applies, that is an `AskUserQuestion`, not a judgement call.

## 3. Work the plan, phase by phase

Take the phases from the spec's *High-level plan*, keep them as a task list in the
order the spec gives, and do them one at a time. Within a phase you make the
ordinary implementation choices yourself - file layout, naming, helper extraction -
following the repository's conventions in `CLAUDE.md`, never the conventions of
another repository.

For each phase:

- implement it, including the tests the spec's *Architecture decisions* say an
  invariant needs
- run the checks that cover it and get them green before moving on
- keep documentation in step: `README.md` and every anchor `CLAUDE.md` lists for
  the area you changed are updated in the same phase, not at the end

Stop and ask only when carrying out a decision is impossible as written, or when
two decisions in the spec contradict each other in code. Everything else is
recorded in the notes and keeps moving.

## 4. Verify

Run the repository's own checks - its test, build and lint commands, plus its
end-to-end suite when the change reaches the UI and the spec asked for E2E coverage.
Take the commands from `CLAUDE.md` and the project's own manifest (`package.json`,
`Makefile`, `pyproject.toml`, ...), never from memory of another project.

A failure you caused is fixed. A failure that was already there on the base branch
is reported as such in the notes, with the evidence. Never skip, disable or narrow
a test to get green.

## 5. Write the implementation notes

```bash
date +%F        # the YYYY-MM-DD prefix - never guess today's date
```

Path: `docs/impl/YYYY-MM-DD-feature-name.md`, where the date is **today** (the day
the work was done, not the spec's date) and `feature-name` is **character for
character the feature name of the spec** - that pairing is what step 1 reads.

The document is short. Sections, all of them, in this order:

```markdown
# <Feature name>

Spec: docs/specs/YYYY-MM-DD-feature-name.md
Date: YYYY-MM-DD
Status: implemented | partially implemented
Area: <modules the change touched>

## What was done

A few lines or bullets: what now exists that did not before, and where it lives.
Name the modules and the key files, not every file touched - the diff is the
detail. Say which checks were run and what they reported.

## What is missing

Everything the spec asked for that is not in the code, and why - deferred,
blocked, or superseded. One line each. Nothing missing: say "Nothing - the spec
is implemented in full."

## Known problems

Honest weaknesses of what was built: shortcuts taken, cases not handled,
performance the change does not have, a spec decision that turned out awkward in
code. One line each, and where a problem has a cost, name it.

## Recommended follow-ups

The next changes worth making, most valuable first, each one sentence on what and
why. This is where a gap you noticed but left alone belongs.

## Changelog

Lines ready to be pasted into a release changelog by an agent that will never read
the rest of this file. One line per user-visible change, present tense, written for
the person using the app, no file names and no internal module names:

- Import a supplier CSV onto products by mapping its columns to product fields
- Fix duplicate products being created when an imported file has no id column

Nothing user-visible: say "No user-visible changes." and nothing else.
```

Style: ASCII only, present tense, and short - the notes are a page, not a report.
The `What was done` section stays smaller than the three that follow it if the
implementation was rough; that asymmetry is the point.

## 6. Commit and hand back

Commit the implementation on the branch the session is working on, in the phases it
was built in where that reads better than one commit. Then commit the notes on
their own, `docs: implementation notes for <feature name>`. Push per the
repository's rules.

Report: the spec, the notes path, what was left undone in one line, and the state
of the checks. Do not restate the changelog - it is in the file.
