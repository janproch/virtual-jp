---
name: vjp-design-feature
description: Design a change into a specification with as few questions as possible - gather context, ask only the questions that cannot be answered from the repository or the request, decide the rest yourself and record why, then write docs/specs/YYYY-MM-DD-feature-name.md in the same format the brainstorming skill produces. Use ONLY when the user explicitly asks for it ("design feature: ...", "design the feature", "use the design feature skill"). Never start it on your own from an ordinary feature request; a plain feature request, a bug report or "what do you think about X" is not an invocation.
---

# Design a change into a specification

This skill runs the **high-level planning phase** of a change, and nothing else. Its
only deliverable is one document under `docs/specs/`. It produces no code, no
refactor, no task breakdown and no implementation.

It produces exactly the document `vjp-brainstorming` produces, in the same place and
the same format, and differs from it in one thing only: **how many questions it
asks**. Brainstorming settles every important choice with the user. This skill
settles what it can from the repository and the request, and puts to the user only
what it genuinely cannot decide. The document still records every decision - the ones
the user made and the ones you made - so a reader cannot tell which choices were
cheap only because you took them.

## Hard rules

- **Explicit invocation only.** Only run when the user names designing a feature.
- **Never write or change source code during the session.** The only file you create
  is the spec, and the only commit you make is the one that carries it.
- **Never create a branch.** The spec is committed and pushed on the repository's
  main branch - see step 5. Branches belong to the implementation phase.
- **Never continue past an unanswered question.** After an `AskUserQuestion` call
  your turn ends - no further tool calls, no edits, no "meanwhile I will...".
  Silence, elapsed time and an interruption are not answers.
- **Never invent an answer.** If the user's reply is ambiguous, ask again rather
  than picking the reading that suits you. If the user answers "Other" with free
  text, that text is the decision, verbatim.
- **Never hide a decision you took.** Fewer questions is not less recorded. Every
  choice that shapes the result is in the **Decisions** section, marked as decided
  by you, with the reason and the alternative it beat.
- **Never put implementation steps in the spec.** File-by-file plans, function
  signatures, commit sequences and effort estimates belong to a later phase.

## 1. Gather context first - no questions yet

This step carries more weight here than in a session that asks freely: every fact you
find in the repository is a question you do not have to spend.

- Read `CLAUDE.md` and the `README.md` sections it points at for the area involved.
- Read the code the change would touch, and any existing `docs/specs/*.md` or
  `docs/*.md` covering the same ground - a superseded design document is context, and
  a spec for a neighbouring feature usually settles half the choices by precedent.
- Check what already exists: half the requests are an extension of something built.
- Look at how comparable features in this repository were shaped. A repeated pattern
  is a decision the repository has already made.

Then state back, in a short paragraph, what you understood the request to be and what
exists today.

## 2. Sort the open choices before asking anything

List the choices the change turns on - what it **is**, where it lives, how it is
stored, how it is presented, what happens to existing data, what is deferred. For
each one, decide which of three piles it belongs in:

- **Already answered** - the repository, its conventions, or the user's own request
  settles it. Take the answer and move on. Never ask about naming, styling, package
  manager, test framework or any other convention the repository fixes.
- **Yours to decide** - not settled anywhere, but one option is clearly better here,
  or the choice is cheap to change later, or getting it wrong costs a small rewrite.
  Decide it, and record it in **Decisions** with the alternative and the reason.
- **The user's to decide** - ask. Only these reach `AskUserQuestion`.

A choice belongs to the user when **both** of these hold:

1. You cannot answer it from the repository, the request, or precedent - it depends on
   the user's intent, their priorities, or facts you have no access to (external
   constraints, deadlines, an API you cannot see).
2. The answers lead to materially different work, and the wrong one is expensive to
   undo - a data model or schema that outlives the change, a scope boundary that
   decides whether a whole workstream exists, a user-facing shape that becomes a
   contract, dropping backwards compatibility for data already written.

If only the first holds, pick the option you would defend and record it. If only the
second holds, you already know the answer - use it.

**Aim for zero to three rounds.** Zero is a good outcome when the request and the
repository are clear; say so in the hand-back rather than manufacturing a question.
More than three means you are asking about things you could have decided - go back
and re-sort the pile.

**Question quality**, for the few you do ask:

- 2-4 options, mutually exclusive, each a choice someone could actually defend.
- Every option gets a `description` naming its trade-off, not restating its label.
- Put your recommendation first and mark it `(Recommended)`. Recommend one; do not
  survey.
- `header` is <= 12 characters.
- Use `multiSelect` only when the options genuinely combine.
- Group at most 2-3 tightly related decisions into one call. Independent decisions
  get their own round, so an early answer can reshape the later question.

