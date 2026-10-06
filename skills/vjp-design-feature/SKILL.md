---
name: vjp-design-feature
description: Design a change into a specification with as few questions as possible - gather context, ask only the questions that cannot be answered from the repository or the request, decide the rest yourself and record why, then write docs/specs/YYYY-MM-DD-feature-name.md in the same format the brainstorming skill produces. Use ONLY when the user explicitly asks for it ("design feature: ...", "design the feature", "use the design feature skill"). Never start it on your own from an ordinary feature request; a plain feature request, a bug report or "what do you think about X" is not an invocation.
---

# Design a change into a specification

Planning only. Produces the same `docs/specs/YYYY-MM-DD-feature-name.md` as
`vjp-brainstorming`, but asks as few questions as possible. Every decision is still
recorded - the user's and yours.

## Rules

- Write no source code. Create no branch.
- After every `AskUserQuestion` end the turn. "Other" text is the decision verbatim.
- No implementation steps in the spec.
- Never hide a decision you took: it goes in *Decisions*, marked as yours.

## Process

1. **Context first** - `CLAUDE.md`, relevant code, existing `docs/specs/` and `docs/`, how
   comparable features were shaped. Each fact found is a question saved.
2. **Sort every open choice** into:
   - *already answered* by the repo, its conventions or the request - use it;
   - *yours* - decide and record with the alternative and reason;
   - *the user's* - only when you cannot answer it from repo/request/precedent **and** the
     wrong answer is expensive to undo (data model, scope boundary, user-facing contract,
     dropping compatibility). Only these are asked.
   Aim for 0-3 rounds; zero is fine. Question format: 2-4 options with trade-offs,
   recommendation first `(Recommended)`, at most 2-3 related decisions per call.
3. **Write the spec** as you go; date from `date +%F`, name a 3-4 word kebab-case slug.

## Spec format

```markdown
# <Feature name>

Status: draft | agreed
Date: YYYY-MM-DD
Area: <modules / deploy modes touched>

## Context of the change
What exists, what it lacks, why change now. Real files. Readable without the conversation.

## User request
All of the user's prompts joined and tidied. Nothing the user did not say.

## Decisions
One subsection per decision, asked or not, in order taken.
### <question verbatim, or as it would have been asked>
| Option | What it means |
|---|---|
| ... | ... |
**Answer: <option>** - the user's reasoning; or
**Answer: <option> (decided without asking)** - why it won, what would have made it worth asking.

## High-level plan
A few phases/workstreams in prose. No file names.

## Architecture decisions
Expensive-to-change choices (seams, data structures, schema, ownership, invariants) and why.

## Weaknesses and risks
Specific risks and open questions, including your own decisions the user may reject.

## Out of scope
```

No section dropped; an empty one says why. ASCII, present tense, under ~300 lines.

## Hand back

- Report the path; summarise which decisions the user made and which you made; name the
  2-3 of yours most likely to be overturned. Say implementation is separate; do not start it.
- Commit and push the spec on the **main branch**: `git switch <main> && git pull --ff-only`,
  commit the spec alone (`docs: spec for <feature>`), push. If the session started on
  another branch, say it is untouched. If pushing to main is forbidden, stop and report -
  do not invent a branch.
