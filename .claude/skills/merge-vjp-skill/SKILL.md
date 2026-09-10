---
name: merge-vjp-skill
description: Land the current virtual-jp work branch on the main branch of this repository - refresh the branch, run the repository's checks, bump the plugin version in .claude-plugin/plugin.json and .claude-plugin/marketplace.json to the same value, then merge and push. Use ONLY when the user explicitly asks for it ("merge skill", "use the merge skill", "merge to master", "land this branch on master", "release virtual-jp"). A request to merge some other branch, to reintegrate master into this branch, or to open a pull request is not an invocation. Internal to the virtual-jp repository; it is never shipped to a repository that installs these skills.
---

# Merge a branch to the main branch of virtual-jp

This skill is the only way work reaches the main branch of this repository. Every
landing carries a version bump, so the plugin version says which set of skills a
consumer has.

This skill is internal. It lives in `.claude/skills/`, never under `skills/`, because
`manifest.json` ships `skills/` as a whole and nothing here belongs in another
repository.

## 1. Check where you are

```bash
git status --porcelain          # must be empty
git rev-parse -q --verify MERGE_HEAD    # must print nothing
git rev-parse --abbrev-ref HEAD
MAIN=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's|^origin/||')
```

If `MAIN` is empty, try `git remote set-head origin --auto`, else fall back to
whichever of `origin/master` / `origin/main` exists.

Stop and report if the tree is dirty, a merge is in progress, or `HEAD` is already
`$MAIN` - there is nothing to land from the main branch onto itself. Never stash,
reset or force on your own initiative.

## 2. Bring the main branch into the work branch

```bash
git fetch origin --prune
git merge --no-ff --no-edit "origin/$MAIN"
```

Resolve every conflict by hand, keeping both sides' intentions. Leave no conflict
marker behind (`git diff --check`). If the version fields conflict, resolve them to
the higher of the two versions; step 3 raises it again from there.

## 3. Bump the version, in both places

The version lives twice and the two must always be equal:

- `.claude-plugin/plugin.json`, top-level `version`
- `.claude-plugin/marketplace.json`, `version` on the `virtual-jp` entry in `plugins`

Read the current value, decide the next one from what the branch actually changes,
and write the same string into both files:

- **major** - a shipped skill is removed or renamed, or `manifest.json` changes what
  it installs or where it lands; anything that makes an existing install stale in a
  way the update skill cannot repair on its own.
- **minor** - a skill is added, or an existing skill's behaviour changes.
- **patch** - wording, documentation, README, or a fix inside a skill that does not
  change what it does.

Say which level you picked and why. Ask the user with `AskUserQuestion` only when the
branch genuinely straddles two levels; otherwise decide it and report the decision.

## 4. Run the repository's checks

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

Every skill directory under `skills/` is `vjp-*`, its frontmatter `name` equals its
directory name, and `README.md` lists exactly the skills present. Fix anything that
fails before merging; do not land a broken manifest.

## 5. Commit the bump

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore: release v<version>"
```

Only the two version files belong in this commit. If the branch has other uncommitted
work at this point, something went wrong in step 1 - stop and report.

## 6. Merge back and push

```bash
git switch "$MAIN"
git merge --ff-only "origin/$MAIN"
git merge --no-ff --no-edit <branch>
git log --oneline "origin/$MAIN".."$MAIN"
git push -u origin "$MAIN"
git push -u origin <branch>
```

The merge must not conflict - step 2 made `$MAIN` an ancestor. If it does, something
moved underneath: `git merge --abort` and report rather than resolving blind. Keep
`--no-ff` so each branch stays one identifiable merge commit. Show the log before
pushing. Never `--force`. If the push is rejected, `git fetch origin` and
`git merge --ff-only "origin/$MAIN"`, then push again; if that fast-forward is
refused, stop and report.

## 7. Report

The version before and after and why that level; what the merge from `$MAIN` brought
in and what conflicted; the check results; which commits reached `$MAIN`; what was
pushed and what is still only local.
