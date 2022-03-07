#!/usr/bin/env python3

import tomli
import tomli_w
import shutil
import subprocess
import sys
from pathlib import Path


root_dir = Path(__file__).parent.resolve()
crate_dir = root_dir / "resvg"
dist_dir = root_dir / "dist"
cargo_manifest_path = crate_dir / "Cargo.toml"
pyproject_toml_path = root_dir / "pyproject.toml"
py_readme = root_dir / "README.rst"


def main():
    # maturin expects the 'pyproject.toml' file to be located in the same
    # directory as Cargo.toml, so we copy it there
    shutil.copyfile(pyproject_toml_path, crate_dir / "pyproject.toml")
    # We also want to include our own README.rst in the source distribution,
    # alongside the original README.md
    shutil.copyfile(py_readme, crate_dir / "README.python.rst")

    # resvg's top-level Cargo.toml declares a workspace with explicit members
    # (subfolders) and each members' Cargo.toml also explicitly points back to the
    # root directory in the package.workspace key. Maturin doesn't like this setup
    # (it complains cargo metadata can't find the members' manifests), so below
    # I modify the manifests such that the 'members' key of [workspace] section from
    # the root Cargo.toml, as well as the 'workspace' key of [package] section of the
    # members' Cargo.toml, are both omitted and implicit. Cargo can figure these out
    # automatically, see:
    # https://rust-lang.github.io/rfcs/1525-cargo-workspace.html#implicit-relations
    cargo_manifest = tomli.load(cargo_manifest_path.open("rb"))
    if "workspace" in cargo_manifest and "members" in cargo_manifest["workspace"]:
        workspace_members = cargo_manifest["workspace"].pop("members")
        for member in workspace_members:
            member_dir = crate_dir / member
            assert member_dir.is_dir()
            member_manifest = tomli.load((member_dir / "Cargo.toml").open("rb"))
            if (
                "package" in member_manifest
                and "workspace" in member_manifest["package"]
            ):
                workspace_root = member_dir / member_manifest["package"]["workspace"]
                assert workspace_root.resolve() == crate_dir
                del member_manifest["package"]["workspace"]
                tomli_w.dump(member_manifest, (member_dir / "Cargo.toml").open("wb"))
        tomli_w.dump(cargo_manifest, cargo_manifest_path.open("wb"))

    try:
        cmd = {
            "sdist": ["maturin", "sdist"],
            "wheel": ["maturin", "build", "--no-sdist", "--release"],
        }[sys.argv[1]]
    except (IndexError, KeyError):
        sys.exit("usage: build.py [sdist|wheel]")

    return subprocess.call(
        cmd + ["-o", str(dist_dir)] + sys.argv[2:], cwd=str(crate_dir)
    )


if __name__ == "__main__":
    sys.exit(main())