Immediately after each answer comes back, append that round to the spec's
**Decisions** section (see step 4) - the question, all offered options with their
descriptions, and the answer. Do this while it is in front of you.

## 3. Record the decisions you took yourself

A decision you took is written up the same way a question is, so the spec reads as
one list and the implementation phase treats both alike. Write it as the question you
would have asked, the options you weighed, and the answer you chose - marked as
yours, with the reason.

Include every choice from the **yours to decide** pile. A choice from the **already
answered** pile only gets an entry when a reader would otherwise expect a question
there; one line naming what settled it is enough.

## 4. Write the specification

```bash
date +%F        # the YYYY-MM-DD prefix - never guess today's date
```

Path: `docs/specs/YYYY-MM-DD-feature-name.md`, the name in lowercase kebab-case,
three or four words describing the feature and not the request ("bulk-price-edit",
not "user-wants-faster-prices"). Create the file once context is agreed and grow it
through the session; do not wait until the end.

The document contains exactly these sections:

```markdown
# <Feature name>

Status: draft | agreed
Date: YYYY-MM-DD
Area: <modules / deploy modes the change touches>

## Context of the change

What exists today in this repository, what it does not do, and why that is being
changed now. Point at real files and README anchors. A reader who has never seen the
conversation must be able to follow from here.

## User request

The user's own request, reformulated into one continuous text: all of their prompts
across the session joined, tidied and ordered, with the noise removed.

Nothing in this section may be information the user did not give. No inferred
requirement, no invented constraint, no solution of yours, no scope you added. If two
prompts contradict each other, keep both and note which came later.

## Decisions

One subsection per decision, in the order taken - the rounds put to the user and the
ones decided without asking, in one list.

### <the question, verbatim as asked - or as it would have been asked>

| Option | What it means |
|---|---|
| <label> | <the description offered or weighed> |
| <label> | <the description offered or weighed> |

**Answer: <the option chosen>** - plus the reasoning. For a round put to the user:
the user's own reasoning, and if they chose "Other", their words, not a paraphrase.
For a decision taken without asking, say so in the same line - **Answer: <option>
(decided without asking)** - and give the reason it beat the alternative and what
would have made it worth a question.

## High-level plan

The change described as a handful of phases or workstreams, each with what it
delivers and what it depends on. Prose and headings, not a task list, no file names,
no ordering finer than "this before that".

## Architecture decisions

The parts that are expensive to change later: the seam between modules, the data
structures and where they live, the schema, which side of the client/worker split
owns what, what gets a capability flag, what invariant a test has to enforce. State
each decision and the reason it beat the alternative.

## Weaknesses and risks

Honest and specific. For each: what could go wrong, how likely, what it costs, and
what would reduce it. Include the questions deliberately left open and what has to
happen before they can be answered. A decision you took without asking that the user
may disagree with belongs here too, named as such.

## Out of scope

What this change explicitly does not do, so a later reader does not read the gaps as
oversights.
```

No section is dropped. If a section has nothing in it, say so in one line and say
why - an empty "Weaknesses and risks" means you did not look.

Style: ASCII only, present tense, tables where a table reads better than prose, and
keep it under roughly 300 lines. This is a document a person reads before agreeing to
the work, not a transcript.

## 5. Hand back

Report the path, then summarise in a few lines: what was decided, which decisions the
user made and which you took on your own. Name explicitly the two or three of your
own decisions the user is most likely to want to overturn, so a disagreement surfaces
now and not during implementation. Say plainly that this is the planning phase and
that implementation is a separate step - do not start it, and do not offer to start
it in the same breath as the summary.

**Commit the spec on the main branch and push it there.** A design session creates no
branch of its own: the spec is a document about work that has not started, so it
belongs where everyone reads it, not on a branch nobody has merged. Switch to the
repository's main branch (`master` or `main`, whatever it uses), take it up to date,
commit the spec on its own with a message naming the feature, and push.

```bash
git switch <main>          # master or main, whatever the repository uses
git pull --ff-only
git add docs/specs/YYYY-MM-DD-feature-name.md
git commit -m "docs: spec for <feature name>"
git push
```

A spec never rides along in a code commit, and never waits on a branch for an
implementation that may never come. If the session started on a feature branch, say
in the hand-back that the spec went to the main branch and the branch is untouched.
If the repository forbids pushing to its main branch, stop there: report that the
spec is written but not pushed and let the user say where it should go - do not
invent a branch for it.

The implementation phase is what cuts a branch, from a main branch that already
carries this spec - `vjp-implement-spec` names it `claude/<feature-name>-<hash>`.
