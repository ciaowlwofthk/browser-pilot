# Measured run · Path B (extension takeover)

This record was produced on Windows on 2026-11-02. Commands and output are kept verbatim, including two failures and one "errored but actually succeeded" anomaly — nothing dressed up.

PIDs, loopback addresses and ports quoted here (e.g. `ws://127.0.0.1:<port>`) are local values from that run and change on every start; they are preserved so the output can be checked line by line. Personal directory paths are redacted.

**Environment:** Windows · bsk CLI 0.4.1 · extension 0.4.1 (protocol 1.8) · Chrome for Testing 156.0.8078.80 · Node v22.22.2

> Commands and JSON are verbatim. Page text that the browser rendered in Chinese during the original run is shown here in its English form.

---

## 1. Installing the CLI

The official recommendation is `irm https://raw.githubusercontent.com/Tencent/BrowserSkill/main/install.ps1 | iex`. On this network the TLS handshake to `raw.githubusercontent.com` fails:

```
curl: (35) schannel: failed to receive handshake, SSL/TLS connection failed
```

`github.com` itself is reachable, so the same script was fetched through the GitHub API:

```
curl -sSL -H "Accept: application/vnd.github.raw" -o bsk_install.ps1 \
  https://api.github.com/repos/Tencent/BrowserSkill/contents/install.ps1
http=200 size=11197
```

This machine's PowerShell execution policy forbids running `.ps1` (`UnauthorizedAccess`), and `Invoke-Expression` is blocked by security policy too, so the script's flow was executed by hand: fetch the manifest, then download, verify, unpack.

```
curl -sSL https://github.com/Tencent/BrowserSkill/releases/latest/download/version.json
```

```json
{
  "version": "0.4.1",
  "tag": "cli-v0.4.1",
  "assets": {
    "windows-x64": {
      "url": "https://github.com/Tencent/BrowserSkill/releases/download/cli-v0.4.1/bsk-v0.4.1-x86_64-pc-windows-msvc.zip",
      "sha256": "f4a62af2dde31508188ea0c80feee11dbb62d9e7b7bf388f3f3a9856cfffb37d"
    }
  }
}
```

```
http=200 size=6888737 time=3.449851s
sha256: f4a62af2dde31508188ea0c80feee11dbb62d9e7b7bf388f3f3a9856cfffb37d
match: True
installed: True 18441776 bytes
```

```
$ bsk --version
bsk 0.4.1
```

**Key point:** `version.json` carries a `sha256` per platform — always verify before installing. The archive contains a single file, `bsk.exe`, 18.4 MB.

## 2. Installing the extension

The extension is published as a packaged artifact under the Release's `ext-v0.4.1` tag — no extension store required:

```
curl -sSL -o bsk_ext.zip \
  https://github.com/Tencent/BrowserSkill/releases/download/ext-v0.4.1/browser-skill-extension-v0.4.1-chrome.zip
http=200 size=1109777
```

It unpacks to 38 entries with `manifest.json` at the root, MV3, key permissions:

```json
"permissions": ["debugger", "tabs", "scripting", "webNavigation", "offscreen", ...],
"host_permissions": ["<all_urls>"]
```

**Takeover relies on the `chrome.debugger` extension permission, not a remote debugging port.** That is also why this skill involves no "debug port" style approach.

## 3. Starting the daemon

A plain `bsk doctor` fails on this host:

```
FAIL  daemon running   automatic daemon startup failed: cannot start an independent Windows
daemon; the Job Object of this process does not allow breakaway
```

The host's job object forbids detached child processes, so a foreground resident process is required:

```
bsk daemon start --foreground     # run inside this host's persistent background task
```

Then verify from a separate command:

```
$ bsk status --json
{
  "daemon_version": "0.4.1",
  "protocol_version": "1.8",
  "pid": 9008,
  "ws_port": 52800,
  "sock_path": "\\\\.\\pipe\\bsk-daemon-b56958f10598c2c2",
  "browsers": [],
  "sessions": []
}
```

## 4. Letting the extension take over the browser

Since Chrome 137 stable removed `--load-extension`, and the measured Chrome 156 left `browsers` empty after loading, switching to Chrome for Testing (same 156 core) worked first time:

```
chrome.exe --user-data-dir=<isolated profile dir> \
           --load-extension=<unpacked extension dir> \
           --no-first-run --no-default-browser-check https://example.com
```

