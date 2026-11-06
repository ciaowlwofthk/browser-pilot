# Environment preparation and first-run checklist

> **Measured status:** both paths have been run for real on this machine. Path C (standalone instance) is in `real-run-2026-11-02-pathc.md`; Path B (extension takeover) is in `real-run-2026-11-02-pathb.md`. Every item below comes from those runs, not from copying the docs.
>
> Use this file to confirm dependencies before you start; each path lists its own checks and pass criteria.

---

## Path C · standalone instance (Apache-2.0)

Best for: regression tests, clean-environment scraping, batch jobs. No existing login is reused.

### Prerequisites

```bash
node -v            # 18 or newer required, 20+ recommended
npm -v
```

### Install

```bash
npm install -g agent-browser     # measured 14 s; installs the scheduler only
agent-browser install            # measured 1 min 3 s; downloads the 199 MB Chrome 156 core
```

Neither step can be skipped. Skip `install` and `open` pulls the core in the background with no output at all — measured 10 minutes without returning, easily mistaken for a hang.

### First verification (four steps)

```bash
agent-browser open https://example.com
agent-browser wait --load networkidle
agent-browser snapshot
agent-browser close
```

Pass criteria and measured results:

| Step | What passing looks like | This run |
|:--|:--|:--|
| `open` | Returns the page title and URL, no connection error | ✓ Example Domain / https://example.com/ |
| `wait` | Returns `✓ Done`, not a timeout | ✓ Done |
| `snapshot` | Prints the page structure with `[ref=eN]` markers | Full structure tree including `[ref=e1]` |
| `close` | Reports a successful close, no leftover instance | ✓ Browser closed |

Two more useful commands: `get title` for the title, `screenshot <path>` to save an image (measured: a 41 KB PNG).

If `snapshot` comes back empty, it usually means the page has not finished rendering — add a wait after `wait` and re-snapshot, rather than concluding the page has no content.

### Click verification (the trap worth reading)

Clicking a link is the easiest thing to get wrong. The cause was located in the measured run: **an element outside the viewport is clicked with no effect, and no error.**

```bash
agent-browser snapshot
agent-browser eval "document.querySelector('a').scrollIntoView({block:'center'})"
agent-browser click "@e1" --json
agent-browser wait --load networkidle
agent-browser get url
```

| Question | Answer |
|:--|:--|
| Why `scrollIntoView` first | `click` dispatches mouse events at the element's centre coordinates without scrolling; off-screen, those coordinates land outside the viewport and the events miss |
| Why `--json` | Normal mode prints `✓ Done` even on failure; `--json` reveals `{"success":false,"error":"Unknown ref: e1"}` |
| Why check `get url` afterwards | `success:true` only means the events were dispatched, not that the page navigated |

Measured data: element `top=677.328125` against a viewport `height=566` → click had no effect; after `scrollIntoView`, `top=510` → the same ref clicked through immediately. If you would rather not deal with scrolling, use `click "@e1" --new-tab`, which takes a different code path and is not coordinate-bound.

---

## Path B · extension takeover (MIT)

Best for: reusing an existing login, actions that need real identity. The measured mechanism opens a new **Agent Window** in the same browser; the user's own window is never seized.

### Prerequisites

```bash
bsk --version          # see the next section if absent
bsk browsers --json    # should list at least one browser
```

### Install (the measured route)

```bash
curl -sSL https://github.com/Tencent/BrowserSkill/releases/latest/download/version.json
# verify against the sha256 in the manifest, then unpack bsk.exe into ~/.local/bin
curl -sSL -o ext.zip https://github.com/Tencent/BrowserSkill/releases/download/ext-v0.4.1/browser-skill-extension-v0.4.1-chrome.zip
```

The extension zip is served directly under the Release's `ext-v*` tags — **no extension store required**.

### Start the daemon

```bash
bsk daemon start --foreground     # required when the host forbids detached child processes
```

Verify with a separate command; do not chain it onto the same call:

```bash
bsk status --json
```

### First verification

