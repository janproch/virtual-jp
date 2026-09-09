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
| [`vjp-design-feature`](skills/vjp-design-feature/SKILL.md) | plan | Produces the same `docs/specs/YYYY-MM-DD-feature-name.md` as brainstorming, but asks only the questions it cannot answer from the repository or the request - the rest it decides itself and records as its own decisions. |
| [`vjp-implement-spec`](skills/vjp-implement-spec/SKILL.md) | build | Picks an agreed spec, carries out its plan and decisions in code, runs the repository's own checks, writes the end-to-end test where the repository asks for one, writes `docs/impl/YYYY-MM-DD-feature-name.md` with the steps to test the feature, and commits and pushes the work on its own `claude/<feature>-<hash>` branch. |
| [`vjp-night-worker`](skills/vjp-night-worker/SKILL.md) | batch | Asks once which not-yet-implemented specs to build, then implements them one by one - oldest spec first, each on its own branch, each landed and pushed on the main branch before the next starts - without asking anything else. |
| [`vjp-systematic-bugfix`](skills/vjp-systematic-bugfix/SKILL.md) | fix | Reproduces a reported bug first, digs to the real root cause, dates the bug as a regression or a bug by design, adds a regression test that is seen failing before the fix, fixes the cause, and writes `docs/fixes/YYYY-MM-DD-bug-name.md`. |
| [`vjp-reintegrate-master`](skills/vjp-reintegrate-master/SKILL.md) | integrate | Merges the freshly fetched main branch into the current feature branch, resolves the conflicts, runs the repository's own checks and commits the merge. |
| [`vjp-merge-claude-branches`](skills/vjp-merge-claude-branches/SKILL.md) | integrate | Lists unmerged `claude/*` branches from the last two weeks, asks which to land, then for each one merges the main branch in, verifies it, and merges it back. |

All of them are invoked explicitly. None starts on its own from an ordinary feature
request.

## Install

This repository is a Claude Code plugin, and that is how it is meant to be installed. Add
the marketplace once, then install the plugin:

```
/plugin marketplace add janproch/virtual-jp
/plugin install virtual-jp@virtual-jp
```

The skills stay outside your repository - nothing is copied into your project's
`.claude/`, so there is nothing of virtual-jp to commit, review or keep in sync there. The
plugin is installed for your Claude Code user, so every repository you open gets the same
skills.

Once installed, the skills are invoked by name in any repository:

```
> design feature: CSV import
```

**Or one skill by hand**, if you want a single skill vendored into one repository - the
skills have no dependency on this repository or on each other:

```bash
cp -r skills/vjp-brainstorming /path/to/project/.claude/skills/
```

A skill copied this way is a snapshot: it is yours to update, and the plugin does not
know about it.

## Updating

Run `/plugin` and use the menu to update the `virtual-jp` marketplace and the installed
plugin. Updating pulls the latest commit on the default branch - there is no pinning and
no release step, so an added, renamed or removed skill arrives with the next update.

Because the plugin's skills live outside your repository, an update changes nothing under
your project's `.claude/` and needs no commit.

## Use

```
> use the brainstorming skill for adding CSV import
  ... a few rounds of questions ...
  -> docs/specs/2026-08-27-csv-import.md

> design feature: CSV import
  ... at most a couple of questions, the rest decided and written down ...
  -> docs/specs/2026-08-27-csv-import.md

> implement the spec from the brainstorming session
  ... implementation, checks, notes ...
  -> docs/impl/2026-08-27-csv-import.md

> run night worker
  ... one round of checkboxes, then a queue of specs built and landed ...
  -> a merge commit and docs/impl/ notes per spec

> systematic bugfix: CSV import drops the last row
  ... reproduce, root cause, failing regression test, fix ...
  -> docs/fixes/2026-08-27-csv-import-drops-last-row.md
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
```

## Contributing a skill

- One directory per skill under `skills/`, named exactly as the skill's `name`, which
  starts with `vjp-`. The prefix keeps these skills recognizable as this plugin's own and
  keeps them from colliding with skills a repository defines for itself.
- `SKILL.md` frontmatter carries `name` and a `description` that says both what the skill
  does and when it should be used - the description is the only thing Claude reads when
  deciding whether to load the skill.
- Skills are repository-agnostic: no project name, no fixed build command, no assumption
  about the language. Take conventions from the target repository's `CLAUDE.md`.
- ASCII only, present tense, imperative instructions.

## License

MIT - see [LICENSE](LICENSE).
