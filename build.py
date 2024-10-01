#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


root_dir = Path(__file__).parent.resolve()
dist_dir = root_dir / "dist"


def main():
    try:
        cmd = {
            "sdist": ["maturin", "sdist"],
            "wheel": ["maturin", "build", "--release"],
        }[sys.argv[1]]
    except (IndexError, KeyError):
        sys.exit("usage: build.py [sdist|wheel]")

    args = sys.argv[2:]
    if "--universal2" in args:
        cmd.extend(["--target", "universal2-apple-darwin"])
        args.remove("--universal2")

    return subprocess.call(
        cmd + ["-o", str(dist_dir)] + args
    )


if __name__ == "__main__":
    sys.exit(main())
