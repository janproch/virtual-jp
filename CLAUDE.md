# virtual-jp

This repository is a collection of Claude Code skills, packaged as a plugin. It contains
no application code - the deliverable is the skill instructions themselves.

## Layout

- `skills/<skill-name>/SKILL.md` - one directory per skill; the directory name matches the
  `name` in the frontmatter.
- `.claude-plugin/plugin.json` - this repository as an installable plugin.
- `.claude-plugin/marketplace.json` - this repository as a plugin marketplace, listing the
  plugin with `"source": "./"`.
- `README.md` - the skill table and install instructions; update it whenever a skill is
  added, renamed or removed.
- `index.json` - the distribution manifest: every file this repository ships, its target
  path in a calling repository, and its hash. Generated, never edited by hand.
- `scripts/build-index.py` - generates `index.json` from `skills/`. Run it after adding,
  renaming or removing anything under `skills/`.

## Conventions for skills

- The frontmatter `description` decides when the skill loads. It states what the skill does
  **and** when to use it, including the phrases that should trigger it and, where the skill
  must not fire on its own, what does not count as an invocation.
- Skills are repository-agnostic. No project name, no hardcoded build or test command, no
  assumed language or package manager - a skill takes those from the target repository's
  own `CLAUDE.md` and manifest.
- Instructions are imperative and addressed to the agent running the skill.
- ASCII only, present tense.
- A skill stands alone: it may reference another skill by name, but must not require it.
- Every skill directory is named `jp-*`. This is not cosmetic: `jp-update-virtual-jp`
  installs skills into a calling repository's `.claude/` and removes what this repository
  no longer ships by sweeping every `jp-*` entry there, with no record of the previous
  install to consult. A shipped file whose target carries no `jp-` prefixed component
  directly inside a `.claude/` directory could never be removed again, so
  `scripts/build-index.py` refuses to put one in the manifest.

## Checks

There is no build and no test suite. After changing anything:

- `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` and the same for
  `marketplace.json` - both must parse.
- Every `skills/*/SKILL.md` has frontmatter whose `name` equals its directory name.
- `README.md` lists exactly the skills present in `skills/`.
- `python3 scripts/build-index.py --check` - `index.json` must match what the generator
  produces. Run `python3 scripts/build-index.py` to refresh it, and commit the result
  alongside the change that caused it.
