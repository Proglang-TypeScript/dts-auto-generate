#! /usr/bin/env python3

import re
import sys
from pathlib import Path
from subprocess import TimeoutExpired, run

with open("works.txt") as f:
    works = [l.strip() for l in f if not l[0] == "#"]

root = Path("testmodules")
new = []
for module in works:
    ok = True

    for path in (root / module / "node_modules" / module).rglob("*.js"):
        if "jalangi" in path.name:
            continue

        with path.open() as f:
            ok &= re.search(r"(this\.|let\s+)\w+\s*=", f.read()) is None

    if ok: new.append(module)

    print(module, "OK" if ok else "NOK", file=sys.stderr)

Path("works_filtered.txt").write_text("\n".join(new) + "\n")
