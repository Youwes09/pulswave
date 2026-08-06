#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

FILES = {
    "chmech": "chem.inp",
    "chthermo": "therm.dat",
    "chtrans": "transportProperties",
}


def stage(src_prefix: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for ext, out_name in FILES.items():
        src = src_prefix.parent / f"{src_prefix.name}.{ext}"
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copyfile(src, out_dir / out_name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("src_prefix", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    stage(args.src_prefix, args.out_dir)


if __name__ == "__main__":
    main()
