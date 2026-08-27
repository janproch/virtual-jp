# virtual-jp

Software development skill set by JP - a collection of [Claude Code](https://claude.com/claude-code)
skills that split a change into two explicit phases: decide it with the user, then build
exactly what was decided.

The two phases are deliberately separate. Planning produces one document and no code;
implementation reads that document, treats its decisions as settled, and writes down what
really happened.

## Skills

| Skill | Phase | What it does |
|---|---|---|
| [`jp-brainstorming`](skills/jp-brainstorming/SKILL.md) | plan | Gathers context, settles every important decision with the user one question at a time, and writes `docs/specs/YYYY-MM-DD-feature-name.md`. Produces no code. |
| [`jp-implement-spec`](skills/jp-implement-spec/SKILL.md) | build | Picks an agreed spec, carries out its plan and decisions in code, runs the repository's own checks, and writes `docs/impl/YYYY-MM-DD-feature-name.md`. |
| [`jp-update-virtual-jp`](skills/jp-update-virtual-jp/SKILL.md) | maintain | Refreshes a repository's vendored copies of these skills from this repository, removes the ones no longer shipped, and commits the result. |

All three are invoked explicitly. None starts on its own from an ordinary feature
request.

## Install

**Vendored, and kept up to date.** Run this once in the target repository; from then on
"update virtual JP" installs every skill and removes what is no longer shipped:

```bash
mkdir -p .claude/skills/jp-update-virtual-jp &&
curl -fsSL https://raw.githubusercontent.com/janproch/virtual-jp/master/skills/jp-update-virtual-jp/SKILL.md \
  -o .claude/skills/jp-update-virtual-jp/SKILL.md &&
git add .claude/skills/jp-update-virtual-jp &&
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
cp -r skills/jp-brainstorming /path/to/project/.claude/skills/
```

## Updating

`jp-update-virtual-jp` clones this repository, reads [`index.json`](index.json) - the
manifest naming every file shipped and where it lands - and installs exactly that. It
takes the latest commit on the default branch; there is no pinning and no release step.

What it touches, and nothing else:

- it writes only under `.claude/`, and only paths the manifest names
- it removes every `jp-*` entry under `.claude/` before installing, which is how a skill
  dropped from this repository disappears from your project
- anything in `.claude/` not named `jp-*` - your `settings.json`, your own skills - is
  left alone
- it refuses to start unless `.claude/` is clean and tracked by git, because the removal
  is a real delete and git is the only undo
- it makes one local commit containing only `.claude/`, and never pushes

## Use

```
> use the brainstorming skill for adding CSV import
  ... a few rounds of questions ...
  -> docs/specs/2026-08-27-csv-import.md

> implement the spec from the brainstorming session
  ... implementation, checks, notes ...
  -> docs/impl/2026-08-27-csv-import.md
```

The spec is what the user agreed to; the notes are what was actually built, including what
is missing and what is weak about it.

## Layout

```
.claude-plugin/
  marketplace.json    this repository as a plugin marketplace
  plugin.json         this repository as a plugin
skills/
  jp-<skill-name>/
    SKILL.md          frontmatter (name, description) + the instructions
scripts/
  build-index.py      generates index.json from skills/
index.json            distribution manifest: every shipped file and its target path
```

## Contributing a skill

- One directory per skill under `skills/`, named exactly as the skill's `name`, which
  starts with `jp-`. The prefix is load-bearing: `jp-update-virtual-jp` removes what this
  repository no longer ships by sweeping `jp-*` entries out of a project's `.claude/`,
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
