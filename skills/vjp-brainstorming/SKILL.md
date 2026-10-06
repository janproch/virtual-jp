---
name: vjp-brainstorming
description: Lead the user through high-level planning of a change - gather context, settle every important decision with AskUserQuestion, then write a specification to docs/specs/YYYY-MM-DD-feature-name.md, including any database or persistent storage changes for the user to review, and link it in the hand-back. Use ONLY when the user explicitly asks for it ("brainstorm", "brainstorming", "use the brainstorming skill", "let's brainstorm this"). Never start it on your own from an ordinary feature request.
---

# Brainstorm a change into a specification

Planning only. The single deliverable is `docs/specs/YYYY-MM-DD-feature-name.md`; no code.
The spec records what **the user** decided, not what you would have decided.

## Rules

- Write no source code. Create or switch no branch.
- After every `AskUserQuestion` end the turn. Ambiguous answer - ask again; "Other" text is
  the decision verbatim.
- No implementation steps in the spec (files, signatures, commits, estimates).
- Schema and persistent storage changes (tables, columns, indexes, migrations, files,
  buckets, KV keys, browser storage of user data) are decisions, not detail: propose them
  yourself and put them to the user. Only pure caches are exempt; when unsure, it is storage.

## Process

1. **Context first.** Read `CLAUDE.md`, the relevant code, existing `docs/specs/` and
   `docs/`. State back what you understood and what exists, including whether the change
   needs schema or storage changes.
2. **Decide in rounds**, in dependency order (what it is -> where it lives -> storage ->
   presentation). Ask about scope, which module it extends, data model and migration,
   user-facing shape, deploy modes, backwards compatibility, what is deferred. Never ask
   what the repository already decides. Each round: 2-4 options with trade-off
   descriptions, recommendation first marked `(Recommended)`, at most 2-3 related decisions
   per call. Typically 3-8 rounds.
3. **Write the spec as you go** - append each round to *Decisions* right after the answer.
   Get the date with `date +%F`. Name: 3-4 word kebab-case feature slug.

## Spec format

```markdown
# <Feature name>

Status: draft | agreed
Date: YYYY-MM-DD
Area: <modules / deploy modes touched>

## Context of the change
What exists, what it lacks, why change now. Real files. Readable without the conversation.

## User request
All of the user's prompts joined and tidied. Nothing the user did not say. Contradictions
kept, later one noted.

## Decisions
### <question verbatim>
| Option | What it means |
|---|---|
| ... | ... |
**Answer: <choice or free text verbatim>** - plus the user's reasoning.

## High-level plan
A few phases/workstreams in prose, what each delivers and depends on. No file names.

## Database and persistent storage
Per store: kind, structure (fields, types, keys, relations, indexes), what it holds, who
reads/writes, lifetime, migration of existing data. Or one line saying nothing new is stored.

## Architecture decisions
Expensive-to-change choices and why each beat the alternative.

## Weaknesses and risks
Specific: what, likelihood, cost, mitigation; open questions.

## Out of scope
```

No section dropped; an empty one says why in one line. ASCII, present tense, under ~300 lines.

## Hand back

- Link the spec as a markdown link by repo-relative path; if a render-to-panel tool exists
  (e.g. `SendUserFile` with `display: "render"`), send the file through it.
- Summarise the decisions; call out *Database and persistent storage* when not empty.
- Say implementation is a separate step; do not start or offer it.
- Commit the spec alone (`docs: spec for <feature>`) on the **current** branch and push
  (`-u origin HEAD` if no upstream). Never force. On the main branch, do not commit - say
  it is uncommitted and let the user decide.