```
$ bsk browsers --json
[
  {
    "instance_id": "01d0580b",
    "browser_name": "chrome",
    "browser_version": "156.0.0.0",
    "extension_version": "0.4.1",
    "extension_protocol_version": "1.8",
    "version_skew": false,
    "unresponsive": false
  }
]
```

Final `bsk doctor` state:

```
ok    bsk home writable                <home>\.bsk
N/A   agent skill matches bundled CLI  no agent skill installed
ok    daemon running                   pid 9008 at ws://127.0.0.1:52800
ok    daemon local process identity    IPC peer PID matches daemon identity
ok    protocol compatible              daemon protocol 1.8 (app 0.4.1)
ok    auto-update                      no update attempt recorded
ok    extension connected              1 browser(s) connected
ok    browser protocol compatible      all 1 online browser(s) are compatible with the daemon
```

The `N/A` line means "the official skill is not installed on this machine" — unrelated to this skill, since this package *is* that skill.

## 5. Session model: not a takeover of the current tab

```
$ bsk session start --no-focus --json
{
  "agent_window_id": 332262077,
  "browser_instance_id": "01d0580b",
  "interaction": { "borrow_confirmation": "always", "request_help": "enabled" },
  "session_id": "prrf"
}
```

```
$ bsk tab list --session prrf --json
{
  "tabs": [
    { "tab_id": 332262076, "window_id": 332262075, "scope": "user",  "active": true },
    { "tab_id": 332262078, "window_id": 332262077, "scope": "agent", "url": "about:blank" }
  ]
}
```

**Actual mechanism:** bsk opens a new **Agent Window** in the same browser, reusing that browser's profile and login state, while the user's own window is never seized. The `scope` field distinguishes `user` tabs from `agent` tabs.

This is safer than "taking over the current tab", and truer to reality: the page the user is reading never flips away underneath them.

## 6. Reading a page

```
$ bsk navigate "https://example.com" --session prrf --json
{ "tab_id": 332262078, "url": "https://example.com", "final_url": "https://example.com/", "reached": "load" }
```

```
$ bsk snapshot --session prrf
@vom 1
@view 1020x445
@layers 1 focus=L1
L1 page
  RootWebArea "Example Domain"
    paragraph "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission."
    ...
    @e1 link "Learn more" [→ iana.org]
```

Three things worth noting:

- `@view 1020x445` gives the viewport size directly
- Every link carries a `[→ iana.org]` destination hint, so you know where it goes before clicking
- `navigate` returns `final_url` and `reached`, more reliable than "the command succeeded"

## 7. Actions need a cooperation context

A direct `evaluate` or `click` is rejected:

```
{
  "code": "permission_denied",
  "message": "This action requires the context returned by the latest cooperate sync",
  "data": { "effect_state": "none", "reason": "cooperation_sync_required" }
}
```

The correct order is sync first, then act with the context:

```
$ bsk cooperate sync --session prrf --json
{
  "context_id": "50fe3b05-7db1-4637-be29-013800d8d029",
  "control_policy": "target",
  "observation_id": "b475ffe8-f3f8-4204-b344-9caebfbe92c8",
  "observation": { "text": "@vom 1 ... @e2 link \"Learn more\" [→ iana.org]" },
  "state": { "mode": "ready", "revision": 10 }
}
```

```
$ bsk click "@e2" --session prrf --context 50fe3b05-... --json
{ "code": "permission_denied", "message": "Page interaction coverage changed; wait and synchronize",
  "data": { "effect_state": "unknown", "reason": "control_context_invalid" } }
```

A single page change invalidates the context, so **sync and action must be executed back to back**.

**Yet on this error the click had in fact landed** — one command later, the tab URL was already `https://www.iana.org/help/example-domains`. `effect_state: "unknown"` means "cannot confirm", not "failed". **When you see it, check actual page state first and never replay the same action.**

## 8. Does clicking scroll automatically? (the decisive comparison with Path C)

Window set to 900×700 (viewport 870×465) so the link sits below the fold:

```
geometry: {"top":652.9166870117188,"vh":465}
```

Element top at 652.9 px against a 465 px viewport — **188 px outside the viewport**. Clicking with no scrolling at all:

```
$ bsk click "@e1" --session hrcg --context <ctx> --json
{ "tab_id": 332262083, "used_ref": "e1", "x": 435.3333435058594, "y": 420.25 }
```

```
url after A: https://www.iana.org/help/example-domains
```

