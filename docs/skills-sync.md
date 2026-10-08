# Skills

`skills/` is the canonical, committed skill tree. Machines receive the same
content through links to `~/.agents/skills`, `~/.claude/skills`, and
`~/.copilot/skills`. Linking works offline; upstream availability is needed
only when installing or refreshing skills.

## Inventory and ownership

| Kind | Manifest entry | Lockfile | Update policy |
| --- | --- | --- | --- |
| Active upstream | `sources[]` | GitHub provenance and folder hash | Refresh with the managed updater |
| Retained snapshot | `retained[]` | Historical provenance when available | Preserve until access and provenance are re-established |
| Kit-owned | `local[]` | None | Edit directly in `skills/` |
| Private | None; folder git-ignored locally | None | Manage on that machine |

[scripts/skills-manifest.json](../scripts/skills-manifest.json) declares the
inventory. [.skill-lock.json](../.skill-lock.json) records upstream provenance
and is linked to `~/.agents/.skill-lock.json`. Vendored files remain the source
of truth for distributed content; hashes describe upstream folders rather than
local host metadata or guarded package normalization.

## Install and update

Use the setup wrappers so installation, reconciliation, and validation stay
consistent. These commands write to the global skill tree linked to this repo.

```bash
# Refresh the declared upstream set
./scripts/setup.sh update-skills

# Select skills from a source interactively
./scripts/setup.sh install-skill owner/repo

# Select one skill; omit -y to retain installer prompts
./scripts/setup.sh install-skill owner/repo -s skill-name -y

# List global skills
./scripts/setup.sh list-skills

# Reconcile an out-of-band installation before validation
./scripts/setup.sh reconcile-skills

# Validate links and inventory; fail on warnings too
./scripts/setup.sh doctor --strict
```

Windows equivalents use `.\scripts\setup.ps1`, for example:

```powershell
.\scripts\setup.ps1 install-skill vercel-labs/agent-skills -s react-best-practices
.\scripts\setup.ps1 update-skills
.\scripts\setup.ps1 doctor --strict
```

Review `skills/`, the manifest, and lockfile diffs together. Do not clone a
nested Git repository into `skills/`. Reconciliation recovers matching entries
from repo/global lockfiles and `~/.agents/.skill-lock.json.backup.*`, declares
installed upstream skills, and removes only empty non-skill directories.

To declare a source manually, add an entry to `sources[]`, then run the updater:

```json
{
  "repo": "owner/repo",
  "skills": ["skill-name"]
}
```

Omitting `skills` installs the entire source. `fullDepth: true` enables discovery
below the installer's normal depth; Microsoft's WinUI source requires it.
Installed names can differ from source names, such as vendor-prefixed Vercel
skills; preserve both the installed name and canonical upstream selector.

## Remove a skill

```bash
./scripts/setup.sh uninstall-skill installed-name
```

The wrapper refuses local skills and sources without explicit selectors.
Those require a manual inventory edit. For upstream removals, it saves the
manifest-removal plan before invoking `npx`, because the CLI mutates the shared
lockfile. Remove archived upstream skills from disk, manifest, and lockfile;
an update alone may leave obsolete folders behind.

## Author a local skill

Create `skills/<name>/SKILL.md` with `name` and a narrowly scoped `description`
in YAML frontmatter. List the folder under `local[]`. Keep optional scripts,
references, assets, and host metadata inside that folder. See
[skill maintenance](skill-maintenance.md) for authoring and review criteria.

[`test-audit`](../skills/test-audit/SKILL.md) is a kit-owned adaptation of
OpenClaw's test-value method. Its attribution and MIT notice stay with the skill;
it uses each project's harness rather than OpenClaw-specific commands.

## Keep private skills machine-local

Add `skills/<private-name>/` to `.git/info/exclude`, never a tracked ignore file.
Place the skill there without using `npx skills add -g`, which records it in the
shared lockfile. Doctor skips git-ignored skills and warns if their names leak
into the tracked lockfile. See [plugins](plugins.md) for machine-local plugin
configuration.

## Package-specific constraints

- SwiftUI Pro includes an obsolete nested entrypoint. The guarded normalizer
  removes only the known root-version `1.1` / nested-version `1.0` duplicate;
  changed packaging stops normalization for review.
- The retained GTK snapshots have no accessible active source. Preserve them
  until provenance and access are re-established.
- Matt Pocock's domain-doc convention is `GLOSSARY.md` / `GLOSSARY-MAP.md`.
  In consuming projects, rename old domain `CONTEXT.md` / `CONTEXT-MAP.md` files
  and update pointers together; unrelated context documents keep their names.
  Run `setup-matt-pocock-skills` per project when configuring tracker and docs.
  Install either the linked skills or Matt's plugin per host to avoid duplicates.
- Adopting Emil's `prototype` alongside Matt's requires source-aware aliases
  across installation, refresh, reconciliation, invocation, and removal on both
  platforms. Keep the existing selection until the installer supports that
  collision without losing provenance.

Doctor checks missing and undeclared skills, manifest/lockfile drift, nested
entrypoints, and nested `.git` directories. Fix inventory drift before further
updates. [vercel-labs/skills](https://github.com/vercel-labs/skills) provides the
underlying installer; wrappers remain the supported kit interface.
