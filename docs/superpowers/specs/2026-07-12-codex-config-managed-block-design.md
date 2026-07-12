# Codex config managed-block design

## Goal

Stop linking the repository's Codex config file directly to `~/.codex/config.toml`.
Keep portable Codex settings in the repository, inject generated agents and those
settings into the user's real Codex config, and preserve Codex-owned machine state
such as trusted projects.

The design supports deliberate updates in both directions: repository changes can
be applied to Codex, and portable settings edited in Codex can be explicitly
captured back into the repository.

## Scope

In scope:

- Removing the Codex config symlink from the AI-agent linker.
- Rendering a marked, replaceable managed block into the real user config.
- Combining portable settings from `config/codex/global.toml` with generated
  agent registrations.
- Detecting unchanged state, one-sided drift, and two-sided conflicts.
- An explicit command to capture portable live-config edits into the repository.
- Updating shell and PowerShell flows and tests/documentation consistently.

Out of scope:

- Migrating the existing symlink automatically. The old symlink will be removed
  manually before using the new linker.
- Synchronizing credentials, trusted projects, desktop state, caches, MCP
  runtime state, marketplace snapshots, or other content outside the managed
  block.
- Automatically writing live Codex changes back into the repository during a
  normal link operation.

## Ownership model

- `agent-templates/*.md` owns agent behavior and agent-specific Codex metadata.
- `config/codex/global.toml` owns portable, non-machine-specific Codex settings.
- The generated `.codex/agents/*.toml` files remain compiler outputs and are not
  hand-edited.
- `~/.codex/config.toml` owns all content outside the Agent Kit block, including
  trusted projects and Codex runtime state.

The portable source must not contain machine-specific paths, trusted project
entries, runtime timestamps, or generated agent registrations. Agent-level
settings that are derived from templates are rendered from the generated outputs.

## Managed block

The linker renders one contiguous block:

```toml
# >>> agent-kit managed codex config
# rendered portable settings from config/codex/global.toml

# >>> agent-kit generated agents
# rendered [agents] configuration
# <<< agent-kit generated agents
# <<< agent-kit managed codex config
```

The exact marker strings are constants shared by the Unix and Windows
implementations. The generated-agent sub-marker lets capture logic distinguish
portable settings from compiler-owned output.

The linker replaces the complete outer block when both markers are present. If
neither marker is present, it appends the block to the existing regular config,
preserving all existing content. If exactly one outer marker is present, or the
generated-agent markers are malformed, it fails without modifying the target and
reports the repair needed.

The linker never follows the old repository symlink as a new managed target. The
user removes that symlink manually before the new flow is used.

## Synchronization behavior

The linker renders the desired block and compares it byte-for-byte with the
current marked block.

- Equal: no write and no backup.
- Repository-only change: replace the live block atomically.
- Live-only change: report drift and do not overwrite it automatically.
- Both changed: report a conflict and do not overwrite either side.

To distinguish the last rendered repository state from a live edit, the linker
stores a machine-local baseline of the rendered managed block under the Codex
home directory. The baseline is updated only after a successful apply or capture;
it is never committed. Missing baseline state is treated conservatively: an
existing marked block is reported as requiring adoption or explicit replacement,
not silently overwritten.

Writes use a temporary file in the target directory followed by an atomic rename.
A timestamped backup is created only before a material replacement. A lock file
serializes concurrent linker/capture operations.

## Capturing live changes

Add an explicit `capture-codex-config` command in both setup entry points.

The command:

1. Reads and validates the marked block in the real Codex config.
2. Extracts only the portable portion, excluding generated agent output.
3. Compares it with `config/codex/global.toml`.
4. Refuses to proceed if the source and live portable settings both changed since
   the recorded baseline.
5. Writes the captured portable settings to `global.toml` atomically and updates
   the baseline after success.
6. Leaves the live Codex config unchanged apart from no-op validation.

Capture preserves the source's managed-region comments where practical, but the
captured result is normalized as valid TOML. Generated agent registrations are
never imported into `global.toml`; template/compiler output remains authoritative
for those entries.

Normal linking does not silently capture changes because it would turn a machine
configuration operation into an unreviewed repository mutation. A user who wants
to retain a live edit runs capture, reviews the repository diff, and commits it
through the normal Git workflow.

## Generation and command flow

`compile-agents` continues to compile templates into `agents/*.md` and
`.codex/agents/*.toml`. The AI-agent linking flow then renders the managed Codex
block from the portable source and those generated outputs.

The normal commands are:

```bash
./scripts/setup.sh compile-agents
./scripts/setup.sh link-ai-agents
./scripts/setup.sh capture-codex-config
```

The equivalent PowerShell commands expose the same operations. `link` and
`install` continue to compile agents and link all supported surfaces, but they no
longer create or replace `~/.codex/config.toml` with a symlink.

## Verification

Tests cover:

- First injection into a regular config with unrelated settings preserved.
- Exact replacement of a marked block.
- No-op behavior when the rendered block is unchanged.
- Repository-only updates.
- Live-only drift detection without overwrite.
- Two-sided conflict detection.
- Malformed/missing markers failing safely.
- Preservation of trusted projects, desktop state, MCP state, and unknown tables.
- Capture importing portable settings while excluding generated agents.
- Atomic writes, backups only on material changes, and baseline updates.
- Unix and PowerShell command wiring.
- Absence of the old Codex config symlink operation.

Documentation will update `docs/linking.md`, `docs/agents.md`, and the related
sync/config strategy documentation to describe the managed block and explicit
capture workflow.
