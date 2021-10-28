#! /usr/bin/env python3

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

modfile = Path("modules.txt")
if modfile.exists():
    modules = modfile.read_text().splitlines()
else:
    with TemporaryDirectory() as tmp:
        subprocess.run(
            f"git clone --depth 1 https://github.com/DefinitelyTyped/DefinitelyTyped.git {tmp}".split(),
            check=True,
            text=True,
        )

        modules = [
            path.name for path in (Path(tmp) / "types").iterdir() if path.is_dir()
        ]
        modules.sort()

    modfile.write_text("\n".join(modules))

print(len(modules), modules[:10])
TIMEOUT = 10

def check(module: str):
    try:
        with TemporaryDirectory() as tmp:
            print("Checking", module)
            cp = subprocess.run(
                f"npm --ignore-scripts --prefix {tmp} --loglevel error install {module}".split(),
                text=True,
                capture_output=True,
                timeout=TIMEOUT,
            )
            if cp.returncode != 0:
                print(module, "not found")
                return

            cp = subprocess.run(
                f"node checker.js {tmp} {module}".split(),
                text=True,
                capture_output=True,
                timeout=TIMEOUT,
            )
            if cp.returncode == 0:
                print(module, "OK")
                return module

            print(module, "NOK")
    except subprocess.TimeoutExpired:
        print(module, "TIMEOUT")


with ThreadPoolExecutor(max_workers=8) as executor:
    okay = [module for module in executor.map(check, modules) if module]

Path("okay.txt").write_text("\n".join(okay))
