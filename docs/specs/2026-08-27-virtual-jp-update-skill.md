# Virtual JP update skill

Status: agreed
Date: 2026-08-27
Area: skills/ (new skill `jp-update-virtual-jp`), repository root distribution manifest, README

## Context of the change

`virtual-jp` is a skill-only repository. It ships two skills today,
`skills/jp-brainstorming/SKILL.md` and `skills/jp-implement-spec/SKILL.md`, and packages
itself twice: as a plugin (`.claude-plugin/plugin.json`) and as a single-plugin marketplace
(`.claude-plugin/marketplace.json`). `README.md` documents both routes into a project:

- install as a plugin (`/plugin marketplace add janproch/virtual-jp`), which keeps the
  skills outside the target repository, or
- copy a skill directory into the target repository's `.claude/skills/`, which vendors it.

The second route is the one people actually use, because a vendored skill is visible in the
target repository's own history and travels with a clone. It has no update story at all:
`cp -r` is a one-shot, nothing records where the copy came from, and a skill that is renamed
or dropped upstream stays behind in every project that ever copied it. There is also no
machine-readable statement of what this repository distributes - the skill list exists only
as a table in `README.md` and as directory names under `skills/`.

`CLAUDE.md` fixes the conventions any new skill has to meet: one directory per skill named
after its frontmatter `name`, a `description` that says what the skill does and when it
fires, repository-agnostic instructions with no hardcoded build command, ASCII only, present
tense, and a skill that stands alone. The repository has no build and no test suite; its
checks are that both JSON manifests parse, that every `SKILL.md` name matches its directory,
and that `README.md` lists exactly the skills present.

## User request

Create a skill `jp-update-virtual-jp`. It is invoked on explicit request only (for example
"update virtual JP"). It downloads all `jp-*` skills from GitHub, and also other files, into
the repository that invokes it - that repository ends up with copies of the `jp-*` skills and
of any files they link to. Add an `index.json` listing the downloadable files if that is
appropriate. Solve deleting files that virtual-jp no longer uses.

## Decisions

### How does jp-update-virtual-jp get the files out of GitHub and into the calling repository?

| Option | What it means |
|---|---|
| Shallow git clone (Recommended) | `git clone --depth 1` into a temp dir, copy out, delete the temp dir. One command, no per-file rate limits, works with private repos through the user's existing git credentials. Costs a git dependency and a full-repo download even when one skill changed. |
| index.json + raw file fetch | Fetch `index.json` from raw.githubusercontent.com, then curl each listed file. No git needed and only listed files ever travel, so the manifest is the hard contract. Costs one request per file and breaks on a private repo. |
| Tarball download + extract | Fetch the branch tarball from codeload.github.com and untar it. One request, no git and no `.git` dir to clean up. Costs tar availability and still pulls the whole repo, so a manifest is still needed to know what is distributable. |

**Answer: Shallow git clone** - the user's words: "I don't understand. Calling repo just
overwrites files in working copy, data are downloaded from public repo (virtual-jp), so
there should be no problem. Shallow git clone will be OK". The private-repo and
overwrite-safety trade-offs in the options do not apply: virtual-jp is public and the
calling repo's working copy is simply overwritten.

### What role does index.json play?

| Option | What it means |
|---|---|
| Full distribution manifest (Recommended) | One entry per shipped file: source path in virtual-jp, target path in the calling repo, and a content hash. Transport-independent, lets a skill ship linked files outside `skills/`, and doubles as the record that drives deletion. Costs keeping it in sync with the tree. |
| Skill list only | `index.json` names the skills and their versions; each skill directory is then taken wholesale from whatever arrives. Simpler to maintain, but linked files outside a skill directory have no way to be declared and target paths are fixed by convention. |
| No index.json | Derive everything from the `skills/jp-*` directory listing at fetch time. Nothing to keep in sync and nothing to forget to update, but no way to ship a file outside `skills/`, and no per-file hash to detect local edits. |

**Answer: Full distribution manifest**


