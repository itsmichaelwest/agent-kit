# Skills & Config Sync Strategy

Status: **decided (2026-05)**, with revisit triggers below.

This document records how this repo syncs skills (and related agent config)
across devices, why it works the way it does, and what would make us change it.
It exists because the tooling here is young and moving fast — when `npx skills`
or the CLIs themselves gain features, re-read the [Revisit triggers](#revisit-triggers)
before reworking anything.

## The problem

Keep one curated, global set of agent skills — plus instructions, subagents, and
MCP servers — consistent across three machines and three CLIs (Claude Code,
Codex CLI, GitHub Copilot CLI). A fresh machine, or an existing one after a
`git pull`, should converge to the same setup with one command and no manual
fixups.

These are **curated global config**: skills chosen because they're useful to the
work, expected to be available everywhere, and changed rarely. Some are authored
here (custom); most are pulled from upstream GitHub repos and should be
refreshable against their sources.

## Research findings (May 2026)

### No CLI ships native config sync

None of the three target CLIs has a built-in cross-device sync mechanism:

- **Claude Code** — cloud-sync request ([#57678](https://github.com/anthropics/claude-code/issues/57678)) closed *not planned*; [#36693](https://github.com/anthropics/claude-code/issues/36693) open. The only native "sync" is Claude.ai connectors, which covers MCP servers only.
- **Codex CLI** — no roadmap ([discussion #14067](https://github.com/openai/codex/discussions/14067)). Session state syncs across surfaces; config does not.
- **Copilot CLI** — request ([#2353](https://github.com/github/copilot-cli/issues/2353)) has no response.

A git dotfiles repo + symlinks remains the only real answer. This repo already
does that.

### `npx skills` is a package manager bolted onto a config manager

`npx skills` (vercel-labs/skills, v1.5.9 verified locally) is built around an
npm-style model: a lockfile you commit, contents you restore.

- `experimental_install` ("Restore skills from skills-lock.json") **shipped** —
  this is the resolution to the long-standing [#549](https://github.com/vercel-labs/skills/issues/549) / [#283](https://github.com/vercel-labs/skills/issues/283) "no install command" gap.
  **But it is project-scope only.** Verified on this machine: with no
  `./skills-lock.json` in cwd it reports *"No project skills found"*. There is no
  `-g`, so it cannot restore our **global** `~/.agents/.skill-lock.json`.
- `update -g -y` refreshes skills that are **already installed**; it will not
  install missing ones, so it cannot bootstrap a bare machine on its own.
- Global scope has a live data-loss bug: [#542](https://github.com/vercel-labs/skills/issues/542)
  ("global lock migration silently wipes tracked skills"). Other rough edges:
  silent update failures on macOS/npx ([#371](https://github.com/vercel-labs/skills/issues/371)),
  same-name collisions ([#606](https://github.com/vercel-labs/skills/issues/606)),
  Windows CRLF hash drift ([#781](https://github.com/vercel-labs/skills/issues/781)),
  `update <one>` dragging in unrelated skills from the same repo ([#915](https://github.com/vercel-labs/skills/issues/915)),
  and nested-repo `.git` dirs leaking into the tree for submodule-based skills ([#492](https://github.com/vercel-labs/skills/issues/492)).

The takeaway: `npx skills` is genuinely useful as an **installer/updater**, but
its sync philosophy (commit the lockfile, gitignore the contents) targets
*project-scope dependencies* and does not yet serve a *global curated config*.

### Strong convergence: AGENTS.md and `~/.agents`

Two things the ecosystem has clearly standardized on:

- **`AGENTS.md`** is the canonical instruction file (Sourcegraph-originated, now
  backed by OpenAI and Google, 60k+ repos). Tools that don't read it natively are
  fed via symlink or thin shim: Claude reads `CLAUDE.md`, Codex reads
  `AGENTS.md`, Copilot CLI reads `copilot-instructions.md`, Gemini reads
  `GEMINI.md`. This repo already maps one `AGENTS.md` source to all three native
  targets — keep this.
- **`~/.agents/` and `~/.agents/skills/`** is the emerging universal home that
  multiple tools read. Codex and Copilot read it natively; **Claude Code does
  not** (it reads `~/.claude/skills`), so Claude needs its own symlink.

### Two philosophies — and they disagree about vendoring

The "should I commit skills to git?" question has two different community
answers depending on whether you frame skills as *dependencies* or *config*:

| Frame | Converged answer | Where it dominates |
|---|---|---|
| Skills are **external dependencies** pulled from upstream | Lockfile, don't vendor, restore (npm model) — `npx skills` + `experimental_install` | The `npx skills` sub-ecosystem |
| Skills are **your config** that you author/curate | Vendor in git + symlink | Cross-CLI dotfiles tools |

The purpose-built cross-CLI sync tools — built for exactly this repo's use case
(personal, multi-machine, multi-tool) — all **vendor**:

- [`wpfleger96/ai-agent-rules`](https://github.com/wpfleger96/ai-agent-rules) — one source dir → Claude/Codex/Gemini/Goose/Amp via symlinks, `mcps.json` rendered per tool, `default→personal→work` profile inheritance. Closest analog to this repo.
- [`dot-agents`](https://www.dot-agents.com/) — everything in `~/.agents/`, symlinks, `dot-agents doctor` to rebuild on a new machine.
- Others: [`ZacheryGlass/agent-sync`](https://github.com/ZacheryGlass/agent-sync), [`chrisleekr/agentsync`](https://github.com/chrisleekr/agentsync) (encrypted git vault), [`mfmezger/ai_agent_dotfiles`](https://github.com/mfmezger/ai_agent_dotfiles), [`wshobson/agents`](https://github.com/wshobson/agents); [chezmoi](https://dev.to/dotwee/one-skills-brain-for-codex-claude-cursor-and-copilot-with-chezmoi-2p3k) for the template-heavy crowd.

## Decision

Treat this repo's skills as **curated global config, not dependencies**, and
commit fully to the dotfiles config-manager philosophy:

1. **Vendor the materialized skills** in `skills/` (committed). This is the
   source of truth for what's actually available. It makes sync reproducible and
   offline-capable: `git pull` + `setup link` gives every machine the exact same
   skills, with no network, no upstream availability risk, and no dependence on
   experimental commands.
2. **Distribute by symlink** into the tool locations (`~/.claude/skills`,
   `~/.agents/skills`, `~/.copilot/skills`) — already wired in
   `scripts/ai-agent-links.json`.
3. **Keep `npx skills` as an optional updater, not required machinery.** It is
   never on the sync path. It is run manually to refresh upstream skills, and its
   output is reviewed as a git diff and committed.
4. **Distinguish custom from upstream by the manifest.** `scripts/skills-manifest.json`
   lists upstream sources. Any skill folder in `skills/` that is *not* covered by
   the manifest is treated as custom/local and is never auto-updated. This is how
   "keep non-custom skills updated against upstream" stays safe — updates only
   touch skills with a declared source.

This keeps the strengths the repo already has (reproducible, offline, one-command
sync) while preserving an upstream-refresh path. The cost — others' code lives in
the repo — is mitigated by `.gitattributes` marking `skills/**` as
`linguist-vendored` + `linguist-generated`, so it's excluded from language stats
and collapsed in diffs.

### Update workflow (non-custom skills)

```bash
# Refresh installed upstream skills to latest, then review + commit the diff
npx skills update -g -y         # or: ./scripts/setup.sh update-skills
./scripts/setup.sh doctor       # verify manifest/lockfile/disk still agree
git add skills/ .skill-lock.json
git diff --cached               # review what changed
git commit -m "chore(skills): refresh upstream skills"
```

Custom skills (not from an upstream source) are edited in `skills/` directly and
committed like any other source. List them under `"local"` in
`scripts/skills-manifest.json` so the doctor treats them as intentional.

## Keeping it consistent: `setup.sh doctor`

`./scripts/setup.sh doctor` (`.\scripts\setup.ps1 doctor`) checks that the three
representations agree, so the drift that prompted this strategy can't silently
recur. Add `--strict` to fail on warnings too (for CI / pre-commit).

It enforces the model:

- manifest `sources[]` = declared upstream repos; `local[]` = skills authored here
- `.skill-lock.json` = provenance for upstream skills
- `skills/<name>/` = the committed vendored output

Errors (exit non-zero): nested `.git` in the tree (the
[#492](https://github.com/vercel-labs/skills/issues/492) footgun), a lockfile
skill missing on disk, a skill folder with no `SKILL.md`, or an undeclared skill
on disk (not in the lockfile and not in `local[]`). Warnings: a manifest source
with no lockfile entry, a declared `local` skill missing on disk, or a lockfile
source absent from the manifest.

The earlier drift — manifest ≠ lockfile ≠ `skills/`, the manually-cloned
`humanizer` carrying a nested `.git`, and `humanizer`/`oklch-skill` untracked and
undeclared — was resolved when this was put in place: both are now upstream
sources in the manifest, recorded in the lockfile, and vendored cleanly; the five
repo-authored skills are declared under `local`.

## Private skills (machine-local, not synced)

Some skills should live on one machine only and never be committed or synced —
client-specific tooling, anything whose name is private. There are three tiers in
total:

| Tier | Declared in | Committed | Synced across your devices |
|---|---|---|---|
| Upstream | manifest `sources[]` + lockfile | yes (vendored) | yes |
| Custom | manifest `local[]` | yes (vendored) | yes |
| Private | nowhere tracked (git-ignored) | no | no |

Because Claude Code only reads `~/.claude/skills` (→ this repo's `skills/`), a
private skill still has to sit in `skills/` for the tools to load it. The
separation is at the **git layer**, not the filesystem: git-ignore the folder and
the doctor treats it as private and skips it. **Its name never appears in any
tracked file** — put the ignore in `.git/info/exclude` (per-clone, never pushed):

```bash
# install/place the private skill so the tools see it (do NOT use `npx skills add -g`,
# which writes the shared, tracked lockfile and would leak the name):
git clone <private-skill-repo> skills/acme-internal
rm -rf skills/acme-internal/.git          # don't leave a nested repo in the tree

echo 'skills/acme-internal/' >> .git/info/exclude   # ignore it, locally, by name
./scripts/setup.sh doctor                 # confirms it's seen as private, not flagged
```

On Windows (PowerShell):

```powershell
git clone <private-skill-repo> skills\acme-internal
Remove-Item -Recurse -Force skills\acme-internal\.git
Add-Content .git\info\exclude 'skills/acme-internal/'   # forward slashes; git-relative
.\scripts\setup.ps1 doctor
```

`setup.sh doctor` discovers ignored skills via `git check-ignore`, so it never
needs their names. It also **warns** if a git-ignored skill is found in the
tracked lockfile (the tell-tale that you installed it with `-g` and its name is
about to be committed).

Private **plugins** follow the existing per-machine overlay convention: declare
them in the git-ignored `.claude/settings.local.json`,
`.copilot/settings.local.json`, or `.codex/config.local.toml` — `enabledPlugins`
merges across the committed base and the local overlay.

## Revisit triggers

Reconsider this strategy (likely toward the lockfile-and-restore model, dropping
vendored contents) when **any** of these lands:

- `npx skills` gains **global** restore — an `experimental_install`/`install`
  that reads `~/.agents/.skill-lock.json` with `-g`. This is the main blocker.
- `npx skills` adds **SHA-pinned** restore (install the locked `skillFolderHash`,
  not latest), giving reproducibility without vendoring. Watch
  [`pcomans/skills-lock`](https://github.com/pcomans/skills-lock) and
  [`pi0/skillman`](https://github.com/pi0/skillman) too.
- The global-scope data-loss bug ([#542](https://github.com/vercel-labs/skills/issues/542))
  is fixed and the tool's global path is trustworthy.
- A CLI ships native cross-device config sync that covers skills (not just MCP).

Until then: vendored config + symlinks + `npx skills` as a manual updater.

## Sources

Captured 2026-05; all verified current as of late May 2026. Command behavior
(`experimental_install` project-only, v1.5.9) verified directly on-machine.

- vercel-labs/skills — [repo](https://github.com/vercel-labs/skills), issues [#549](https://github.com/vercel-labs/skills/issues/549) [#283](https://github.com/vercel-labs/skills/issues/283) [#542](https://github.com/vercel-labs/skills/issues/542) [#371](https://github.com/vercel-labs/skills/issues/371) [#606](https://github.com/vercel-labs/skills/issues/606) [#492](https://github.com/vercel-labs/skills/issues/492)
- Lockfile model write-ups — [maier.tech](https://maier.tech/notes/a-lockfile-for-agent-skills), [toyama0919 (dev.to)](https://dev.to/toyama0919/managing-ai-agent-skills-with-npx-skills-a-practical-guide-2an8)
- Cross-CLI sync tools — [ai-agent-rules](https://github.com/wpfleger96/ai-agent-rules), [dot-agents](https://www.dot-agents.com/), [agent-sync](https://github.com/ZacheryGlass/agent-sync), [agentsync](https://github.com/chrisleekr/agentsync)
- AGENTS.md standard — [agents.md](https://agents.md/), [deployhq guide](https://www.deployhq.com/blog/ai-coding-config-files-guide)
- CLI native sync gaps — Claude [#57678](https://github.com/anthropics/claude-code/issues/57678), Codex [discussion #14067](https://github.com/openai/codex/discussions/14067), Copilot [#2353](https://github.com/github/copilot-cli/issues/2353)
