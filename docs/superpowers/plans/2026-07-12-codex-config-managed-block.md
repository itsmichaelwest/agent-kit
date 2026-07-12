# Codex Config Managed Block Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Codex config symlink with a bidirectional, marker-based managed block that injects portable settings and generated agents while preserving machine-local Codex state.

**Architecture:** A new Python synchronizer will render the managed block from `config/codex/global.toml` and `.codex/agents/*.toml`, then atomically apply it to the real Codex config. A machine-local baseline enables safe classification of repository-only changes, live-only drift, and two-sided conflicts. Explicit capture imports only the portable portion back into `global.toml`; shell and PowerShell wrappers call the same Python implementation.

**Tech Stack:** Python 3.11+ standard library (`tomllib`, `argparse`, `hashlib`, `tempfile`), Bash, PowerShell, unittest.

## Global Constraints

- Preserve all config outside the marked block, including trusted projects and unknown future tables.
- Never recreate or manage the old Codex config symlink.
- Repository edits must not be silently created by normal linking; capture is explicit.
- Generated agent registrations remain owned by `agent-templates/*.md` and compiler output.
- Writes are atomic; backups occur only before material changes.
- Maintain equivalent Unix and Windows commands.
- Preserve the user’s existing unstaged modification to `config/codex/global.toml` unless the implementation explicitly normalizes its machine-specific content as part of the requested change.

---

### Task 1: Add failing synchronizer tests and define the render contract

**Files:**
- Create: `tests/test_codex_config_sync.py`
- Create: `scripts/lib/sync-codex-config.py`

**Interfaces:**
- The test suite will invoke the script with `--repo-root`, `--home-dir`, and either `apply` or `capture`.
- The script will expose `render_managed_block(repo_root)`, `apply_config(repo_root, home_dir)`, and `capture_config(repo_root, home_dir)` for direct unit tests.

- [ ] **Step 1: Write failing tests** covering first append, exact replacement, no-op, preservation of `[projects]` and unknown content, marker failure, and the three baseline states.