### Where in the calling repository may index.json place files?

| Option | What it means |
|---|---|
| Anywhere under `.claude/` (Recommended) | Skills land in `.claude/skills/jp-*/`, and the manifest may also ship `.claude/agents/`, `.claude/commands/` or a shared reference doc. One owned root, still bounded, and a reader knows every path the update can touch. |
| `.claude/skills/jp-*/` only | A skill's linked files must live inside its own skill directory. Deletion becomes a clean namespace sweep and a skill still stands alone, but virtual-jp can never ship a repo-level agent, slash command or shared template. |
| Any path under the repo root | Each manifest entry declares its own target, so a skill could ship `docs/templates/` or a CI file. Most flexible, but the update now writes outside `.claude/` and the calling repo must trust the manifest not to clobber project files. |

**Answer: none of the offered options - the user rejected the premise.** Their words:
"Don't store it in calling repo. Simply go though downloaded index.json and do what's
neccessary. In case of deleted files, in index.json is neccessary to hold historically
deleted files (we want not to pollute calling repo)". The calling repository carries no
state of its own: the update reads the freshly downloaded `index.json` and acts on it, and
`index.json` itself records the files virtual-jp used to ship so those can be removed. The
footprint question proper is re-asked below.

### How does the update remove files virtual-jp no longer ships?

| Option | What it means |
|---|---|
| Save the applied manifest (Recommended) | Write the fetched `index.json` into the calling repo as a lock file with the source commit. Next run deletes every path present in the old manifest and absent from the new one. Exact, works for any target path, and the deletion shows up in the calling repo's own diff. Costs one tracked state file. |
| Namespace sweep, no state | Delete every `.claude/skills/jp-*` directory, then write the new set from scratch. Nothing to keep in sync, self-healing after an old manual `cp -r`, but it only reaches that one namespace and every run rewrites the whole set even when nothing changed. |
| Saved manifest plus namespace sweep | Use the lock file for exact deletion, and additionally drop any `.claude/skills/jp-*` directory the new manifest does not name. Catches orphans copied in before this skill existed and still cleans wider paths. Costs carrying both mechanisms and explaining which one acted. |

**Answer: Namespace sweep, no state** - combined with the clarification above. Nothing is
written into the calling repository to remember a previous run. Removal therefore has two
stateless sources: a `.claude/skills/jp-*` directory the freshly downloaded manifest does
not name is dropped, and every path in the manifest's historical-removals list is deleted if
it is present.

### Each manifest entry names where its file lands in the calling repo. How far may those target paths reach?

| Option | What it means |
|---|---|
| Anywhere under `.claude/` (Recommended) | Skills go to `.claude/skills/jp-*/`, and virtual-jp may also ship `.claude/agents/`, `.claude/commands/` or a shared reference doc. One owned root: the update can never touch project source, and a reader knows the blast radius from one line. |
| `.claude/skills/jp-*/` only | Everything a skill needs lives inside its own skill directory, references and scripts included. Smallest possible blast radius and the namespace sweep alone cleans everything, but virtual-jp can never ship a repo-level agent, slash command or shared template. |
| Any path under the repo root | A manifest entry may target `docs/`, a CI file, anything. Lets virtual-jp ship project-level material, but the update writes into the project's own tree and a mistake in `index.json` clobbers real source files. |

**Answer: Anywhere under `.claude/`**

### What shape does the historical-removals list in index.json take?

| Option | What it means |
|---|---|
| Paths with the version that dropped them (Recommended) | Each removed entry carries its target path and the virtual-jp version it disappeared in. The skill deletes them all regardless, but can report what it cleaned, and old entries can be pruned once a stated horizon passes. Costs one extra field per entry. |
| Flat list of paths, append-only | A plain array of target paths that virtual-jp used to ship. Simplest possible thing to maintain and to read. The list only ever grows, and there is no basis for ever pruning it or for telling the user when something went away. |
| No list - derive from git history | Read the history of `index.json` in the clone to compute what vanished. Nothing to maintain by hand and it can never be forgotten. Costs a full clone instead of the shallow one already decided, and makes the update depend on repo history staying intact. |