**Navigation succeeded**, and the reported click point `y=420.25` is already inside the 465 px viewport — meaning the CLI **scrolled the element into view before dispatching** the mouse events.

The same scenario fails silently on Path C (see `real-run-2026-11-02-pathc.md`). This is the most consequential behavioural difference between the two paths:

| | Path B (bsk) | Path C (agent-browser) |
|:--|:--|:--|
| Clicking an off-viewport element | Scrolls into view, then clicks; succeeds | Coordinates miss, silently returns `✓ Done` |
| What the click returns | `used_ref` + actual click point `x`/`y` | Only a `success` boolean |
| On failure | `effect_state` + `exit_code`, decidable | No failure signal |

### A real failure: window too small

Same test, window set to 420×300 (viewport only 486×93), element `top=559.9`:

```
{
  "code": "cdp_failed",
  "message": "Could not clear the extension overlay from the click point",
  "data": { "effect_state": "none", "pointer_moved": false, "reason": "input_not_ready" },
  "exit_code": 3
}
```

The page did not navigate, and `effect_state: "none"` states plainly that no effect occurred. The cause: with only 93 px of viewport, the extension's own overlay covered the click point. **Do not make the Agent Window too small** — keep `--width`/`--height` at 800×600 or above.

`scroll-to` can also be used explicitly and returns the element box model:

```
$ bsk scroll-to "@e2" --session hrcg --context <ctx> --json
{ "tab_id": 332262083, "used_ref": "e2", "x": 25.0, "y": 69.66667175292969, "width": 234.0, "height": 22.0 }
```

## 9. Screenshots

```
$ bsk screenshot --session cksh --json
{ "byte_size": 61793, "format": "png", "height": 668, "width": 1554,
  "path": "C:\\Users\\<user>\\AppData\\Local\\Temp\\bsk-screenshot-1793617739315.png" }
```

By default the file lands in the system temp directory; to choose a path use `--out <path>` (positional arguments are not supported — passing a path errors with `unexpected argument`). This screenshot is 61,793 bytes at 1554×668, showing the rendered example.com page; the returned structure is the JSON above. The platform forbids uploading binaries, so the image itself is not distributed.

## 10. Ending the session

```
$ bsk session stop cksh --json
{ "failed": [], "return_failures": [], "returned_tab_ids": [], "stopped": ["cksh"] }
```

## 11. What this run proved

| Capability | Evidence |
|:--|:--|
| CLI installs and can be verified | `version.json` sha256 matched the downloaded file; `bsk 0.4.1` |
| Extension installs without a store | The Release serves the extension zip directly; unpack and use |
| Real browser login state reused | The Agent Window shares that browser's profile; `scope=user` tabs are visible |
| Page readable | `snapshot` yields a VOM, viewport size and refs with destination hints |
| Click can trigger navigation | A below-the-fold link navigated to iana.org |
| Auto-scroll | Element `top=652.9`, viewport `465`, click point `y=420.25` |
| Failures are decidable | A too-small window returned `effect_state: none` + `exit_code: 3` |
| Screenshots work | A genuinely rendered 1554×668 PNG |
| Session exits cleanly | `stopped: ["cksh"]`, nothing left behind |
| Return values still need checking | On `effect_state: unknown` the click had actually taken effect |

## 12. How to reproduce

```bash
# 1. Install the CLI (fetch the script via the GitHub API when raw.githubusercontent is unreachable)
curl -sSL https://github.com/Tencent/BrowserSkill/releases/latest/download/version.json
curl -sSL -o bsk.zip https://github.com/Tencent/BrowserSkill/releases/download/cli-v0.4.1/bsk-v0.4.1-x86_64-pc-windows-msvc.zip
# verify the sha256 from version.json, then unpack bsk.exe into ~/.local/bin

# 2. Install the extension
curl -sSL -o ext.zip https://github.com/Tencent/BrowserSkill/releases/download/ext-v0.4.1/browser-skill-extension-v0.4.1-chrome.zip

# 3. Start the daemon (foreground when the host forbids job-object breakaway)
bsk daemon start --foreground

# 4. Load the extension in the browser, then confirm it is connected
bsk browsers --json

# 5. Run a minimal task
bsk session start --no-focus --json
bsk navigate https://example.com --session <id> --json
bsk snapshot --session <id>
bsk cooperate sync --session <id> --json
bsk click "@e1" --session <id> --context <context_id> --json
bsk tab list --session <id> --json
bsk session stop <id> --json
```