```python
def test_apply_appends_and_preserves_unmanaged_config():
    live.write_text('[projects."/private/project"]\ntrust_level = "trusted"\n', encoding="utf-8")
    result = run_sync("apply")
    assert result.returncode == 0
    text = live.read_text(encoding="utf-8")
    assert '[projects."/private/project"]' in text
    assert "# >>> agent-kit managed codex config" in text

def test_apply_replaces_only_marked_block():
    live.write_text(unmanaged + old_block, encoding="utf-8")
    run_sync("apply")
    text = live.read_text(encoding="utf-8")
    assert text.startswith(unmanaged)
    assert old_block not in text
    assert rendered_block in text

def test_apply_reports_live_only_drift_without_overwriting():
    run_sync("apply")
    original = live.read_text(encoding="utf-8")
    live.write_text(original.replace('personality = "pragmatic"', 'personality = "calm"'), encoding="utf-8")
    result = run_sync("apply")
    assert result.returncode != 0
    assert 'personality = "calm"' in live.read_text(encoding="utf-8")

def test_capture_updates_portable_source_but_not_generated_agents():
    run_sync("apply")
    live.write_text(live.read_text(encoding="utf-8").replace('personality = "pragmatic"', 'personality = "calm"'), encoding="utf-8")
    result = run_sync("capture")
    assert result.returncode == 0
    assert 'personality = "calm"' in source.read_text(encoding="utf-8")
    assert "developer_instructions" not in source.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run the focused tests and verify they fail because the synchronizer is missing.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: FAIL with import/script-not-found or missing behavior errors, not fixture errors.

- [ ] **Step 3: Create the minimal script surface and marker constants.**

Define `START_MARKER`, `END_MARKER`, `GENERATED_START_MARKER`, and
`GENERATED_END_MARKER`; add argparse dispatch; leave apply/capture raising a
clear `SyncError` until the next task implements them.

- [ ] **Step 4: Run the focused tests again and confirm the failures now identify missing behavior.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: fixture setup succeeds and behavior assertions fail.

### Task 2: Implement deterministic rendering and baseline classification

**Files:**
- Modify: `scripts/lib/sync-codex-config.py`
- Modify: `tests/test_codex_config_sync.py`

**Interfaces:**
- `render_managed_block(repo_root: Path) -> str` returns one newline-terminated block.
- `baseline_path(home_dir: Path) -> Path` returns `~/.codex/agent-kit-config-baseline.sha256`.
- `classify(current: str | None, desired: str, baseline: str | None) -> Literal["new", "unchanged", "repo-only", "live-only", "conflict"]`.

- [ ] **Step 1: Add tests for deterministic rendering and all classifier outcomes.**

Assert that generated agent files are included under the generated sub-block,
source portable settings are included verbatim, and `[agents]` is not duplicated
when compiler output is rendered.

- [ ] **Step 2: Run focused tests and verify the new tests fail.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: rendering/classification assertions fail.

- [ ] **Step 3: Implement rendering and classification.**

Read and TOML-validate the source and generated files with `tomllib`, preserve
the source text for portable settings, render generated agent tables in sorted
filename order, and classify using SHA-256 of the exact marked block. Allow
portable scalar settings such as `[agents] max_threads`, but reject machine-local
`[projects]` data and generated `[agents.<name>]` registrations in the source.

- [ ] **Step 4: Run focused tests and confirm they pass.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: all render and classification tests PASS.

### Task 3: Implement safe apply, capture, locking, and atomic writes

**Files:**
- Modify: `scripts/lib/sync-codex-config.py`
- Modify: `tests/test_codex_config_sync.py`

**Interfaces:**
- `apply_config(repo_root: Path, home_dir: Path) -> int` updates the real config or returns a nonzero conflict/drift result.
- `capture_config(repo_root: Path, home_dir: Path) -> int` imports portable settings and returns a nonzero validation/conflict result.

- [ ] **Step 1: Add tests for malformed markers, missing baseline, atomic replacement, backup behavior, and capture conflicts.**

Verify that a partial marker leaves the file and source byte-identical, that an
unchanged apply creates no backup, and that a material replacement creates one
backup and a new baseline.

- [ ] **Step 2: Run focused tests and verify the safety tests fail.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: safety assertions fail while earlier rendering tests remain green.

- [ ] **Step 3: Implement apply and capture.**

Use a lock file under `~/.codex`, write temporary files in the destination
directory, `os.replace` them, and store the baseline only after success. Apply
appends when neither marker exists, replaces both markers when valid, and refuses
partial markers or live-only/conflict states. Capture extracts the text before
the generated-agent marker, validates it with `tomllib`, writes
`config/codex/global.toml` atomically, and never imports generated agent text.

- [ ] **Step 4: Run focused tests and confirm they pass.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: all synchronizer tests PASS.

### Task 4: Wire generation and linker commands on Unix and Windows

**Files:**
- Modify: `scripts/lib/compile-agents.sh`
- Modify: `scripts/lib/compile-agents.ps1`
- Modify: `scripts/lib/link-ai-agents.sh`
- Modify: `scripts/lib/link-ai-agents.ps1`
- Modify: `scripts/setup.sh`
- Modify: `scripts/setup.ps1`
- Create: `scripts/lib/sync-codex-config.sh`
- Create: `scripts/lib/sync-codex-config.ps1`
- Modify: `tests/test_codex_config_sync.py`

**Interfaces:**
- `./scripts/setup.sh capture-codex-config` and `.scripts\setup.ps1 capture-codex-config` invoke capture.
- `compile-agents`, `link`, and `link-ai-agents` apply the managed block after successful compilation.

- [ ] **Step 1: Add command-wiring tests that inspect help output and run the Unix wrapper with a temporary home.**

Assert that the old `ensure_linked`/`Ensure-Linked` Codex config operation is
absent and that the new capture command is accepted.

- [ ] **Step 2: Run the wiring tests and verify they fail.**

Run: `python3 -m unittest tests.test_codex_config_sync -v`

Expected: command/help assertions fail before wiring exists.

- [ ] **Step 3: Add thin wrappers and replace the old Codex link calls.**

The wrappers resolve Python 3.11+, invoke the synchronizer with `--repo-root`
and `--home-dir "$HOME"`, and preserve the synchronizer’s exit status. Add the
new action to both setup validators, usage text, dispatch cases, and call apply
from compilation/link flows exactly once.

- [ ] **Step 4: Run shell syntax and wiring tests.**

Run: `bash -n scripts/setup.sh scripts/lib/compile-agents.sh scripts/lib/link-ai-agents.sh scripts/lib/sync-codex-config.sh && python3 -m unittest tests.test_codex_config_sync -v`

Expected: exit 0 and all focused tests PASS.

### Task 5: Update documentation and source configuration boundaries

**Files:**
- Modify: `config/codex/global.toml`
- Modify: `docs/linking.md`
- Modify: `docs/agents.md`
- Modify: `docs/skills-sync.md`
- Modify: `tests/test_codex_plugin_policy.py`

- [ ] **Step 1: Add policy tests rejecting trusted projects, runtime timestamps, and generated agent bodies from the portable source.**

- [ ] **Step 2: Run the policy tests and confirm they fail against the current linked-file-shaped source.**

Run: `python3 -m unittest tests.test_codex_plugin_policy -v`

Expected: failures identify machine-local or generated content that must be removed from the source.

- [ ] **Step 3: Remove machine-local and generated sections from `global.toml` while preserving portable settings and plugin declarations.**

Keep the existing user modification’s portable values where they are truly
portable; remove paths, timestamps, runtime MCP data, `[projects]`, `[desktop]`,
and generated agent registrations from the repository source.

- [ ] **Step 4: Document managed-block ownership, drift handling, capture, and manual old-symlink removal.**

- [ ] **Step 5: Run policy tests and documentation/config validation.**

Run: `python3 -m unittest tests.test_codex_plugin_policy -v && python3 -c 'import tomllib, pathlib; tomllib.loads(pathlib.Path("config/codex/global.toml").read_text())'`

Expected: exit 0.

### Task 6: Full verification and review cleanup

**Files:**
- Modify: any implementation/test/docs files above only as needed by verification.

- [ ] **Step 1: Run the complete Python test suite.**

Run: `python3 -m unittest discover -s tests -v`

Expected: exit 0 with zero failures or errors.

- [ ] **Step 2: Run shell syntax checks and inspect the complete diff.**

Run: `bash -n scripts/setup.sh scripts/lib/*.sh && git diff --check && git diff --stat && git status --short`

Expected: all checks exit 0; only intended files are changed, with the original
user modification accounted for rather than overwritten.

- [ ] **Step 3: Remove accidental complexity and update `LEARNINGS.md` only with durable discoveries.**

- [ ] **Step 4: Run the full test suite once more after cleanup.**

Run: `python3 -m unittest discover -s tests -v`

Expected: exit 0 with zero failures or errors.
