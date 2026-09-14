from pathlib import Path

import pytest


@pytest.mark.smoke
def test_meshset_import_and_filter_listing():
    mod = pytest.importorskip("pymeshlab2")

    ms = mod.MeshSet()
    filters = ms.list_filters()

    assert len(filters) > 0
    mesh_info = next((f for f in filters if f.id == "measure_mesh_summary"), None)

    assert mesh_info is not None
    assert mesh_info.python_name == "measure_mesh_summary"


@pytest.mark.smoke
def test_meshlab2_filter_registry_is_linked():
    mod = pytest.importorskip("pymeshlab2")

    filters = mod.MeshSet().list_filters()
    filter_ids = {item.id for item in filters}
    plugin_ids = {item.plugin_id for item in filters}

    assert len(plugin_ids) >= 20
    assert {
        "create_box",
        "subdivide_by_midpoint",
        "remesh_isotropically_vcglib",
        "normalize_reference_frame",
        "select_all",
        "measure_geometric_properties",
    } <= filter_ids


@pytest.mark.smoke
def test_basic_filter_on_sample_mesh():
    mod = pytest.importorskip("pymeshlab2")

    mesh_path = Path("external/meshlab2/tests/data/simple.off")
    if not mesh_path.exists():
        pytest.skip("MeshLab2 sample mesh not found")

    ms = mod.MeshSet()
    ms.load_new_mesh(str(mesh_path))
    result = ms.apply_filter("measure_mesh_summary", {"precision": 2})

    assert result.success is True
    assert result.document_modified is False
    assert len(result.info_messages) > 0


@pytest.mark.smoke
def test_raster_api_is_available():
    mod = pytest.importorskip("pymeshlab2")

    ms = mod.MeshSet()

    assert ms.raster_number() == 0
    assert ms.current_raster() == -1
