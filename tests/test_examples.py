from __future__ import annotations

import importlib
from pathlib import Path

import pytest


pytestmark = pytest.mark.examples


def _example(name: str):
    return importlib.import_module(f"examples.{name}")


def test_list_filters_example():
    pymeshlab2 = pytest.importorskip("pymeshlab2")

    filters = _example("list_filters").main([])

    assert filters
    assert all(isinstance(item, pymeshlab2.FilterInfo) for item in filters)
    assert any(item.id == "measure_mesh_summary" for item in filters)


def test_mesh_info_example():
    pymeshlab2 = pytest.importorskip("pymeshlab2")

    result = _example("mesh_info").main([])

    assert isinstance(result, pymeshlab2.FilterRunResult)
    assert result.success is True
    assert result.info_messages


def test_normalize_and_save_example(tmp_path: Path):
    pymeshlab2 = pytest.importorskip("pymeshlab2")
    available = {item.id for item in pymeshlab2.MeshSet().list_filters()}
    if "normalize_reference_frame" not in available:
        pytest.skip("normalize example needs the meshing plugin")
    output = tmp_path / "normalized.ply"

    written = _example("normalize_and_save").main(["--output", str(output)])

    assert written == output
    assert output.exists()
    assert output.stat().st_size > 0


def test_create_noisy_isosurface_example():
    pymeshlab2 = pytest.importorskip("pymeshlab2")

    result = _example("create_noisy_isosurface").main(["--resolution", "8"])

    assert isinstance(result, pymeshlab2.FilterRunResult)
    assert result.success is True
    assert result.new_mesh_indices


def test_raster_basics_example():
    pytest.importorskip("pymeshlab2")

    raster_number, current_raster = _example("raster_basics").main([])

    assert raster_number == 0
    assert current_raster == -1


def test_wavy_box_example_if_filters_are_available(tmp_path: Path):
    pymeshlab2 = pytest.importorskip("pymeshlab2")
    available = {item.id for item in pymeshlab2.MeshSet().list_filters()}
    missing = sorted(
        {
            "create_hexahedron",
            "subdivide_by_midpoint",
            "compute_vertex_coordinates_by_expression",
            "remesh_isotropically_vcglib",
        }
        - available
    )
    if missing:
        pytest.skip("wavy box example needs unavailable filters: " + ", ".join(missing))

    output = tmp_path / "wavy_box.ply"
    written = _example("wavy_box").main([str(output)])

    assert written == output
    assert output.exists()
    assert output.stat().st_size > 0
