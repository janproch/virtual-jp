# virtual-jp

Software development skill set by JP - a collection of [Claude Code](https://claude.com/claude-code)
skills that split a change into two explicit phases: decide it with the user, then build
exactly what was decided. Alongside them are the skills that keep the result flowing
between branches.

The two phases are deliberately separate. Planning produces one document and no code;
implementation reads that document, treats its decisions as settled, and writes down what
really happened.

## Skills

| Skill | Phase | What it does |
|---|---|---|
| [`vjp-brainstorming`](skills/vjp-brainstorming/SKILL.md) | plan | Gathers context, settles every important decision with the user one question at a time, and writes `docs/specs/YYYY-MM-DD-feature-name.md`. Produces no code. |
| [`vjp-implement-spec`](skills/vjp-implement-spec/SKILL.md) | build | Picks an agreed spec, carries out its plan and decisions in code, runs the repository's own checks, and writes `docs/impl/YYYY-MM-DD-feature-name.md`. |
| [`vjp-night-worker`](skills/vjp-night-worker/SKILL.md) | batch | Asks once which not-yet-implemented specs to build, then implements them one by one - oldest spec first, each on its own branch, each landed and pushed on the main branch before the next starts - without asking anything else. |
| [`vjp-update-virtual-jp`](skills/vjp-update-virtual-jp/SKILL.md) | maintain | Refreshes a repository's vendored copies of these skills from this repository, removes the ones no longer shipped, and commits and pushes the result on the main branch. |
| [`vjp-reintegrate-master`](skills/vjp-reintegrate-master/SKILL.md) | integrate | Merges the freshly fetched main branch into the current feature branch, resolves the conflicts, runs the repository's own checks and commits the merge. |
| [`vjp-merge-claude-branches`](skills/vjp-merge-claude-branches/SKILL.md) | integrate | Lists unmerged `claude/*` branches from the last two weeks, asks which to land, then for each one merges the main branch in, verifies it, and merges it back. |

All of them are invoked explicitly. None starts on its own from an ordinary feature
request.

## Install

**Vendored, and kept up to date.** Run this once in the target repository; from then on
"update virtual JP" installs every skill and removes what is no longer shipped:

```bash
mkdir -p .claude/skills/vjp-update-virtual-jp &&
curl -fsSL https://raw.githubusercontent.com/janproch/virtual-jp/master/skills/vjp-update-virtual-jp/SKILL.md \
  -o .claude/skills/vjp-update-virtual-jp/SKILL.md &&
git add .claude/skills/vjp-update-virtual-jp &&
git commit -m "chore: bootstrap virtual-jp update skill"
```

The commit is part of the command on purpose: the update refuses to run against an
uncommitted `.claude/`, so a bootstrapped copy that was never committed would stop it on
its first invocation. Then, in that repository:

```
> update virtual JP
```

**As a plugin**, leaving the skills outside the target repository:

```
/plugin marketplace add janproch/virtual-jp
/plugin install virtual-jp@virtual-jp
```

**Or one skill by hand** - the skills have no dependency on this repository or on each
other:

```bash
cp -r skills/vjp-brainstorming /path/to/project/.claude/skills/
```

## Updating

`vjp-update-virtual-jp` clones this repository, reads [`index.json`](index.json) - the
manifest naming every file shipped and where it lands - and installs exactly that. It
takes the latest commit on the default branch; there is no pinning and no release step.

What it touches, and nothing else:

- it writes only under `.claude/`, and only paths the manifest names
- it removes every `vjp-*` entry under `.claude/` before installing, which is how a skill
  dropped from this repository disappears from your project
- it also removes `jp-*` entries, the prefix these skills shipped under before the rename,
  so a repository vendored back then is not left holding both copies of every skill
- anything in `.claude/` not named `vjp-*` or `jp-*` - your `settings.json`, your own
  skills - is left alone
- it refuses to start unless `.claude/` is clean and tracked by git, because the removal
  is a real delete and git is the only undo
- it makes one commit containing only `.claude/`, on the main branch, and pushes it there

## Use

```
> use the brainstorming skill for adding CSV import
  ... a few rounds of questions ...
  -> docs/specs/2026-08-27-csv-import.md

> implement the spec from the brainstorming session
  ... implementation, checks, notes ...
  -> docs/impl/2026-08-27-csv-import.md

> run night worker
  ... one round of checkboxes, then a queue of specs built and landed ...
  -> a merge commit and docs/impl/ notes per spec
```

The spec is what the user agreed to; the notes are what was actually built, including what
is missing and what is weak about it.

## Layout

```
.claude-plugin/
  marketplace.json    this repository as a plugin marketplace
  plugin.json         this repository as a plugin
skills/
  vjp-<skill-name>/
    SKILL.md          frontmatter (name, description) + the instructions
scripts/
  build-index.py      generates index.json from skills/
index.json            distribution manifest: every shipped file and its target path
```

## Contributing a skill

- One directory per skill under `skills/`, named exactly as the skill's `name`, which
  starts with `vjp-`. The prefix is load-bearing: `vjp-update-virtual-jp` removes what this
  repository no longer ships by sweeping `vjp-*` entries out of a project's `.claude/`,
  with no record of the previous install to consult.
- Run `python3 scripts/build-index.py` after adding, renaming or removing a skill, and
  commit the regenerated `index.json` with the change.
- `SKILL.md` frontmatter carries `name` and a `description` that says both what the skill
  does and when it should be used - the description is the only thing Claude reads when
  deciding whether to load the skill.
- Skills are repository-agnostic: no project name, no fixed build command, no assumption
  about the language. Take conventions from the target repository's `CLAUDE.md`.
- ASCII only, present tense, imperative instructions.

## License

MIT - see [LICENSE](LICENSE).
