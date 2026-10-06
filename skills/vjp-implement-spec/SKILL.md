---
name: vjp-implement-spec
description: Implement an agreed specification from docs/specs/ - pick the spec, carry out its plan and its decisions in code, then write implementation notes to docs/impl/YYYY-MM-DD-feature-name.md, and commit and push the work on its own branch. Use ONLY when the user explicitly points at a spec ("implement spec", "implement the spec", "implement the plan from the brainstorming session"). A bare "implement this" or "start implementation" with no spec named is not an invocation.
---

# Implement a specification

The spec is the authority: its *Decisions*, storage and architecture sections are settled.

## Rules

- Never re-decide what the spec decided - implement it and question it in *Known problems*.
- Never implement what the spec puts out of scope; gaps become *Recommended follow-ups*.
- Ask only when a decision is impossible as written, two decisions contradict in code, or
  the code drifted so far a decision no longer applies. After `AskUserQuestion` end the turn.
- Never skip, disable or narrow a test to get green.
- The notes file is part of the work; without it the implementation is unfinished.

## 1. Choose the spec

Use the one the user named or this session produced. Otherwise list specs without notes
(a spec is implemented when `docs/impl/` has a file with the same feature slug):

```bash
for spec in docs/specs/[0-9][0-9][0-9][0-9]-*.md; do
  feature=$(basename "$spec" .md | sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}-//')
  ls docs/impl/*-"$feature".md >/dev/null 2>&1 || echo "$spec"
done
```

None - say so and stop. Else one single-select `AskUserQuestion`, up to 4 newest, flag
`Status: draft`; list the rest in the message. End the turn.

## 2. Build it

- Cut the branch before the first commit: `git switch -c "claude/<feature-slug>-$(openssl rand -hex 3)"`
  (unless the repo has its own naming convention). Never keep a session-generated name.
- Read the spec, `CLAUDE.md` and the code it touches; state what moved since it was written.
- Work the *High-level plan* phase by phase; per phase add the tests the spec's invariants
  need, run the relevant checks, and update `README.md`/docs `CLAUDE.md` points at.
- Run the repo's own test, build, lint (and E2E when UI is touched) from `CLAUDE.md` and the
  manifest. Pre-existing failures on the base branch are reported with evidence.
- **E2E test:** write it here when `CLAUDE.md` asks for E2E coverage or the spec does - use
  the existing framework and patterns, drive the real user surface, and confirm it fails
  with the feature disabled. Never introduce an E2E framework; where none exists, *How to
  test* replaces it.

## 3. Implementation notes

`docs/impl/YYYY-MM-DD-<feature-slug>.md` - date is today (`date +%F`), slug identical to
the spec's. A page, not a report:

```markdown
# <Feature name>

Spec: docs/specs/YYYY-MM-DD-feature-name.md
Date: YYYY-MM-DD
Status: implemented | partially implemented
Area: <modules touched>

## What was done
Briefly what now exists and where; checks run and their results.

## Follow-up changes
(Only after a post-hand-back request.) Numbered: the ask in one line + 1-2 sentences how.

## How to test
**Automated coverage.** The E2E test and its command, or "None" and why.
**Setup.** Start command, account/role, seed data, flags.
**Steps.** Numbered single actions naming exact screen/route/field/button, and what to observe.
**Also worth trying.** Edge cases with expected behaviour.
Concrete enough for a human tester or an agent writing an E2E test without asking.

## What is missing
Spec items not built, and why. Or "Nothing - the spec is implemented in full."

## Known problems
Shortcuts, unhandled cases, awkward spec decisions; one line each.

## Recommended follow-ups
Most valuable first, one sentence each.

## Changelog
User-facing lines, present tense, no file or module names. Or "No user-visible changes."
```

## 4. Commit, push, report

Commit the implementation (per phase if clearer), then the notes alone
(`docs: implementation notes for <feature>`). `git push -u origin <branch>`; retry network
failures 4x (2s, 4s, 8s, 16s); never force. Stop at the branch - merging is the caller's step.

Report: spec, branch (pushed), notes path, what is undone, check results, whether an E2E
test was written.

## Follow-up requests

Every later change to the feature updates the notes in the same turn: sections reflect the
current behaviour, *How to test* is corrected (E2E extended under the same rule), a numbered
*Follow-up changes* entry is added, checks are rerun. A request that changes a spec decision
is not a follow-up - ask whether to revise the spec first.
