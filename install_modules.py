#! /usr/bin/env python3

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory

if len(sys.argv) != 2:
    print("missing path to list of files")
    exit(1)

modules = Path(sys.argv[1]).read_text().splitlines()
if not modules:
    print(f"{sys.argv[1]} does not contain any module names")
    exit(1)

root = Path("testmodules")


def install(module: str):
    print("Installing", module)
    module_root = root / module
    module_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        f"npm --ignore-scripts --prefix {module_root} --loglevel error install {module}".split(),
        check=True,
        text=True,
        capture_output=True,
    )


with ThreadPoolExecutor(max_workers=8) as executor:
    for module in modules:
        executor.submit(install, module)
