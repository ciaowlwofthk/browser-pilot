# Site experience (site-patterns)

> This file describes a **path-agnostic** extension mechanism; both Path B and Path C can use it.

Stores "hints that worked on a specific site" keyed by domain. **No site experience is built in by default.** File naming: `references/site-patterns/<domain>.md`.

## File format

Each entry has three parts, all stated explicitly:

- **Symptom**: what the generic pattern runs into on this site (e.g. lazy-loaded content, the button sits inside a shadow DOM)
- **Hint**: what actually works for that symptom (e.g. `scrollIntoView` before clicking, wait for a particular selector)
- **Fallback when it stops working**: which generic action to return to when the hint fails (e.g. re-snapshot, change the selector)

## Usage conventions

1. Treat an entry as "a hint that may help", never as a rule; if it fails, fall back to the generic pattern.
2. Entries must be expirable: state the date they applied and the page-version characteristics, so a redesign automatically makes the entry suspect.
3. When adding an entry, cite the evidence (which task, what symptom). No unsupported guesses.
4. **Never store credentials, cookies, tokens or personal data.** This directory holds operating hints only.
5. Matching: before a task, look up the entry for the target domain; with no match, use the generic pattern alone.

## Adding experience

When a task shows that "the generic pattern repeatedly fails on one site but some adjustment works", write the three-part entry into that domain's file. Do not modify `SKILL.md` or the path documents.
