from __future__ import annotations

import argparse
from pathlib import Path

import pymeshlab2


DEFAULT_MESH = Path(__file__).resolve().parents[1] / "external/QMeshLab/tests/data/simple.off"


def main(argv: list[str] | None = None) -> Path:
    parser = argparse.ArgumentParser()
    parser.add_argument("mesh", nargs="?", default=str(DEFAULT_MESH), help="mesh file to normalize")
    parser.add_argument("--output", default="normalized.ply", help="where to write the normalized mesh")
    parser.add_argument("--target-size", type=float, default=1.0, help="largest output box dimension")
    parser.add_argument("--no-recenter", action="store_true", help="scale without recentering to origin")
    args = parser.parse_args(argv)

    output = Path(args.output)

    meshset = pymeshlab2.MeshSet()
    meshset.load_new_mesh(args.mesh)
    params = {}
    if args.target_size != 1.0:
        params["target_size"] = args.target_size
    if args.no_recenter:
        params["recenter"] = False
    meshset.apply_filter("normalize_unit_box", params)
    meshset.save_current_mesh(str(output))

    print(output)
    return output


if __name__ == "__main__":
    main()
