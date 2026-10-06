---
name: vjp-systematic-bugfix
description: Fix a bug the disciplined way - reproduce it first, find the real root cause, work out whether it is a regression or a bug by design, cover it with a regression test that fails before the fix, then write the fix report to docs/fixes/YYYY-MM-DD-bug-name.md. Use ONLY when the user explicitly asks for it ("systematic bugfix", "make a systematic bugfix", "systematic bugfix:", "fix this systematically", "use the systematic bugfix skill"). A plain bug report, a stack trace, a failing test or "this is broken, fix it" is not an invocation - fix those directly instead.
---

# Fix a bug systematically

## Rules

- No fix before a reproduction. If it does not reproduce, report what you tried and what you
  need, make no fix, stop.
- Fix the cause, not the symptom. If the cause cannot be repaired here, label the patch a
  mitigation.
- The regression test must be seen **failing** on unfixed code before the fix.
- Never skip, weaken or delete a test.
- One bug per run; anything else found is a follow-up.
- An origin commit is only what blame/diff/bisect showed - otherwise "unknown".
- After `AskUserQuestion` end the turn.

## Process

1. **Record the report** in the user's own words (observed, expected, where, verbatim errors/
   steps). If reproduction is impossible without missing info, ask one question and end the turn.
2. **Reproduce** - prefer a failing test, then a script, then manual steps. Record the exact
   command and output; reduce to the minimal case; show a neighbouring case that works.
3. **Root cause** - follow actual values to the first wrong state; read history. State the
   cause in one sentence with no "probably". Remove instrumentation afterwards.
4. **Origin** (bounded: a few commands, at most one bisect): `git blame` + `git show` on the
   cause lines; past moves use `git blame -w -C` / `git log --follow -p`; unchanged since
   written = by design; `git bisect run` only if the repro is one scriptable command. Too
   costly - "unknown" with one line why. For a regression, read what the breaking commit was
   for so the fix does not undo it.
5. **Regression test** at the level the cause lives, in the repo's test layout. Run it, record
   the failure.
6. **Fix** - smallest change removing the cause. Run the new test, nearby tests, then the
   repo's full checks. Claim a pre-existing failure only after verifying it on the base. Look
   for the same cause elsewhere (follow-ups). If the fix is architectural (moves an invariant,
   changes a contract, replaces a mechanism), decide it with the user first.

## Report

`docs/fixes/YYYY-MM-DD-<bug-slug>.md` - today's date (`date +%F`), slug names the bug, not
the fix (`csv-import-drops-last-row`). One page:

```markdown
# <Bug in one line>

Date: YYYY-MM-DD
Status: fixed | mitigated
Area: <modules>
Origin: regression in <commit> | by design | unknown

## Reported problem
The user's report, errors and steps quoted as given.

## Reproduction
Exact command and trimmed output; required conditions; the working control case.

## Root cause
File and lines, the wrong state, the reasoning error.

## Origin
Regression: commit hash, date, subject, what it did, how it broke this. By design: the
unhandled case and since when. Unknown: what was searched, why it stopped.

## The fix
What changed and why it removes the cause; rejected alternatives, one line each.

## Regression tests
Each test by path/name, what it pins, and its pre-fix failure output. Checks run afterwards.

## Consequences and risks
Behaviour changes, affected callers, remaining risk; or one line why it is safe.

## Follow-ups
Same cause elsewhere, missing tests, design weaknesses. Or "None."

## ADR
Only architectural decisions this fix implemented: numbered, each with Context, Decision,
Alternatives, Consequences. Usually "None - the fix changes no architecture."
```

## Commit and hand back

Commit fix + test together, then the report alone (`docs: fix report for <bug>`). Stay on the
current feature branch; on the main branch first `git switch -c "claude/fix-<bug-slug>-$(openssl rand -hex 3)"`
(unless the repo has its own convention). `git push -u origin <branch>`; retry network
failures 4x (2s, 4s, 8s, 16s); never force.

Report: root cause in one sentence, origin, the change, the test and that it failed first,
check results, branch (pushed), report path.
