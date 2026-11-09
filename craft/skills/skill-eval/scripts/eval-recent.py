#!/usr/bin/env python3
"""Tell eval-changed.py's stall watchdog whether a run still writes.

Usage: eval-recent.py <seconds> <results dir> <tmp dir>

Exits 0 when the results dir, or any claude-eval-* workspace directly under
the tmp dir, holds a file or directory modified within the last <seconds>;
1 otherwise. Portable where `find -newermt` is not (BSD find).
"""
import os
import sys
import time


def recent(seconds, out, tmpdir):
    """Return whether anything under out or a claude-eval-* dir in tmpdir
    was modified within the last seconds."""
    since = time.time() - seconds
    roots = [out]
    try:
        roots += [os.path.join(tmpdir, d) for d in os.listdir(tmpdir) if d.startswith("claude-eval-")]
    except OSError:
        pass
    for root in roots:
        for dp, dns, fs in os.walk(root):
            for name in [dp] + [os.path.join(dp, f) for f in fs]:
                try:
                    if os.lstat(name).st_mtime >= since:
                        return True
                except OSError:
                    continue
    return False


if __name__ == "__main__":
    sys.exit(0 if recent(float(sys.argv[1]), sys.argv[2], sys.argv[3]) else 1)
