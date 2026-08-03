"""Check live survey option count."""

from __future__ import annotations

import re
import sys

import requests

URL = "https://human-ai-survey.onrender.com/"


def main() -> None:
    session = requests.Session()
    home = session.get(URL, timeout=90)
    home.raise_for_status()
    print("home badge.claude css:", "badge.claude" in home.text)
    print("home mentions Claude:", "Claude" in home.text)

    survey = session.post(f"{URL.rstrip('/')}/start", allow_redirects=True, timeout=90)
    survey.raise_for_status()
    print("survey url:", survey.url)
    badges = re.findall(r'class="badge ([^"]+)"[^>]*>([^<]+)<', survey.text)
    print("options:", badges)
    print("count:", len(badges))
    if len(badges) != 5:
        sys.exit(1)


if __name__ == "__main__":
    main()
