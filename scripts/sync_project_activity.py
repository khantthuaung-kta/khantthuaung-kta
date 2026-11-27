"""Refresh a small curated project activity section in the GitHub profile README.

The section changes only when the real public GitHub repository metadata changes.
No date stamps, fake commits, or personal access token required.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OWNER = "khantthuaung-kta"
PROJECTS = (
    ("techpulse-ai", "Tech news automation"),
    ("nihongo-companion-site", "Japanese learning platform"),
    ("n2-news-reader-demo", "News reader demo"),
)
START = "<!-- AUTO-PROJECT-ACTIVITY:START -->"
END = "<!-- AUTO-PROJECT-ACTIVITY:END -->"
README = Path("README.md")


def fetch_metadata(name: str) -> dict:
    request = Request(
        f"https://api.github.com/repos/{OWNER}/{name}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "khantthuaung-profile-project-sync",
            **({"Authorization": f"Bearer {os.environ['GH_TOKEN']}"} if os.environ.get("GH_TOKEN") else {}),
        },
    )
    with urlopen(request, timeout=20) as response:
        data = json.load(response)
    if data.get("private") or data.get("archived"):
        raise ValueError(f"{name} is not an active public repository")
    return {"name": name, "url": data["html_url"], "pushed": (data.get("pushed_at") or "")[:10]}


def main() -> int:
    original = README.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise SystemExit("README must contain exactly one start/end marker pair")
    if original.index(START) >= original.index(END):
        raise SystemExit("Invalid project activity markers")

    items = []
    for name, label in PROJECTS:
        try:
            items.append((fetch_metadata(name), label))
        except (HTTPError, URLError, TimeoutError, KeyError, ValueError, json.JSONDecodeError) as error:
            raise SystemExit(f"Cannot safely update profile: {name}: {error}") from error

    lines = [
        START,
        "<div align=\"center\">",
        "  <sub>Selected public projects · last repository push dates (UTC), not a coding streak</sub>",
        "</div>",
        "",
        "| Project | Focus | Last push (UTC) |",
        "| --- | --- | --- |",
    ]
    for item, label in items:
        lines.append(f"| [\`{item['name']}\`]({item['url']}) | {label} | {item['pushed'] or 'Unknown'} |")
    lines.extend(["", END])

    updated = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: "\n".join(lines),
        original,
        count=1,
        flags=re.DOTALL,
    )
    if updated == original:
        print("Project activity unchanged; no commit needed.")
        return 0
    README.write_text(updated, encoding="utf-8")
    print("Refreshed curated project activity from real GitHub metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
