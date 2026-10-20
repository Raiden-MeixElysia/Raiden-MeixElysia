"""Rewrites every <!--stars:owner/repo-->…<!--/stars--> span in README.md with the repo's current star count."""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parents[2] / "README.md"
SPAN = re.compile(r"<!--stars:([\w.-]+/[\w.-]+)-->.*?<!--/stars-->")


def stars(repo: str) -> int:
    request = urllib.request.Request(f"https://api.github.com/repos/{repo}")
    request.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["stargazers_count"]


def main() -> None:
    text = README.read_text(encoding="utf-8")
    repos = sorted(set(SPAN.findall(text)))
    if not repos:
        sys.exit(f"{README}: no stars spans found")
    counts = {repo: stars(repo) for repo in repos}
    updated = SPAN.sub(lambda m: f"<!--stars:{m[1]}-->★ {counts[m[1]]:,}<!--/stars-->", text)
    README.write_text(updated, encoding="utf-8", newline="\n")
    for repo, count in counts.items():
        print(f"{repo}: {count}")


if __name__ == "__main__":
    main()
