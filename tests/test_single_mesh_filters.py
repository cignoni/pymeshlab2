from __future__ import annotations

import json
from pathlib import Path

import pytest


pytestmark = pytest.mark.filters


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MESH = ROOT / "external/QMeshLab/tests/data/simple.off"


def _single_mesh_filter_ids() -> set[str]:
    ids: set[str] = set()
    for descriptor in (ROOT / "external/QMeshLab/plugins").glob("*/filters.json"):
        data = json.loads(descriptor.read_text())
        for item in data.get("filters", []):
            if item.get("inputDomain") == "SingleMesh":
                ids.add(item["id"])
    return ids


def test_exposed_single_mesh_filters_run_with_defaults():
    pymeshlab2 = pytest.importorskip("pymeshlab2")
    if not SAMPLE_MESH.exists():
        pytest.skip("QMeshLab sample mesh not found")

    single_mesh_ids = _single_mesh_filter_ids()
    exposed = [f for f in pymeshlab2.MeshSet().list_filters() if f.id in single_mesh_ids]

    assert exposed

    failures = []
    for filter_info in exposed:
        meshset = pymeshlab2.MeshSet()
        meshset.load_new_mesh(str(SAMPLE_MESH))
        try:
            result = meshset.apply_filter(filter_info.id)
        except Exception as exc:  # noqa: BLE001 - report all filter failures together.
            failures.append(f"{filter_info.id}: {exc}")
        else:
            if not result.success:
                failures.append(f"{filter_info.id}: returned success=False")

    assert not failures, "\n".join(failures)
