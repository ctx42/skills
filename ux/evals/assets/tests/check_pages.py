"""Fails when a page links to a local file that does not exist."""
import glob
import os
import sys
from html.parser import HTMLParser

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src", "data-source") and value:
                self.refs.append(value)


def main():
    missing = []
    for page in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        p = Links()
        with open(page) as f:
            p.feed(f.read())
        for ref in p.refs:
            if "://" in ref or ref.startswith(("#", "mailto:")):
                continue
            if not os.path.exists(os.path.join(ROOT, ref.split("#")[0])):
                missing.append(f"{os.path.basename(page)}: {ref}")
    for m in missing:
        print("missing:", m)
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
