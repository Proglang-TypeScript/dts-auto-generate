#! /usr/bin/env python3

import sys
from pathlib import Path
from subprocess import run, TimeoutExpired

works = []
to_test = list(Path("testmodules").iterdir())
for i, dir in enumerate(to_test):
    assert dir.is_dir()

    progress = f"{i+1}/{len(to_test)}"
    print(f"{progress:<9} {dir.name:<20}", end=" ", file=sys.stderr)

    ok = False

    try:
        p = run(
            f"/rti/bin/runNew {dir.absolute()} {dir.name}".split(),
            text=True,
            env={"REQUIRE_ONLY": "true"},
            capture_output=True,
            timeout=5,
        )

        ok = p.returncode == 0
    except TimeoutExpired:
        pass

    if ok:
        works.append(dir.name)

    print("OK" if ok else "NOK", file=sys.stderr)

print("\n".join(works))
