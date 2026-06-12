"""Load a mesh and print the messages produced by the mesh_info filter."""

from __future__ import annotations

import argparse
from pathlib import Path

import pymeshlab2


DEFAULT_MESH = Path(__file__).resolve().parents[1] / "external/QMeshLab/tests/data/simple.off"


def main(argv: list[str] | None = None) -> pymeshlab2.FilterRunResult:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", nargs="?", default=str(DEFAULT_MESH), help="mesh file to inspect")
    parser.add_argument("--precision", type=int, default=2, help="decimal precision for metrics")
    args = parser.parse_args(argv)

    meshset = pymeshlab2.MeshSet()
    meshset.load_new_mesh(args.mesh)
    result = meshset.apply_filter("mesh_info", {"precision": args.precision})

    for message in result.info_messages:
        print(message)

    return result


if __name__ == "__main__":
    main()
