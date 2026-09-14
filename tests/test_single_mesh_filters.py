from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


pytestmark = pytest.mark.filters


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_MESH = ROOT / "external/meshlab2/tests/data/simple.off"

FILTER_RUNNER = """
import sys
import pymeshlab2

meshset = pymeshlab2.MeshSet()
meshset.load_new_mesh(sys.argv[2])
filter_info = next(item for item in meshset.list_filters() if item.id == sys.argv[1])
if not filter_info.applicable:
    print("SKIP:" + filter_info.applicability_error)
    raise SystemExit(77)
meshset.apply_filter(filter_info.id)
"""


def _single_mesh_filter_ids() -> set[str]:
    ids: set[str] = set()
    for descriptor in (ROOT / "external/meshlab2/plugins").glob("*/filters.json"):
        data = json.loads(descriptor.read_text())
        for item in data.get("filters", []):
            if item.get("inputDomain") == "SingleMesh":
                ids.add(item["id"])
    return ids


def _exposed_single_mesh_filter_ids() -> list[str]:
    pymeshlab2 = pytest.importorskip("pymeshlab2")
    single_mesh_ids = _single_mesh_filter_ids()
    return sorted(f.id for f in pymeshlab2.MeshSet().list_filters() if f.id in single_mesh_ids)


@pytest.mark.parametrize("filter_id", _exposed_single_mesh_filter_ids())
def test_exposed_single_mesh_filters_run_with_defaults(filter_id: str):
    if not SAMPLE_MESH.exists():
        pytest.skip("MeshLab2 sample mesh not found")

    try:
        result = subprocess.run(
            [sys.executable, "-c", FILTER_RUNNER, filter_id, str(SAMPLE_MESH)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        pytest.fail("filter did not finish within 60 seconds")

    if result.returncode == 77:
        pytest.skip(result.stdout.removeprefix("SKIP:").strip())
    assert result.returncode == 0, result.stderr or result.stdout
