"""Generate a small noisy isosurface mesh."""

from __future__ import annotations

import argparse

import pymeshlab2


def main(argv: list[str] | None = None) -> pymeshlab2.FilterRunResult:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resolution", type=int, default=16, help="volume resolution")
    args = parser.parse_args(argv)

    meshset = pymeshlab2.MeshSet()
    result = meshset.apply_filter("create_noisy_isosurface", {"resolution": args.resolution})
    if not result.new_mesh_indices:
        raise RuntimeError("create_noisy_isosurface did not create a mesh")

    print(f"mesh_count={meshset.mesh_count()}")
    print(f"new_mesh_indices={result.new_mesh_indices}")
    return result


if __name__ == "__main__":
    main()
