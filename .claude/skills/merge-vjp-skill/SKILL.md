---
name: merge-vjp-skill
description: Land the current virtual-jp work branch on the main branch of this repository - refresh the branch, run the repository's checks, bump the plugin version in .claude-plugin/plugin.json and .claude-plugin/marketplace.json to the same value, then merge and push. Use ONLY when the user explicitly asks for it ("merge skill", "use the merge skill", "merge to master", "land this branch on master", "release virtual-jp"). A request to merge some other branch, to reintegrate master into this branch, or to open a pull request is not an invocation. Internal to the virtual-jp repository; it is never shipped to a repository that installs these skills.
---

# Merge a branch to the main branch of virtual-jp

Every landing carries a version bump. Internal to this repo - stays under `.claude/skills/`.

## 1. Preconditions

```bash
git status --porcelain && git rev-parse -q --verify MERGE_HEAD   # both must print nothing
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
```

`MAIN` empty - `git remote set-head origin --auto`, else whichever of master/main exists.
Stop if HEAD is `$MAIN`. Never stash, reset or force.

## 2. Merge main into the branch

`git fetch origin --prune && git merge --no-ff --no-edit "origin/$MAIN"`. Resolve conflicts
keeping both intentions; version conflicts resolve to the higher version.

## 3. Bump the version

Same string in `.claude-plugin/plugin.json` (top-level `version`) and
`.claude-plugin/marketplace.json` (`version` of the `virtual-jp` plugin entry):
- **major** - shipped skill removed/renamed, or `manifest.json` changes what/where it installs
- **minor** - skill added, or a skill's behaviour changes
- **patch** - wording, docs, README

State the level and why; ask only if the branch genuinely straddles two levels.

## 4. Checks

```bash
for f in .claude-plugin/plugin.json .claude-plugin/marketplace.json manifest.json; do
  python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" || echo "BROKEN: $f"
done
python3 - <<'PY'
import json, pathlib, re
plugin = json.load(open('.claude-plugin/plugin.json'))['version']
market = [p for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']
          if p['name'] == 'virtual-jp'][0].get('version')
print('versions match' if plugin == market else f'MISMATCH: {plugin} vs {market}')
readme = pathlib.Path('README.md').read_text()
for d in sorted(pathlib.Path('skills').iterdir()):
    name = re.search(r'^name:\s*(\S+)', (d / 'SKILL.md').read_text(), re.M).group(1)
    print(d.name,
          'name ok' if name == d.name else f'NAME MISMATCH: {name}',
          'prefix ok' if d.name.startswith('vjp-') else 'PREFIX MISSING',
          'in README' if f'skills/{d.name}/SKILL.md' in readme else 'NOT IN README')
PY
```

Fix anything failing before merging.

## 5. Commit, merge, push

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: release v<version>"
git switch "$MAIN" && git merge --ff-only "origin/$MAIN"
git merge --no-ff --no-edit <branch>
git log --oneline "origin/$MAIN".."$MAIN"
git push -u origin "$MAIN" && git push -u origin <branch>
```

A conflict in the merge back means something moved - `git merge --abort`, report. Rejected
push - fetch, `--ff-only`, retry; refused - stop and report.

## 6. Report

Version before/after and why; what came in from `$MAIN` and conflicts; check results;
commits that reached `$MAIN`; what was pushed.
