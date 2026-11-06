# Measured run · Path C (standalone instance)

This record was produced on Windows on 2026-11-02. Commands and output are kept verbatim — nothing polished, including one result that did not meet expectations.

**Environment:** Windows · Node v22.22.2 · npm 10.9.7 · agent-browser 0.27.0 · Chrome for Testing 156.0.8078.80

> Commands, exit states and parameters below are verbatim. Page text that the browser rendered in Chinese during the original run is shown here in its English form.

---

## 1. Installation

```
npm install -g agent-browser
```

Actual output:

```
added 1 package in 14s
```

The CLI itself installs fast because it is only a scheduler; the actual browser core is a separate download.

```
agent-browser install
```

Actual output (excerpt):

```
Installing Chrome...
  Downloading Chrome 156.0.8078.80 for win64
  https://storage.googleapis.com/chrome-for-testing-public/156.0.8078.80/win64/chrome-win64.zip
  199/199 MB (100%)
✓ Chrome 156.0.8078.80 installed successfully
  Location: <home>\.agent-browser\browsers\chrome-156.0.8078.80
```

(The user name in the install path is redacted; all other output is verbatim.)

**This step took 1 minute 3 seconds and downloaded 199 MB.** Note: if you skip `install` and run `open` directly, the program tries to pull the core in the background with no output for a long time, which looks like a hang — the measured wait exceeded 10 minutes without returning. **The correct order is install first, then open.**

## 2. Four-step verification

```
agent-browser open https://example.com
```

```
✓ Example Domain
  https://example.com/
```

```
agent-browser wait --load networkidle
```

```
✓ Done
```

```
agent-browser snapshot
```

The output is a page structure tree with reference markers on interactive elements (first two lines shown):

```
- paragraph
  - StaticText "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission."
...
- link "Learn more" [ref=e1]
```

```
agent-browser get title
```

```
Example Domain
```

```
agent-browser screenshot shot.png
```

```
✓ Screenshot saved to shot.png
```

The generated file is a 41 KB PNG. The platform forbids uploading binaries, so the screenshot is not distributed; only the generating command and its output are kept here.

```
agent-browser close
```

```
✓ Browser closed
```

## 3. One result that did not meet expectations

While verifying whether an element ref could trigger navigation, two clicks were issued:

```
agent-browser click "@e1"
✓ Done

agent-browser click "a"        # retry with a CSS selector
✓ Done
```

Both returned success, but checking afterwards showed the **page had not navigated**:

```
agent-browser get url
https://example.com/

agent-browser tab list
→ [t1] example.com - https://example.com/
```

To rule out "the link itself is broken", the element source was read with `eval`:

```
agent-browser eval "document.querySelector('a').outerHTML"
"<a href=\"https://iana.org/help/example-domains\">Learn more</a>"
```

A plain `<a href>` — no `target` attribute, no JS interception.

A native DOM click was then used as a control, bypassing the CLI's click implementation:

```
agent-browser eval "document.querySelector('a').click()"
✓ Done

agent-browser get url
https://iana.org/help/example-domains
```

**The page navigated.** Link, browser and navigation chain were all fine — the problem lay in the `click` command's own implementation.

### Narrowing it down

**Step one: look at the real return with `--json`.** In non-JSON mode `✓ Done` masks failure; with `--json` you see it:

```
agent-browser click "@e1" --json
{"success":false,"error":"Unknown ref: e1"}
```

The ref had gone stale — page state changed after the previous `snapshot`, invalidating the old ref, yet normal mode still printed `✓ Done`.

**Step two: re-snapshot for a fresh ref and retry:**

```
agent-browser snapshot
agent-browser click "@e1" --json
{"success":true,"tag":"a","text":"Learn more"}

agent-browser get url
https://example.com/          # still no navigation
```

This time `success` really was `true` — valid ref, element matched — yet navigation still did not happen.

**Step three: open in a new tab to check whether href resolution works:**

```
agent-browser click "@e1" --new-tab --json
{"success":true,"tab":"t2"}

agent-browser tab list
→ [t1] example.com - https://example.com/
  [t2] Example Domains - https://www.iana.org/help/example-domains
```

The URL in the new tab is exactly right. So element location and href resolution are fine; **only "click within the current tab" fails**.

**Step four: check the element's geometry.** This is the root cause:

```
agent-browser eval "JSON.stringify(document.querySelector('a').getBoundingClientRect())"
{"x":294,"y":677.328125,"width":66,"height":17,...}

agent-browser eval "JSON.stringify({h:window.innerHeight,w:window.innerWidth})"
{"h":566,"w":1024}
```

The element's top edge sits at **677 px** while the viewport is only **566 px** tall — the element is **outside** the visible area (111 px below it).

**Step five: scroll it into view, then click:**

```
agent-browser eval "document.querySelector('a').scrollIntoView({block:'center'})"

agent-browser eval "document.querySelector('a').getBoundingClientRect().top"
510

agent-browser click "@e1" --json
{"success":true,...}

agent-browser get url
https://www.iana.org/help/example-domains
```

**Navigation succeeded.**

### Root cause

`agent-browser click` **dispatches mouse events by coordinates**: it takes the element's centre point and sends mousedown / mouseup / click there. It **does not scroll the element into view first**. When the element is outside the viewport, the coordinates land outside the visible area, the mouse events miss and hit nothing — but the command's own action, "dispatch the events", did succeed, so it returns `✓ Done` / `success:true`.

This has nothing to do with core version or page structure; it is inherent to coordinate dispatch.

### The correct usage

Before clicking anything that may be below the fold, scroll it into view:

```bash
agent-browser eval "document.querySelector('<selector>').scrollIntoView({block:'center'})"
agent-browser click "@e1" --json
agent-browser wait --load networkidle
agent-browser get url          # verify the result separately
```

Or just use `--new-tab`, which takes a different code path and is not coordinate-bound.

### Three lessons to remember

1. **`✓ Done` in non-JSON mode masks failure.** In automation always add `--json` and check the `success` field.
2. **Refs go stale.** After any page change you must re-`snapshot`; never reuse an old ref across steps.
3. **Always verify the result separately after `click`.** Use `get url` or `snapshot` to confirm the state actually changed; never trust the return value.

## 4. What this run proved

| Capability | Evidence |
|:--|:--|
| Standalone instance starts | `open` returned a real page title and URL, without the user's installed Chrome |
| Page structure readable | `snapshot` produced a structure tree with `[ref=e1]` |
| Content extractable | `get title` and `eval` both returned real data |
| Screenshots work | A 41 KB PNG was generated |
| Navigation chain works | `open` to a second site succeeded, including server-side redirect detection |
| Click can trigger navigation | After `scrollIntoView`, `click` navigated to iana.org |
| Process exits cleanly | No leftover instance after `close` |
| Return value ≠ result | Clicking an off-viewport element returned `✓ Done` without effect; cause located and usage corrected |

## 5. How to reproduce

```bash
npm install -g agent-browser
agent-browser install
agent-browser open https://example.com
agent-browser wait --load networkidle
agent-browser snapshot
agent-browser screenshot shot.png
agent-browser get title
agent-browser close
```

If `open` produces no output for a long time, first confirm whether `install` completed — do not retry `open` repeatedly.

The full correct shape for click operations:

```bash
agent-browser open https://example.com
agent-browser snapshot
agent-browser eval "document.querySelector('a').scrollIntoView({block:'center'})"
agent-browser click "@e1" --json
agent-browser wait --load networkidle
agent-browser get url
```
