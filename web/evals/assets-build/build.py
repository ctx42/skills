"""Build the dashboard into an output directory (default dist/).

Like a bundler, it first empties the output directory, then copies the
entry HTML and the files it references. Usage: python3 build.py [--outDir DIR]
"""

import argparse
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = ["index.html", "style.css", "app.js", "lib.js"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outDir", default=os.path.join(ROOT, "dist"))
    out = parser.parse_args().outDir
    os.makedirs(out, exist_ok=True)
    for name in os.listdir(out):
        path = os.path.join(out, name)
        shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    for name in FILES:
        shutil.copy(os.path.join(ROOT, name), out)
    print(f"built {len(FILES)} files into {out}")


if __name__ == "__main__":
    main()
