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

### Step 3: Update marketplace.json

Update `.claude-plugin/marketplace.json` with new versions for each modified plugin.

Ensure:
- All plugins are listed
- Versions match the determined bumps
- Descriptions are accurate and current

### Step 4: Update Plugin READMEs

For each modified plugin, review and update its README.md:

- Ensure all commands are documented
- Verify usage examples are current
- Check that configuration options match config.example.toml
- Update any outdated information

### Step 5: Sync Config Examples

For each plugin with a config file:

- Ensure `config.example.toml` reflects all available options
- Verify comments are helpful and accurate
- Check that defaults are sensible

### Step 6: Commit and Push

Proceed automatically without asking for confirmation:

1. Stage all changes: `git add -A`
2. Create commit with message format:
   ```
   Release: [plugin names] v[versions]

   - [Summary of changes per plugin]

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
   ```
3. Push to remote: `git push`

### Step 7: Confirm

Tell the user:
- Commit SHA
- Plugins released with versions
- Any follow-up actions needed

## Quality Checklist

Before committing, verify:
- [ ] All modified plugins have version bumps
- [ ] marketplace.json is valid JSON
- [ ] All READMEs document current functionality
- [ ] Config examples match actual options
- [ ] No uncommitted sensitive data (.env, credentials)
- [ ] Commit message accurately describes changes
