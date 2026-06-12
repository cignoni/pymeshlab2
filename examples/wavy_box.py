"""Create a wavy box from QMeshLab filters.

Pipeline:
1. create a cube,
2. uniformly refine it with midpoint subdivision,
3. perturb vertices with a sinusoidal geometric function,
4. regularize it with isotropic remeshing,
5. optionally save the result.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pymeshlab2


REQUIRED_FILTERS = {
    "create_box",
    "meshing_surface_subdivision_midpoint",
    "per_vertex_geometric_function",
    "meshing_isotropic_explicit_remeshing",
}


def _require_filters(meshset: pymeshlab2.MeshSet) -> None:
    available = {item.id for item in meshset.list_filters()}
    missing = sorted(REQUIRED_FILTERS - available)
    if missing:
        missing_list = ", ".join(missing)
        raise RuntimeError(
            "This example needs QMeshLab create, meshing, and func filters. "
            f"Missing filter ids: {missing_list}"
        )


def build_wavy_box(
    *,
    side: float = 1.0,
    midpoint_iterations: int = 4,
    remesh_iterations: int = 8,
    target_edge_fraction: float = 1.0 / 24.0,
) -> pymeshlab2.MeshSet:
    meshset = pymeshlab2.MeshSet()
    _require_filters(meshset)

    amplitude = side / 5.0
    frequency = 3.0
    angular_frequency = 2.0 * math.pi * frequency / side
    target_edge_length = side * target_edge_fraction

    meshset.apply_filter("create_box", {"size": side})
    meshset.apply_filter(
        "meshing_surface_subdivision_midpoint",
        {
            "Iterations": midpoint_iterations,
            "Threshold": 0.0,
            "Selected": False,
        },
    )
    meshset.apply_filter(
        "per_vertex_geometric_function",
        {
            "x": "x",
            "y": "y",
            "z": f"z + ({amplitude:.17g}) * sin(({angular_frequency:.17g}) * x) * sin(({angular_frequency:.17g}) * y)",
            "onselected": False,
        },
    )
    meshset.apply_filter(
        "meshing_isotropic_explicit_remeshing",
        {
            "Iterations": remesh_iterations,
            "Adaptive": False,
            "SelectedOnly": False,
            "TargetLen": target_edge_length,
            "FeatureDeg": 30.0,
            "CheckSurfDist": False,
            "MaxSurfDist": target_edge_length,
            "ReferenceMesh": meshset.current_mesh(),
            "SplitFlag": True,
            "CollapseFlag": True,
            "SwapFlag": True,
            "SmoothFlag": True,
            "ReprojectFlag": True,
        },
    )

    return meshset


def main(argv: list[str] | None = None) -> Path | None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="", help="optional output mesh path, e.g. wavy_box.ply")
    parser.add_argument("--side", type=float, default=1.0, help="cube side length")
    parser.add_argument("--midpoint-iterations", type=int, default=4, help="uniform midpoint refinement steps")
    parser.add_argument("--remesh-iterations", type=int, default=8, help="isotropic remeshing iterations")
    parser.add_argument(
        "--target-edge-fraction",
        type=float,
        default=1.0 / 24.0,
        help="target remeshing edge length as a fraction of the cube side",
    )
    args = parser.parse_args(argv)

    meshset = build_wavy_box(
        side=args.side,
        midpoint_iterations=args.midpoint_iterations,
        remesh_iterations=args.remesh_iterations,
        target_edge_fraction=args.target_edge_fraction,
    )

    print(f"mesh_count={meshset.mesh_count()}")
    print(f"current_mesh={meshset.current_mesh()}")

    if not args.output:
        return None

    output = Path(args.output)
    meshset.save_current_mesh(str(output))
    print(output)
    return output


if __name__ == "__main__":
    main()
