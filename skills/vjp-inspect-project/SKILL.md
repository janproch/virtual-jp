---
name: vjp-inspect-project
description: Inspect a project along four axes - the language and technology stack it is built on, how it is deployed, whether its documentation and root README.md carry the basic information, and what its tests cover - then publish the findings as an HTML artifact. Use ONLY when the user explicitly asks for it ("inspect project:", "inspect project", "inspect the project", "run the project inspection", "use the inspect project skill"). A question about one of those areas ("what language is this?", "how do I run the tests?", "is there a README?") is not an invocation - answer it directly instead.
---

# Inspect a project

This skill inspects a repository and reports on four things: **what it is built
with**, **how it gets deployed**, **what its documentation tells a newcomer**, and
**what its tests actually cover**. The deliverable is one HTML artifact - a page the
user can read, keep and share.

It is a read-only review. Nothing here assumes a particular project, language,
runtime or CI system: everything reported comes from files that exist in the checkout
in front of you.

## Hard rules

- **Explicit invocation only.** A question about the stack, the deploy or the tests is
  not an invocation. Only run when the user names a project inspection.
- **Never change the repository.** No edits, no new files inside the working tree, no
  commits, no branches, no dependency install, no formatter, no code generator. The
  HTML file is written to a scratch directory outside the project.
- **Never run the project's tests, build or deploy.** You report what the repository
  says about them; you do not execute them. Reading a config, a lockfile or a CI
  workflow is the evidence, not a run. The single exception is a command the user
  explicitly asks you to run during the inspection.
- **Every finding cites evidence.** A path, a file name, a config key, a workflow job
  - something a reader can open. A claim with nothing behind it is dropped, not
  softened.
- **Never infer a stack from a name.** A directory called `docker` proves nothing
  until a Dockerfile is read. A `test` folder with no test files is a finding, not a
  test suite.
- **Distinguish "missing" from "not applicable".** A library with no deploy is
  complete; a service with no deploy is a gap. Say which one you are looking at
  before grading the deploy axis.
- **Never grade on tone.** The grades are defined in step 6 and follow the evidence,
  including when the answer is unflattering. Do not round a `missing` up to `partial`
  because the project is otherwise good.
- **One artifact per run.** Every axis lands on the same page. Do not publish four
  pages, and do not report the findings only as terminal text.

## 1. Establish the ground

Before judging anything, find out what you are looking at.

```bash
git rev-parse --show-toplevel     # the repository root - work from here
git log -1 --format='%H %ad %s' --date=short
git ls-files | wc -l
```

Read the repository's own account of itself first, because it decides what the rest
of the inspection means:

- `CLAUDE.md` and any `.claude/` instructions - conventions, commands, the checks the
  repository asks for
- `README.md` at the root
- the manifest of whatever ecosystem this is - the one file that names the project and
  its dependencies

Then get the shape of the tree without walking every file:

```bash
git ls-files | sed 's|/.*||' | sort | uniq -c | sort -rn | head -30
git ls-files | grep -Ei '(^|/)(readme|license|contributing|changelog|dockerfile|makefile)'
```

State in one paragraph what kind of repository this is - application, service,
library, plugin, monorepo, documentation - because every axis below is graded against
that answer.

## 2. Language and technology stack

Find what the code is actually written in, and what it is built on.

```bash
git ls-files | sed -n 's/.*\.\([A-Za-z0-9]\{1,10\}\)$/\1/p' | sort | uniq -c | sort -rn | head -20
```

Extension counts are the starting point, not the answer: generated files, vendored
directories and fixtures inflate them. Confirm each candidate language by opening a
real source file in it.

Then find the technology around the code, from the files that declare it - a package
or project manifest, a lockfile, a runtime version pin, a build or task file, a
container definition, a compose or orchestration file, a database migration
directory, a framework's own config. For each one you find, record:

- **what it is** - the file, by path
- **what it says** - the framework, the runtime version, the database, the build tool
- **whether it is live** - a manifest referenced by the build is live; a config for a
  tool nothing runs is a leftover, and saying so is a finding