| Check | What passing looks like | This run |
|:--|:--|:--|
| CLI runs | `bsk --version` returns a version | `bsk 0.4.1` |
| Daemon running | `bsk status --json` returns pid and port | pid 9008 / ws_port 52800 |
| Extension connected | `bsk browsers --json` lists the browser with `version_skew: false` | chrome 156 / extension 0.4.1 / protocol 1.8 |
| `doctor` has no failures | All ok except "agent skill matches bundled CLI" = N/A | 7 ok, 1 N/A |
| Page readable | `snapshot` gives `@view` and refs with `[→ domain]` | `@view 1020x445`, `@e1 link "Learn more" [→ iana.org]` |
| Click can navigate | A below-the-fold link changes the URL after clicking | element `top=652.9`, viewport `465`, navigated to iana.org |
| Screenshot works | Returns PNG byte size and dimensions | 61,793 bytes / 1554×668 |
| Session can exit | `stopped` lists the session id | `stopped: ["cksh"]` |

### Three traps specific to Path B

1. **Actions need a cooperation context first.** A direct `click` / `evaluate` errors with `cooperation_sync_required`. Call `bsk cooperate sync` for a `context_id` and act immediately after; a page change invalidates the context, so sync again.
2. **`effect_state: "unknown"` is not a failure.** In the measured run that click had already taken effect. Check the URL from `tab list` first, then decide — never replay.
3. **Do not make the Agent Window too small.** With a 93 px viewport the extension overlay covers the click point and it errors with `Could not clear the extension overlay from the click point`. 800×600 or larger is recommended.

---

## Choosing between the two paths

| Your situation | Choice |
|:--|:--|
| Read a page under an account you are already logged into, without re-entering a password | Path B |
| Batch scraping without touching your own account or history | Path C |
| End-to-end regression testing of your own site | Path C |
| A complicated login flow (SMS, two-factor) where re-authenticating is expensive | Path B |

## Common blockers and what to do

| Symptom | Handling |
|:--|:--|
| `npm install -g` reports a permission error | Use a version manager such as nvm, or elevate per platform rules; do not `sudo` global packages |
| `bsk` / `agent-browser` command not found | Confirm the npm global bin directory is on PATH, restart the terminal, retry |
| Extension shows as installed but not connected | Check it is enabled for the current browser profile — multiple profiles are independent |
| Page opens but no content can be extracted | Confirm loading finished, then add a wait; if still empty, check whether login is required |
| Target site returns a verification page | This skill does not attempt adversarial bypass; stop and tell the user |
| `open` produces no output for a long time | First confirm `agent-browser install` completed; do not retry `open` repeatedly |
| `click` returns success but the page does not navigate | The element is most likely outside the viewport (confirmed on Path C). `scrollIntoView({block:'center'})` first, or add `--new-tab`; confirm with `get url` |
| `click --json` reports `Unknown ref` | The ref went stale with a page change; re-`snapshot` for a new ref, never reuse across steps |
| An element is missing from `snapshot` | It may be outside the viewport or rendered asynchronously; scroll or wait, then snapshot again |
| `bsk doctor` says the daemon cannot start (job object forbids breakaway) | Run `bsk daemon start --foreground` in a resident task and set `BSK_AUTO_START=0` for other commands |
| `bsk browsers` is empty | The extension is not loaded or not connected; Chrome 137+ ignores `--load-extension`, so use Chrome for Testing or have the user install the extension normally |
| `bsk click` reports `cooperation_sync_required` | `bsk cooperate sync` for a `context_id`, then act immediately with `--context` |
| `bsk click` reports `control_context_invalid` | A page change invalidated the context; sync again before clicking, never reuse an old context |
| `bsk click` reports `Could not clear the extension overlay` | The Agent Window viewport is too small and the overlay covers the click point; increase `--width`/`--height` |
| `bsk screenshot` with a path reports `unexpected argument` | Use `--out <path>`; positional arguments are not supported |
| `bsk` returns `effect_state: "unknown"` | Not a failure — "cannot confirm". Check the URL with `bsk tab list`, then decide; never replay |

## To be filled in

Once you have installed and run it, consider adding the following so the next person can compare directly:

1. Your operating system and Node version
2. The commands you actually ran and their raw output
3. The first blocker you hit and how you resolved it
4. Total time from install to a working run