**Answer: skipped, the question falls away.** The user's words: "skip this - solved by
deleting all jp-* in .claude". There is no removals list. Deletion is one sweep: every
`jp-*` entry anywhere under the calling repo's `.claude/` is removed, then the manifest is
installed fresh. This makes a naming rule load-bearing - every path virtual-jp ships must
put a `jp-` prefixed component directly inside a `.claude/` directory, so that the sweep
finds it and nothing else.

### How does index.json stay correct as skills are added, renamed or dropped in virtual-jp?

| Option | What it means |
|---|---|
| Generator script, run before commit (Recommended) | A small script in virtual-jp walks `skills/` and writes `index.json`; the repository's checks re-run it and fail if the file on disk differs. Cannot drift, and adding a skill is just adding the directory. Costs one script in a repo that currently has no code at all. |
| Hand-maintained, checked by the existing checks | `index.json` is edited by hand like `README.md`, and `CLAUDE.md`'s checks gain a rule that it must list exactly what `skills/` contains. No code in the repo, in keeping with what it is today, but a rename means editing three places and the check only catches it afterwards. |
| No file - built on the fly by the update skill | The skill inspects the clone it just made and derives the file list itself. Nothing to maintain or drift at all, but virtual-jp then has no machine-readable statement of what it distributes, and target paths must be pure convention. |

**Answer: Generator script, run before commit**

### Which version of virtual-jp does an update pull?

| Option | What it means |
|---|---|
| Default branch, always latest (Recommended) | Clone `master` and take what is there. One rule, nothing to release, and "update virtual JP" means exactly what it says. The user gets whatever was pushed last, including a half-finished skill. |
| Latest git tag | Clone, resolve the newest tag, check that out. Updates land only when JP cuts a tag, so `master` stays free for work in progress. Costs a release step that does not exist today, and a repo with no tags yet needs a fallback. |
| Default branch, with an optional ref argument | Latest by default, but "update virtual JP from v0.2.0" or a branch name pins it. Useful for testing a branch before it lands and for pinning a project deliberately. Costs argument parsing and a second code path in the skill. |

**Answer: Default branch, always latest**

### The sweep deletes and overwrites files in the calling repo. What happens when those files have uncommitted local changes?

| Option | What it means |
|---|---|
| Refuse until `.claude/` is clean (Recommended) | Check `git status` for `.claude/` first; if anything there is modified or untracked, stop and name the paths. Git is the only undo the sweep leaves, so this is the one check that makes the deletion recoverable. Costs a refusal in the one case where someone is mid-edit on a `jp-*` skill. |
| Warn and continue | Do the update regardless, but list every `jp-*` path that had local modifications before it was overwritten. Never blocks the user, and the warning tells them what to recover from git. A local tweak still disappears with only a line of output as its record. |
| Overwrite silently | Sweep and copy, no git inspection at all. Simplest possible skill and it matches "the calling repo just overwrites files in its working copy". The calling repo's own diff is the only record, and uncommitted work in `.claude/` is gone. |

**Answer: Refuse until `.claude/` is clean**

### Does the skill commit the update in the calling repository?

| Option | What it means |
|---|---|
| No - leave the changes in the working tree (Recommended) | Report what was added, updated and removed, then stop. The user reviews a real diff and commits it with their own message on their own branch. Costs one manual step after every update. |
| Commit automatically | Stage the `.claude/` changes and commit them alone with a fixed message naming the source commit of virtual-jp. The update is always one reviewable commit and never mixes into a feature commit. Costs the skill making a commit the user did not ask for, on whatever branch they happen to be on. |
| Offer, and commit if the user says yes | Show the summary, then ask. Neither surprises the user nor leaves them work. Costs a question at the end of every run, which is the thing this skill is otherwise trying to avoid. |

