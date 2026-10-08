# Maintenance

Use the [README](../README.md) to find the operational reference for a change.
Edit canonical templates and configuration rather than generated outputs or live
runtime state. Review a declaration together with the scripts that consume it.

## Validate a change

For documentation, inspect local links and commands and run `git diff --check`.
For inventory changes, use the skills doctor without changing home configuration:

```bash
python3 scripts/lib/doctor-skills.py --repo-root . --strict
```

For script changes, run the relevant existing tests and shell syntax checks:

```bash
python3 -m unittest discover -s tests -p 'test_doctor_skills.py'
bash -n scripts/setup.sh scripts/lib/*.sh
```

Use the applicable `test_*.py` pattern for the changed subsystem. For cross-cutting
setup changes, run the complete existing suite:

```bash
python3 -m unittest discover -s tests
```

Platform-dependent tests may skip without PowerShell or Windows. Report those
limits. Setup's `doctor` also validates live links; use it on configured machines.
Do not run `link`, `install`, or capture commands merely to check documentation.

## Preserve implementation constraints

- TOML table scope persists until another header. Edit with the comment-preserving
  parser, including quoted key components, instead of matching table names with
  bare-name regular expressions. See [Codex sync](codex-config-sync.md).
- Keep script-owned and machine-owned Codex fields separate. Portable keys come
  from `config/codex/global.toml`; generated registrations come from templates.
- Compute the link marker as `<layoutVersion>+<sha256(topology)[:8]>` from
  `source|sourceRel|path` lines in manifest order. Keep Python, Bash, and PowerShell
  implementations equivalent. Bump `layoutVersion` for explicit target migrations.
- Windows junctions are reparse points; `os.path.islink()` can be false for a
  valid directory junction. Use `os.readlink()` and resolved-target comparison.
- Route captured jq output through `jqr` in `helpers.sh`. Windows jq emits CRLF;
  multiline shell captures and read loops can retain interior carriage returns.
  Output redirected directly to a file does not need that wrapper.
- Guard PSReadLine predictions with an interactive `ConsoleHost` check and
  non-redirected input/output/error streams.
- A global skill removal mutates the repo lockfile through its home link. Save the
  manifest edit plan before calling the CLI. Reconciliation must preserve valid
  skills and non-empty unknown folders.
- Apply link-manifest changes with `setup link` on each machine. Missing safety
  hook links can block shell calls; see [Hooks](hooks.md).

## Maintain documentation

Each topic has one operational reference. Keep commands, contracts, compatibility
limits, troubleshooting, and useful source attribution. Remove completed plans,
run logs, obsolete alternatives, and duplicated explanations once their durable
material is incorporated. Git history preserves prior designs.
