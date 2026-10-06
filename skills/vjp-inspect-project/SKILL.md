---
name: vjp-inspect-project
description: Inspect a project along four axes - the language and technology stack it is built on, how it is deployed, whether its documentation and root README.md carry the basic information, and what its tests cover - then publish the findings as an HTML artifact. Use ONLY when the user explicitly asks for it ("inspect project:", "inspect project", "inspect the project", "run the project inspection", "use the inspect project skill"). A question about one of those areas ("what language is this?", "how do I run the tests?", "is there a README?") is not an invocation - answer it directly instead.
---

# Inspect a project

Read-only review along four axes - stack, deployment, documentation, tests - published as
one HTML artifact.

## Rules

- Change nothing in the repo: no edits, files, commits, installs. Write the HTML to the
  scratchpad.
- Do not run tests, builds or deploys (unless the user asks). Configs, lockfiles and CI
  files are the evidence.
- Every finding cites a path, config key or job name; drop claims without evidence. Never
  infer from a name alone (a `test/` dir with no tests is a finding).
- Distinguish missing from not applicable (a library needs no deploy).
- Grade on evidence, not tone.

## Axes

First state what kind of repo it is (app, service, library, plugin, monorepo, docs) - every
axis is graded against that.

1. **Stack** - languages (confirm extension counts by opening real files; ignore vendored/
   generated), runtime and pinned version, framework, data store, build tool, package
   manager, external services. Flag unpinned runtimes and dead configs. Per package in a
   monorepo.
2. **Deployment** - the path from merge to running system, each step naming the file that
   does it: CI jobs on main/tags (read the jobs), containers, platform/IaC config, registry
   publishing for libraries. Docs' claims last; where they disagree with files, files win
   and it is a finding. List gaps: manual steps, undocumented secrets, no rollback.
3. **Documentation** - root `README.md` checklist, each present / thin / absent: what it is,
   who it is for, requirements, install, run, test, build, configuration, deploy, layout,
   license. Every documented command must exist in the manifest/build file. Then other docs:
   reachable from the README? stale?
4. **Tests** - runner and its config, rough count and which modules have none, kinds (unit/
   integration/E2E), whether CI runs them (job name), coverage only if measured (never
   estimate), skipped/quarantined tests. No suite = `missing`.

Grades: `good` (actionable without asking anyone), `partial`, `missing`, `n/a` - each with a
one-sentence justification. Then an ordered **fix list** of actions, each naming its file.

## Artifact

One page, published with `Artifact` (if unavailable: write the `.html` to the scratchpad and
say it was not published). Title: "<repo> Project Inspection". Sections in order: header
(repo, branch, short commit, date, repo kind); summary cards with the four grades; fix list;
one section per axis; README checklist table; **What was not inspected** (always present).
Follow the artifact-design skill if available; keep it self-contained, theme-aware, readable
at phone width, with grades shown as text labels, not colour alone.

## Hand back

Artifact URL, the four grades, the top 2-3 fixes. State the repo was not modified and nothing
was run. Name any axis graded on thin evidence and what would settle it.
