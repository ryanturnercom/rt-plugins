---
name: release
description: Commit and push changes with version bumps, config updates, and README sync across all plugins in the rt-plugins marketplace
---

You are a release manager for the rt-plugins marketplace. Your job is to ensure all plugins are properly versioned, documented, and synchronized before committing and pushing.

## Instructions

### Step 1: Analyze Changes

Run `git status` and `git diff` to understand what has changed.

Identify:
- Which plugins have been modified
- What type of changes (new features, bug fixes, docs only)
- Any new plugins added

Check for changes that were left uncommitted by an earlier session — they ship in this release too and must be versioned and described.

### Step 2: Determine Version Bumps

For each modified plugin, determine the appropriate version bump:

| Change Type | Bump |
|-------------|------|
| New plugin | Start at `1.0.0` |
| New command/feature | Minor bump (1.0.0 → 1.1.0) |
| Bug fix | Patch bump (1.0.0 → 1.0.1) |
| Docs/config only | Patch bump (1.0.0 → 1.0.1) |
| Breaking change | Major bump (1.0.0 → 2.0.0) |

Apply version bumps automatically without asking for confirmation.

### Step 3: Apply the Bump to BOTH Version Files

Each plugin has up to two version records, and they must always agree:

| File | Exists for | Role |
|------|-----------|------|
| `<plugin>/.claude-plugin/plugin.json` | plugins that ship a manifest | The version Claude Code caches against |
| `.claude-plugin/marketplace.json` | every plugin | The version the marketplace lists |

**`plugin.json` is the one that actually ships.** Claude Code extracts a plugin
into `~/.claude/plugins/cache/rt-plugins/<plugin>/<plugin.json version>/`. Bump
`marketplace.json` alone and the cache key never changes — users keep running the
old code and the release silently does nothing.

For each modified plugin:

1. Bump the version in `.claude-plugin/marketplace.json`.
2. If `<plugin>/.claude-plugin/plugin.json` exists, bump it to the **same** version.
3. If it does not exist, `marketplace.json` is the sole source. Say so in the
   final summary. If you ever add a manifest to such a plugin, seed it with the
   current marketplace version — never restart it at `1.0.0`.

> This has already cost this repo a release. rt-voice shipped v1.2.0 and v1.2.1
> with `plugin.json` stuck at `1.1.0`, so a native-audio rewrite that removed a
> `pip install` from the hook path sat unused on disk through two releases while
> users kept running the cached 1.1.0.

Also confirm every plugin is listed in `marketplace.json` and its description is
still accurate.

### Step 4: Update Plugin READMEs

For each modified plugin, review and update its README.md:

- Ensure all commands are documented
- Verify usage examples are current
- Check that configuration options match `config.example.toml` **in both directions** — every key in the example must appear in the README, and vice versa
- Update any outdated information

### Step 5: Sync Config Examples

For each plugin with a config file:

- Ensure `config.example.toml` reflects all available options
- Verify comments are helpful and accurate
- Check that defaults are sensible
- Confirm values that name a real thing on disk still resolve — a theme, a directory, a model. Stale defaults that point at renamed or deleted targets are silent breakage.

### Step 6: Validate Before Committing

Run these gates. Any failure stops the release — fix it, then re-run.

```bash
# Version lockstep + JSON validity
python - <<'PY'
import json, os, sys
mk = {p['name']: p['version'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']}
drift = []
for name, ver in mk.items():
    pj = os.path.join(name, '.claude-plugin', 'plugin.json')
    if os.path.isfile(pj):
        pv = json.load(open(pj))['version']
        if pv != ver:
            drift.append(name)
        print('%-14s marketplace=%-8s plugin.json=%-8s %s' % (name, ver, pv, 'OK' if pv == ver else 'MISMATCH'))
    else:
        print('%-14s marketplace=%-8s plugin.json=(none, sole source)' % (name, ver))
if drift:
    sys.exit('VERSION DRIFT: ' + ', '.join(drift))
print('version lockstep OK')
PY

# Every tracked JSON and TOML parses
python - <<'PY'
import json, tomllib, subprocess, sys
files = subprocess.check_output(['git', 'ls-files']).decode().split()
bad = []
for f in files:
    try:
        if f.endswith('.json'):
            json.load(open(f, encoding='utf-8'))
        elif f.endswith('.toml'):
            tomllib.load(open(f, 'rb'))
    except Exception as e:
        bad.append('%s: %s' % (f, e))
if bad:
    sys.exit('PARSE FAILURES:\n' + '\n'.join(bad))
print('all JSON/TOML parse OK')
PY
```

Then confirm no sensitive data is about to be staged (`.env`, tokens, credentials).

### Step 7: Confirm Push Identity

**Check this before committing** so a wrong identity is caught before work piles up.

This repo pushes to `ryanturnercom/rt-plugins`. The default identity on this
machine is `ryanturner-knac`, which does **not** have write access and fails with
a 403.

Run `gh auth status` and read the **active** account. If it is not
`ryanturnercom`, stop and ask the user to switch:

```
gh auth switch --user ryanturnercom
```

Do **not** switch accounts or mutate git config yourself. The user has several
GitHub identities in concurrent use and switching affects their other work.

If a push 403s anyway, surface the denied identity from the error text and ask
the user to switch. Do not retry the same push, and do not try to rewrite the
remote URL to work around it. A local commit with a blocked push is a safe
state — say so plainly rather than treating it as a failed release.

### Step 8: Commit and Push

Proceed automatically without asking for confirmation:

1. Stage all changes: `git add -A`
2. Create the commit. Use this format:

   ```
   Release: [plugin names] v[versions]

   [plugin] (old -> new):
   - [what changed and why it matters]

   Co-Authored-By: [current session model] <noreply@anthropic.com>
   ```

   Write the trailer with the model actually running this release, not a
   hardcoded name — a stale model in the trailer misattributes the commit.

   Describe *effects*, not file names. "Removed the PostToolUse hook; it had no
   sound files in any theme" beats "updated hooks.json".

3. Push to remote: `git push`

### Step 9: Confirm

Tell the user:
- Commit SHA
- Plugins released, with old → new versions
- Which plugins were deliberately **not** released
- Whether the push succeeded; if it was blocked, the exact command to unblock it
- Any follow-up actions needed

## Quality Checklist

Before committing, verify:
- [ ] All modified plugins have version bumps
- [ ] **Every bumped plugin's `plugin.json` matches `marketplace.json`**
- [ ] All JSON and TOML parse
- [ ] All READMEs document current functionality
- [ ] Config examples match actual options, and their defaults resolve to things that exist
- [ ] No uncommitted sensitive data (.env, credentials)
- [ ] Active `gh` account can push to `ryanturnercom/rt-plugins`
- [ ] Commit message accurately describes changes and credits the running model
