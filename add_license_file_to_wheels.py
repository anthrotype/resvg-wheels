#!/usr/bin/env python3

import sys
from pathlib import Path
import shutil
from wheeltools import InWheel


root_dir = Path(__file__).parent.resolve()
crate_dir = root_dir / "resvg"
license = crate_dir / "LICENSE.txt"


def main():
    # maturin has problems adding the license text to the wheel archive yet so we
    # have to do it ourselves: cf. https://github.com/PyO3/maturin/issues/829
    for wheel_file in sys.argv[1:]:
        print(f"Adding '{license.name}' to '{wheel_file}'")
        with InWheel(in_wheel=wheel_file, out_wheel=wheel_file) as tmpdir:
            distinfo = next(Path(tmpdir).glob("*.dist-info"))
            assert distinfo.is_dir()
            shutil.copyfile(license, distinfo / "LICENSE")


if __name__ == "__main__":
    sys.exit(main())