**Answer: Commit automatically** - the recommendation was not taken. Together with the
previous answer this gives a clean pairing: the update refuses to start on a dirty
`.claude/`, so the commit it makes contains its own changes and nothing else.

### How does jp-update-virtual-jp get into a repository the very first time, before it exists there to be invoked?

| Option | What it means |
|---|---|
| README one-liner that curls the skill (Recommended) | One documented curl from raw.githubusercontent.com writes `.claude/skills/jp-update-virtual-jp/SKILL.md`, then "update virtual JP" installs everything else including a newer copy of itself. Single command, no manual clone, and the bootstrap only ever fetches one small file. |
| Ask Claude to install it, no fixed command | The README says to tell Claude "install virtual-jp into this repo" and Claude clones and copies the skill by hand. Nothing to maintain and it survives any layout change, but the first install is unrepeatable and depends on Claude improvising it correctly. |
| Keep the existing `cp -r` from a clone | README already documents copying a skill directory out of a clone; bootstrap is that same step aimed at `jp-update-virtual-jp`. No new mechanism at all, consistent with what is written today, but it needs a full manual clone before the first update. |
| Bootstrap script piped to sh | curl an `install.sh` from virtual-jp straight into a shell; it does the whole first install, not just the skill. Shortest path from nothing to fully installed, but it pipes a remote script into a shell and duplicates logic the skill already has. |

**Answer: README one-liner that curls the skill**

## High-level plan

### Phase 1 - the distribution manifest and its generator

Define what virtual-jp distributes, as a file. `index.json` at the repository root lists
every shipped file with its source path in virtual-jp, its target path in a calling
repository, and a content hash; it carries the plugin version alongside. A generator under
`scripts/` walks `skills/jp-*` and writes that file, so the manifest is derived from the tree
and never edited by hand. The repository's checks in `CLAUDE.md` gain a rule that re-running
the generator must leave `index.json` unchanged.

Delivers the manifest and the guarantee it is current. Depends on nothing.

### Phase 2 - the naming rule that makes stateless deletion work

Deletion has no memory to consult, so it has to be able to recognise virtual-jp's files by
their names alone. Every target path virtual-jp ships puts a `jp-` prefixed component
directly inside a `.claude/` directory, and nothing else in a calling repository may be named
that way. This becomes a stated convention in `CLAUDE.md` and a hard failure in the
generator, so a file that could not be cleaned up later can never enter the manifest.

Delivers the invariant the whole removal story rests on. Depends on phase 1.

### Phase 3 - the skill

`skills/jp-update-virtual-jp/SKILL.md`, explicitly invoked, doing in order: establish the
calling repository and refuse if `.claude/` is not clean or not tracked by git; shallow-clone
virtual-jp and note the commit it got; read the manifest and reject it outright if any target
escapes `.claude/` or breaks the naming rule; sweep every `jp-*` entry under `.claude/`;
write the manifest's files; verify what was written against the hashes; commit `.claude/`
alone, naming the source commit; report what was added, updated and removed.

Delivers the update itself. Depends on phases 1 and 2.

### Phase 4 - bootstrap and documentation

The one-line curl that puts the skill into a repository that has never seen it, the skill
table row, and a short section on what an update does and does not touch. The existing
plugin instructions stay as they are; this is the third route in, described alongside them.

Delivers a repeatable first install. Depends on phase 3.

## Architecture decisions

**The manifest is the contract; the clone is only transport.** Nothing is installed because
it happened to be in the clone - only what `index.json` names is written. This keeps the
transport replaceable (raw fetch or tarball later) without touching the skill's behaviour,
and it means adding a file to virtual-jp does not silently start shipping it. It beat
deriving the file list from the clone because a derived list has no place to state a target
path, and no place to state a hash.

**The `jp-` prefix inside `.claude/` is load-bearing, so the generator enforces it.** Removal
carries no state; the sweep finds virtual-jp's files by name alone. That only holds if every
shipped target has a `jp-` prefixed component at depth 1 or 2 under `.claude/`, and if the
convention is enforced where files enter the system rather than trusted at the far end. A
file that violates the rule is rejected at generation time, because by the time it reaches a
calling repository it is already unremovable.

