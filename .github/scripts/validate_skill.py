#!/usr/bin/env python3
"""Validate a SKILL.md skill repository.

Checks:
  1. SKILL.md exists, starts with a closed YAML frontmatter block, no BOM
  2. required frontmatter keys: name, version, description, license
  3. version follows semver (X.Y.Z)
  4. a LICENSE file exists at repo root
  5. relative Markdown links resolve to existing files
  6. text files use LF line endings
  7. required directories exist: references/ and examples/

Usage: python3 validate_skill.py [repo-root]
Exit code 0 = pass, 1 = fail.
"""
import os
import re
import sys

REQUIRED_KEYS = ("name", "version", "description", "license")
TEXT_EXTS = {".md", ".json", ".yml", ".yaml", ".sh", ".ps1", ".txt", ".html"}
FENCE_RE = re.compile(r"^```.*?^```", re.S | re.M)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def main(root):
    problems = []

    def fail(msg):
        problems.append(msg)

    skill_path = os.path.join(root, "SKILL.md")
    if not os.path.isfile(skill_path):
        print("FAIL SKILL.md missing")
        return 1

    raw = open(skill_path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        fail("SKILL.md has a UTF-8 BOM")
    lines = raw.decode("utf-8", errors="replace").splitlines()

    front = {}
    if not lines or lines[0].strip() != "---":
        fail("SKILL.md must start with --- frontmatter")
    else:
        try:
            end = lines.index("---", 1)
        except ValueError:
            end = -1
        if end < 0:
            fail("SKILL.md frontmatter is not closed with ---")
        else:
            for line in lines[1:end]:
                m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
                if m:
                    front[m.group(1)] = m.group(2).strip()

    for key in REQUIRED_KEYS:
        if not front.get(key):
            fail(f"frontmatter missing key: {key}")

    version = front.get("version", "")
    if version and not SEMVER_RE.match(version):
        fail(f"version is not semver (X.Y.Z): {version}")

    if not any(
        os.path.isfile(os.path.join(root, name))
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt")
    ):
        fail("no LICENSE file at repo root")

    for directory in ("references", "examples"):
        if not os.path.isdir(os.path.join(root, directory)):
            fail(f"missing directory: {directory}/")

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            ext = os.path.splitext(name)[1].lower()
            if ext in TEXT_EXTS:
                data = open(path, "rb").read()
                if b"\r\n" in data:
                    fail(f"CRLF line endings: {rel}")
                if data.startswith(b"\xef\xbb\xbf"):
                    fail(f"UTF-8 BOM: {rel}")
            if ext == ".md":
                text = open(path, encoding="utf-8", errors="ignore").read()
                text = FENCE_RE.sub("", text)
                for target in LINK_RE.findall(text):
                    target = target.strip()
                    if target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    path_part = target.split("#", 1)[0].strip()
                    path_part = path_part.split(" ", 1)[0]  # drop optional "title"
                    if not path_part:
                        continue
                    resolved = os.path.normpath(os.path.join(dirpath, path_part))
                    if not os.path.exists(resolved):
                        fail(f"broken link in {rel}: {target}")

    if problems:
        for problem in problems:
            print(f"FAIL {problem}")
        return 1

    print(
        "OK  {} v{} — frontmatter, links, line endings all pass".format(
            front.get("name", "?"), version or "?"
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
