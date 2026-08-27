# Virtual JP update skill

Spec: docs/specs/2026-08-27-virtual-jp-update-skill.md
Date: 2026-08-27
Status: implemented
Area: skills/jp-update-virtual-jp, scripts/, index.json, CLAUDE.md, README.md

## What was done

All four phases of the spec are in place.

- `scripts/build-index.py` generates `index.json` from `skills/`, with `--check` for the
  repository's checks. It enforces the naming rule where files enter the system: a skill
  directory not named `jp-*`, or a target with no `jp-` component directly inside a
  `.claude/` directory, fails generation rather than shipping something a later update
  could never remove.
- `index.json` at the repository root, listing the three skills with source path, target
  path and sha256.
- `skills/jp-update-virtual-jp/SKILL.md` - the explicitly invoked skill: establish the
  calling repository, refuse on a dirty or ignored `.claude/`, shallow-clone the default
  branch, validate the whole manifest before deleting anything, sweep `jp-*` at depth 1
  and 2 under `.claude/`, install, verify by hash, commit `.claude/` alone, report from
  `git status`.
- `CLAUDE.md` gained the layout entries, the `jp-` naming convention with the reason it
  is load-bearing, and the manifest check. `README.md` gained the bootstrap one-liner,
  the skill table row, an "Updating" section stating exactly what an update touches, and
  the regenerate-the-manifest rule for contributors.

Checks run, all green: the three JSON files parse; every `SKILL.md` frontmatter `name`
equals its directory name; `README.md` lists exactly the skills in `skills/`;
`python3 scripts/build-index.py --check` reports the manifest current; the bootstrap
one-liner passes `bash -n`.

The skill is instructions rather than code, so its procedure was verified by running it
by hand against simulated calling repositories: a repo carrying a stale `jp-brainstorming`,
a dropped `jp-oldskill`, a dropped `.claude/agents/jp-thing.md`, its own `settings.json`
and its own non-jp skill. The dropped files were removed at both depths, the stale one
updated, the three skills installed and hash-verified, and `settings.json` and the
project's own skill left untouched. Re-running produced an empty `git status` and no
commit. Both refusal paths were exercised.

## What is missing

Nothing the spec asked for. Two things the spec named as possible but not exercised are
deliberately not built: the generator walks `skills/` only, so shipping
`.claude/agents/jp-*` or `.claude/commands/jp-*` needs a generator change, and there is
no CI, so the checks still depend on someone running them.

## Known problems

- **The bootstrap conflicted with the clean-tree refusal.** A curled `SKILL.md` is
  untracked, so the very first invocation would have refused. Resolved by committing
  inside the documented bootstrap command, and the skill names this case explicitly when
  it stops. It is a wrinkle a user can still hit by curling the file by hand.
- **The first gitignore probe was wrong and would have hidden the worst case.**
  `git check-ignore` says nothing about a path that is already tracked, and in a repo
  that ignores `.claude/` and never committed it, `git status` reports clean. The two
  checks together would have passed and the sweep would have deleted with no undo. The
  skill now uses `git check-ignore --no-index` combined with a tracked-file count, and
  step 7 additionally verifies every installed target is tracked so a partly ignored
  `.claude/` is not reported as "already up to date".
- **The bootstrap URL points at `master`** and does not resolve until this branch is
  merged. Anyone following the README before then gets a 404.
- **Nothing tests the skill.** Its commands were verified once, by hand, in this session.
  A later edit to `SKILL.md` can drift from what actually works and no check will notice.
- **The skill overwrites itself mid-run**, as the spec accepted: a change to the
  procedure takes effect one invocation late.
- **Always-latest has no rollback.** A bad push to `master` reaches every project that
  updates that day; the only recovery is reverting the commit in the calling repository.

## Recommended follow-ups

- Add a GitHub Actions workflow running the four checks, which is what turns the
  generator's guarantee from a habit into a rule.
- Add a shell test that runs the skill's procedure against a fixture repository, so the
  commands in `SKILL.md` cannot rot unnoticed.
- Add the optional ref argument that was left out, once there is a reason to pin - it is
  the only answer to a bad push reaching every project.
- Extend the generator beyond `skills/` when the first non-skill file needs shipping.

## Changelog

- Update JP's skills in your project with "update virtual JP" - it installs the current
  set and removes the ones no longer published
- Install the skills into a project with a single command, then keep them current from
  the chat