**The target root is `.claude/`, validated before anything is deleted.** The skill checks
every target in the manifest before the first `rm`, and aborts on the whole manifest rather
than skipping a bad entry. Confining targets to `.claude/` means a mistake upstream can
damage a project's Claude configuration but never its source.

**No state in the calling repository.** No lock file, no receipt, no recorded source commit
outside the commit message. The calling repository's git history is the only durable record,
which is also why git is a hard precondition rather than a nice-to-have.

**A clean `.claude/` is the precondition that makes the sweep reversible.** The sweep deletes
without asking; `git checkout` is the only undo, and it only exists if the tree was clean
going in. The refusal and the automatic commit are two halves of one decision: the update
starts from a clean state and ends as exactly one commit containing nothing else.

**Hashes serve the report, not security.** The per-file hash confirms a write landed intact
and distinguishes "updated" from "unchanged" so the summary is honest. It is not a trust
boundary - HTTPS to a public GitHub repository is the trust boundary, and the manifest is
signed by nothing.

**The skill ships itself.** `jp-update-virtual-jp` appears in its own manifest and is
overwritten during its own run. This is deliberate - it is what makes the mechanism
self-maintaining - and its cost is recorded below.

## Weaknesses and risks

**A calling repository that gitignores `.claude/` loses the undo.** The sweep still deletes,
but nothing is tracked, the commit is empty, and there is no way back. Likely enough to
matter - ignoring `.claude/` is a common choice. Cost: silent, unrecoverable loss of whatever
was in there. The skill should treat "the targets are ignored" the same way it treats a dirty
tree and refuse, which turns the worst failure into a message.

**Always-latest means no rollback and no pinning.** A bad push to `master` reaches every
project that updates that day, and the only recovery is reverting the commit in the calling
repository. Cost is bounded because the commit is isolated and reviewable, but there is no
way to say "give me the version from last week" without adding the ref argument that was
deliberately left out.

**The skill overwrites itself mid-run.** The instructions already in context finish the run,
so the visible behaviour is the old version's; the new version only takes effect in a later
session. A change to the update procedure therefore lands one run late, and a change that
breaks the skill is not observable on the run that installs it.

**The clean-tree refusal blocks a real workflow.** Editing a `jp-*` skill in place to try a
change is exactly how someone would experiment, and the skill refuses to run until that work
is committed or thrown away. Reducing it means a force flag, which reintroduces the
unrecoverable case; leaving it means the friction is felt by the person most likely to be
improving the skills.

**The manifest check depends on someone running it.** The repository has no CI, so the
generator's guarantee is only as good as the habit of running the checks in `CLAUDE.md`
before committing. A hand-edited `index.json` sits wrong until the next person notices.
Wiring the checks into an action would close this and is not part of this change.

**Deliberately left open:** whether virtual-jp will ever ship anything other than skills.
The manifest and the naming rule are built to allow `.claude/agents/jp-*` and
`.claude/commands/jp-*`, but nothing exercises that path yet, so the footprint is wider than
the current contents need. This is answerable only when the first non-skill file exists.

## Out of scope

- The plugin and marketplace route is untouched. `/plugin marketplace add` keeps working as
  it does today, and this change does not deprecate it or convert anyone off it.
- No selective install. An update installs everything the manifest names; a repository cannot
  ask for one skill and not another.
- No ref pinning, no dry-run, no uninstall command, and no push - the skill commits locally
  and stops.
- Nothing outside `.claude/` in the calling repository is read or written. The calling
  repository's own `CLAUDE.md` and `README.md` are not updated to mention the installed
  skills.
- Running the update inside virtual-jp itself is not supported and not guarded against;
  virtual-jp keeps its skills in `skills/`, not in `.claude/skills/`.
- No signing, checksum pinning, or provenance beyond HTTPS to a public repository.
