# Codex config sync

Agent Kit syncs explicit keys from `config/codex/global.toml` into the real local
`~/.codex/config.toml`. It does not own entire tables or capture app state.
Arrays are single values. Nested tables are merged by leaf key, including inline
tables. Generated agent registrations own only their `config_file` and
`description` fields; capture never imports those fields into portable settings.

## Preview, apply, and capture

On Windows:

```powershell
.\scripts\setup.ps1 preview-codex-config
.\scripts\setup.ps1 link
.\scripts\setup.ps1 capture-codex-config
```

On macOS/Linux, use `./scripts/setup.sh` with the same actions. Preview is read-only,
including on a fresh machine. `link`, `link-ai-agents`, and `compile-agents` apply
config changes as part of their existing workflows. Capture updates only keys
already declared in the portable source. Add new portable keys by editing that
source deliberately, then commit and pull as usual.

Each machine keeps its own last-synced per-key baseline in
`~/.codex/agent-kit-config-baseline.json`. Keep this baseline out of Git.

| Preview status | Apply | Capture |
| --- | --- | --- |
| APPLY: only repo changed, or local key is absent on first adoption | Apply repo value | Leave repo change pending |
| LOCAL: only local changed, or existing value differs on first adoption | Preserve local; report it | Import it for a portable key |
| CONFLICT: both changed differently | No writes | No writes |
| RELEASE: key removed from the source | Preserve machine value; stop tracking | Preserve machine value; stop tracking |

Equal values converge without a conflict, even when both sides changed.
Unowned keys are never imported or removed. Deleting an owned local key and then
capturing releases it from the portable source. Removing a generated role also
releases its registration fields; it does not silently delete local registrations.
Remove obsolete registrations explicitly if the corresponding files are retired.

To resolve a conflict, edit the named key in either the repo or local config so
both express your chosen value, then rerun preview. Values are not printed in
previews or conflict errors. A local-only change does not block unrelated repo
updates. Exit status is zero for successful apply/capture/preview, including
reported local-only changes, and nonzero for conflicts or invalid inputs.

## Existing installations

The first apply adopts a version-2 per-key baseline and removes old managed-block
marker comments. It preserves all values, including unrecognized entries inside
old markers. Existing differing owned values remain local until explicitly
captured or made equal to the repo. Old hash-only baselines cannot reconstruct
past values, so migration does not guess which differing side is authoritative.
Malformed or incomplete marker pairs fail without writes. Once migration finishes,
marker placement has no role in ownership.

Removing `sandbox_mode` from the portable source releases permission policy to
each machine. It does not reset an existing local permission choice.

## Write protection and dependencies

The editor uses vendored tomlkit 0.15.1 (MIT), with no pip installation and no
additional runtime dependencies. Python 3.11+ remains the existing requirement.
The vendored package preserves TOML structure, comments, and unmodified values.

Apply and capture lock out other Agent Kit sync processes. Before writing, they
check all inputs for changes and recheck the target before atomically replacing
it. Changed files get timestamped backups; the baseline is updated last. A second
sync with unchanged inputs is a no-op. If a process stops between writes, rerunning
sync accepts already-converged values.

This is optimistic concurrency, not a lock shared with Codex. A Codex write in
the narrow interval between the final check and replacement can still race.
Avoid changing app settings during apply/capture. Detected stale input produces
an error instead of an automatic retry or overwrite. Codex's config API was
considered, but it only permits writes to its user config and cannot implement
capture back into the repo through the same editor.
