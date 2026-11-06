# NOTICE · Third-party provenance and license status

This skill (`browser-pilot`) is an integrated work. Version 1.7.3 contains only the two paths, both of which carry a clear open-source license.

## Changes since 1.7.0 (1.7.1 – 1.7.3)

Staged fixes against the scoring gaps (output accuracy, error handling and stability, channel adaptation). The compliance structure is unchanged: two paths, license files complete, no bundled scripts.

**1.7.3** — English edition for GitHub distribution. Same content as the Chinese 1.7.2, plus wording-alignment edits. No functional change.

**1.7.2** — Public description trimmed to fit the SkillHub field limit (summary 99 characters). Content unchanged.

**1.7.1** — Error-handling hardening:

- Error-handling table for 6 scenarios with unified codes B1–B6, so a reported code locates the scenario directly
- New uniform retry policy: one channel switch for install failures, one scroll/selector retry for action failures, no replay when the result is unknown, timeouts count as failure and degrade
- New channel degradation table: npm → npmmirror → private registry; core download → proxy → network switch → Path B; extension → foreground daemon → manual load. Switch levels instead of stalling on one point
- New fixed verification wording and key-number trace-back rule: verify URL / title / key numbers before delivery and cite where each came from; untraceable numbers are deleted or marked [unverified]

## Changes since 1.6.0 (1.7.0, 2026-11-04)

Flexibility and advanced capability added on top of 1.6.0. Compliance structure unchanged (two paths, license files complete, no bundled scripts):

- New "How to use it, and single-step calls": 4 single-step entries plus three execution gates (ask before irreversible actions, never replay when the effect is unknown, restate the scene when resuming)
- New "Failure handling and degradation": a 6-scenario wording table (CLI not installed / core download failed / extension cannot connect / click has no effect / effect unknown / anti-automation block)
- Universal guardrails 5 → 7: added "credentials never touch disk or leave the machine" and "never bulk-export private data"
- New FAQ with 8 entries
- New `references/site-patterns/README.md` site-experience extension mechanism (path-agnostic, expirable, falls back to generic patterns, stores no credentials)
- summary / description updated with those capability keywords; `workbuddy.json` and `README.md` kept in sync

## The two sources in this package

| Path in this package | Upstream project | License (verified 2026-11-02) | Redistribution condition |
|:--|:--|:--|:--|
| `references/path-extension-browser-skill.md` | github.com/Tencent/BrowserSkill | MIT | Keep copyright and license notices |
| `references/path-standalone-agent-browser.md` | github.com/vercel-labs/agent-browser | Apache-2.0 | Include a license copy, keep NOTICE, mark modifications prominently |

The remaining `references/` documents (environment, authentication, sessions, screenshots, troubleshooting) are consolidated from the technical documentation of those two projects and inherit their upstream license status.

## Removed content and why

An earlier version contained a third path (a third-party browser-takeover approach) whose source project is `github.com/eze-is/web-access`. Verified through the GitHub API (`license: null`), that project **declares no open-source license**. Under default copyright rules the author retains all rights, so its documentation cannot be copied or redistributed without permission.

To eliminate that risk, this version removes all content from that source; it is no longer distributed. The removal is described by type below — the specific files are no longer in the package, so they are not listed by name:

| Removed type | Count | Reason |
|:--|:--|:--|
| That project's documentation body (including interface notes and version-migration notes) | 3 | No license; not redistributable |
| That project's executable scripts (including the proxy program and its dependency scripts) | 5 | No license; not redistributable |
| Configuration templates for that path | 2 | Removed alongside, to avoid dead links and misuse |
| Measured run record for that path | 1 | The described capability is no longer in the package; keeping it would mislead |

After removal, the related references in `SKILL.md` and `README.md` were deleted as well. A full-text search confirms no residual pointers and no links to deleted files.

## Original parts of this package

The following was added by this integration and comes from no upstream project; it is MIT-licensed:

- The two-step routing layer, universal guardrails, environment self-check flow and known-limitations section of `SKILL.md`
- The structure description in `README.md`
- `examples/real-run-2026-11-02-pathb.md` — measured Path B run (cooperation sync, auto-scroll conclusion, two failures)
- `examples/real-run-2026-11-02-pathc.md` — measured Path C run (commands and raw output)
- `examples/setup-checklist.md` — environment preparation checklist and common blocker handling
- Screenshots generated during the measured runs (Path B 61,793 bytes / 1554×668, Path C about 41 KB): the platform forbids uploading binaries, so screenshots are not distributed; the measured records keep the generating commands and returned parameters
- This NOTICE file