Report the stack as: primary language(s) with the evidence, runtime and its pinned
version, framework, data store, build tooling, package manager, and anything notable
alongside (queues, caches, external services declared in config). Where a version is
pinned nowhere, say that - an unpinned runtime is a finding on this axis.

In a monorepo, do this per package, then summarise. Do not average several stacks
into one sentence that describes none of them.

## 3. Deployment

Answer one question: **if this change is merged, how does it reach the place it
runs?** Look for the answer in this order, and stop describing hopes once you find
facts:

1. **CI/CD definitions** - workflow and pipeline files under whatever directory this
   host uses. Read the jobs, not the file names: which trigger on the main branch or
   a tag, what they build, what they push, where they push it, what gates them
   (approval, environment, secret).
2. **Container and orchestration** - Dockerfile and its base image, compose files,
   chart or manifest directories, and what image tag the deploy consumes.
3. **Platform config** - a hosting platform's config file, a serverless definition, an
   infrastructure-as-code directory, a service unit, a deploy script under the
   repository's own scripts directory.
4. **Publishing** - for a library or a plugin, "deploy" means a registry release: the
   publish job, the version field, the tag convention, the marketplace or plugin
   manifest.
5. **The documentation's claim** - what the README or a deploy document says. Read it
   last and check it against 1-4; where the two disagree, the files win and the
   disagreement is a finding.

Report the path from commit to running system as a short sequence of steps, each step
naming the file that performs it. Then report what is missing on this axis: no
automated deploy, manual steps that only exist in someone's head, a secret with no
documented source, an environment that no file mentions, a rollback nobody described.

If the repository genuinely deploys nothing - a library consumed as source, a
documentation repository - say so explicitly and grade this axis `n/a` rather than
`missing`.

## 4. Documentation, starting with the root README

The root `README.md` must exist and must carry the basic information. Check it
against this list, and record for each item whether it is present, thin or absent,
with the heading or line that covers it:

| Item | What counts as present |
|---|---|
| What the project is | A first paragraph naming the project and what it does, in plain terms |
| Who it is for / what problem it solves | Enough for a newcomer to know whether they need it |
| Requirements | Runtime, versions, services or accounts needed before anything runs |
| Install / setup | The commands that take a fresh checkout to a working state |
| Run | How to start the thing locally, with the real command |
| Test | How to run the test suite, with the real command |
| Build | How to produce the deployable or distributable artifact, where one exists |
| Configuration | The environment variables or config files that must be set, and where their values come from |
| Deploy | How it reaches production, or a link to the document that says |
| Layout | What the top-level directories are for, for a repository big enough that this is not obvious |
| License | A statement, and a LICENSE file it agrees with |

Verify, do not skim: every command quoted in the README must correspond to something
real - a script in the manifest, a target in the build file, a binary the project
declares. A documented command that does not exist is a finding, and the check for it
is reading the manifest, never running it.

Then look at the rest of the documentation: other markdown at the root, a `docs/`
tree, per-package READMEs, an architecture or decision record directory, comments
that carry design rationale. Report what exists, and check two things about it -
whether it is reachable from the README, and whether it is stale (a document
describing a directory, command or service the tree no longer has). Note in one line
what a newcomer would still have to ask a person for.

## 5. Tests

Find the tests, then find out what they are worth.

```bash
git ls-files | grep -Ei '(^|/)(tests?|spec|__tests__|e2e|it)(/|$)|[._-](test|spec)\.[A-Za-z0-9]+$' | head -50
```

Establish, with evidence:

- **the runner** - the test framework and where it is configured; the command the
  repository itself documents for running it
- **the count and the spread** - roughly how many test files, and which parts of the
  tree they cover. Name the significant modules with no tests next to them; that gap
  is the most useful thing on this axis.
- **the kinds** - unit, integration, end-to-end, snapshot, property, contract. A suite
  that is entirely one kind is a finding either way: only unit tests means the wiring
  is untested, only end-to-end means failures will be slow and vague.
- **whether CI runs them** - the workflow job that invokes the runner, by name. Tests
  that exist but are not wired into CI are close to tests that do not exist.
