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

Both are invoked explicitly. Neither starts on its own from an ordinary feature request.

## Install

As a plugin, from this repository:

```
/plugin marketplace add janproch/virtual-jp
/plugin install virtual-jp@virtual-jp
```

Or copy a single skill into a project - the skills have no dependency on this repository
or on each other:

```bash
cp -r skills/jp-brainstorming /path/to/project/.claude/skills/
```

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
  <skill-name>/
    SKILL.md          frontmatter (name, description) + the instructions
```

## Contributing a skill

- One directory per skill under `skills/`, named exactly as the skill's `name`.
- `SKILL.md` frontmatter carries `name` and a `description` that says both what the skill
  does and when it should be used - the description is the only thing Claude reads when
  deciding whether to load the skill.
- Skills are repository-agnostic: no project name, no fixed build command, no assumption
  about the language. Take conventions from the target repository's `CLAUDE.md`.
- ASCII only, present tense, imperative instructions.

## License

MIT - see [LICENSE](LICENSE).