## Modification notices (Apache-2.0 requirement)

Under Apache-2.0 section 4, modifications to content from `vercel-labs/agent-browser` are recorded here (cumulative):

- Chapter order rearranged to "installed → running → typical scenarios → advanced → security → troubleshooting"
- Chapters and supporting material of two same-named documents merged
- Usage notes for "connect to an already-running browser" parameters deleted; the authentication chapter now logs in inside the instance's own profile, consistent with this package's two-path model
- A scroll-into-view prerequisite added before click operations (based on this package's measurements)
- The install wrapper script that ran automatically on plugin load removed; installation is now invoked manually from `templates/`
- Measured records and screenshots for Path B (`Tencent/BrowserSkill`, MIT) added; the boundary between the two upstream contributions is marked in the two-path comparison table in `SKILL.md`
- Naming convention: all-lowercase kebab-case (`browser-pilot`); display name, document titles, sample outputs and copyright lines use the same identifier, with ASCII hyphens only

## Verification record

The license status above was verified on 2026-11-02 through the GitHub API `license.spdx_id` field, not from second-hand descriptions. If an upstream project changes its license, the new actual status governs and this file should be updated.

## Changes in 1.6.0 since 1.5.0

1. **Mainland-China install guidance**: the npmmirror form of npm, plus branch handling and alternatives when `agent-browser install` (199 MB core) fails (P1)
2. **Eight routing examples**: user phrasing → path → output table, including the rule of thumb (P1)
3. **Three-step minimum first-run table**: self-check → install → smoke test, verifiable immediately after install (P3)
4. **Post-crash cleanup list**: processes, sessions, daemon, temp files, proxy/ports — five categories plus closing verification (P2)
5. **Consistency pass**: README wording changed from "takes over the current tab" to "opens a new Agent Window without seizing the user's window" (matching the measured record "Session model: not a takeover of the current tab"); a "path" column added to the reference index in `SKILL.md` (P2)
6. **Path labels on reference files**: all 20 files under `references/` are headed with "This file applies to Path X" (P2)
7. **License completion** (Apache-2.0 §4): full text of `LICENSES/Apache-2.0.txt` added; upstream copyright lines for Tencent/BrowserSkill and vercel-labs/agent-browser added to `NOTICE.md`; file-level modification notices added to the four modified files (`path-standalone-agent-browser.md`, `authentication.md`, `path-extension-browser-skill.md`, `environment.md`)
8. **Copy update**: `summary` / `description` / `description_en` and `workbuddy.json` rewritten along "title — positioning — highlights — scenarios — value — boundaries"

## File-level modification notice summary (Apache-2.0 §4(b))

| File | Upstream | Notice location |
|:--|:--|:--|
| `references/path-standalone-agent-browser.md` | vercel-labs/agent-browser (Apache-2.0) | Top of file |
| `references/authentication.md` | vercel-labs/agent-browser docs (Apache-2.0) | Top of file |
| `references/path-extension-browser-skill.md` | Tencent/BrowserSkill (MIT) | Top of file |
| `references/environment.md` | Tencent/BrowserSkill (MIT) | Top of file |

Other files under `references/` only gained a "This file applies to Path X" scope label and, where relevant, light cross-references; their operating instructions were not altered.

## Copyright notices

This package is an integrated work; copyright in the derived content belongs to its upstream authors:

- Path B derived content (`references/path-extension-browser-skill.md` and others): Copyright (c) 2026 Tencent/BrowserSkill contributors, MIT License (full text in `LICENSE`)
- Path C derived content (`references/path-standalone-agent-browser.md`, `references/authentication.md` and others): Copyright (c) 2026 vercel-labs/agent-browser contributors, Apache License 2.0 (full text in `LICENSES/Apache-2.0.txt`)

Original parts of this package are Copyright (c) 2026 browser-pilot contributors, MIT License. File-level modification notices for the changed files appear at the top of each file; the NOTICE attribution required by Apache-2.0 section 4 is retained in this file.