- **coverage** - only if the repository measures it: a coverage config, a threshold, a
  published report. Never estimate a coverage percentage yourself; "not measured" is
  the honest answer and a finding of its own.
- **the state of the suite** - tests skipped, marked pending, quarantined or commented
  out, and fixtures or snapshots that look abandoned.

A repository with no test suite at all is graded `missing` on this axis, whatever its
other qualities, and the report says which part of the code that is riskiest.

## 6. Grade each axis

Give each of the four axes exactly one grade, from this scale:

| Grade | Meaning |
|---|---|
| `good` | Present, current, and enough for a newcomer to act on without asking a person |
| `partial` | Present but incomplete, stale, or undocumented in a way that costs the reader time |
| `missing` | Absent, or so thin that it does not answer the axis at all |
| `n/a` | The axis does not apply to this kind of repository - say in one line why |

Each grade carries a one-sentence justification naming the evidence that decided it.
Then produce **the ordered fix list**: the concrete gaps found, most valuable first,
each one line, each naming the file it would live in. This list is what the user acts
on, so it holds actions ("pin the Node version in `.nvmrc`"), not observations ("the
Node version is unpinned").

## 7. Publish the HTML artifact

The report is one self-contained HTML page, published with the `Artifact` tool.

Write the file to the session's scratchpad directory - never inside the repository -
then publish it:

- pass a one-sentence `description` and, on a first publish, a `favicon`
- put a `<title>` at the top of the file: the repository name plus "Project Inspection"
- if a skill covering artifact design is available in the session, follow it; the page
  below is the minimum either way

Where the `Artifact` tool is not available in the session, write the same page as a
standalone `.html` file in the scratchpad, hand the user its path, and say plainly
that it was not published.

**The page contains, in this order:**

1. **Header** - the repository name, the branch and short commit it was inspected at,
   the date, and one sentence saying what kind of repository it is.
2. **Summary** - the four axes as four cards, each with its grade and its
   one-sentence justification. This is what the page is read for; it comes before any
   detail.
3. **Fix list** - the ordered actions from step 6, numbered, each naming its file.
4. **One section per axis**, in the order of steps 2-5, each holding the findings and
   the evidence - paths, config keys, job names - as short prose plus a table where a
   table reads better.
5. **README checklist** - the table from step 4, item by item, with present / thin /
   absent against each.
6. **What was not inspected** - the limits of this run: what you did not read, what
   could not be verified without running something, what a person still has to
   confirm. Never leave this section out.

**Page rules**, so the artifact renders correctly wherever it is opened:

- Write the page content only: a `<title>`, a `<style>`, then the body markup. No
  doctype, no `<html>`, `<head>` or `<body>` tags of your own.
- Everything inline - CSS in the `<style>` block, no external stylesheet, no script
  from a CDN, no web font, no image URL. The page must render with no network.
- Theme-aware: define the light palette as custom properties on `:root`, redefine
  them under `@media (prefers-color-scheme: dark)` guarded as
  `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`. Give
  `body` an explicit background from those properties.
- Responsive to about 400px: one side gutter set once on a wrapper, cards that wrap to
  a single column, and any table inside its own `overflow-x: auto` container.
- Carry the grade in text as well as colour - a `good` / `partial` / `missing` /
  `n/a` label on every card and heading - so the page survives being printed or read
  without colour.
- Paths and commands in `<code>`, and long file lists in a scrollable block rather
  than a wall of text.

Keep the writing on the page the same as the writing in the repository's documents:
ASCII only, present tense, specific. The page is a review a person reads once and
acts on, not a dashboard.

## 8. Hand back

Report in a few lines: the artifact URL (or the file path, where nothing was
published), the four grades on one line each, and the first two or three items from
the fix list. Do not restate the report - it is on the page.

Say explicitly that the repository was not modified, and that nothing was built,
tested or deployed during the inspection. If an axis was graded on thin evidence - a
deploy described only in prose, a test suite you could not map to CI - say which one
and what would settle it.
