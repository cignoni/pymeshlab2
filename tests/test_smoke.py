from pathlib import Path

import pytest


@pytest.mark.smoke
def test_meshset_import_and_filter_listing():
    mod = pytest.importorskip("pymeshlab2")

    ms = mod.MeshSet()
    filters = ms.list_filters()

    assert len(filters) > 0
    assert any(f.id == "mesh_info" for f in filters)


@pytest.mark.smoke
def test_basic_filter_on_sample_mesh():
    mod = pytest.importorskip("pymeshlab2")

    mesh_path = Path("external/QMeshLab/tests/data/simple.off")
    if not mesh_path.exists():
        pytest.skip("QMeshLab sample mesh not found")

    ms = mod.MeshSet()
    ms.load_new_mesh(str(mesh_path))
    result = ms.apply_filter("mesh_info", {"precision": 2})

    assert result.success is True
    assert result.document_modified is False
    assert len(result.info_messages) > 0
