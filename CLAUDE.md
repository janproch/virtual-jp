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
- `manifest.json` - the distribution manifest: the directories and files this repository
  ships and where each one lands in a calling repository. It lists `skills/` as a whole,
  carries no checksums and no per-file inventory, so adding, renaming or removing a skill
  does not touch it. Edited by hand, only when what gets shipped changes shape.

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
- Every skill directory is named `vjp-*`. This is not cosmetic: `vjp-update-virtual-jp`
  copies skills into a calling repository's `.claude/` and removes what this repository
  no longer ships by sweeping every `vjp-*` entry there, with no record of the previous
  install to consult. A shipped file that lands outside a `vjp-` prefixed component
  directly inside a `.claude/` directory could never be removed again, so the update
  skill validates the manifest against that rule and refuses the whole manifest if an
  entry breaks it.

## Checks

There is no build and no test suite. After changing anything:

- `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` and the same for
  `marketplace.json` and `manifest.json` - all three must parse.
- Every `skills/*/SKILL.md` has frontmatter whose `name` equals its directory name.
- Every directory under `skills/` is named `vjp-*`, so the sweep in
  `vjp-update-virtual-jp` can remove it again.
- `README.md` lists exactly the skills present in `skills/`.
