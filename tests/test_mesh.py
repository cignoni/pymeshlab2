from pathlib import Path

import pytest


SAMPLE_MESH = Path("external/QMeshLab/tests/data/simple.off")


def test_current_mesh_exposes_geometry_as_numpy_arrays():
    mod = pytest.importorskip("pymeshlab2")
    if not SAMPLE_MESH.exists():
        pytest.skip("QMeshLab sample mesh not found")

    meshset = mod.MeshSet()
    meshset.load_new_mesh(str(SAMPLE_MESH))
    mesh = meshset.current_mesh()

    assert isinstance(mesh, mod.Mesh)
    assert mesh.id() == meshset.current_mesh_id()
    assert meshset.mesh(mesh.id()).id() == mesh.id()
    assert mesh.vertex_matrix().shape == (mesh.vertex_number(), 3)
    assert mesh.face_matrix().shape == (mesh.face_number(), 3)
    assert mesh.vertex_normal_matrix().shape == (mesh.vertex_number(), 3)
    assert mesh.face_normal_matrix().shape == (mesh.face_number(), 3)
