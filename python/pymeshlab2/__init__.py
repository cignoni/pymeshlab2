import os
from pathlib import Path


_quadwild_root = Path(__file__).resolve().parent / "quadwild-bimdf"
if _quadwild_root.is_dir():
	os.environ.setdefault("MESHLAB2_QUADWILD_ROOT", str(_quadwild_root))

try:
	from ._meshlab import FilterInfo, FilterRunResult, Mesh, MeshSet
except ModuleNotFoundError:
	# Local development fallback: import extension directly from build directory.
	from _meshlab import FilterInfo, FilterRunResult, Mesh, MeshSet

__all__ = ["Mesh", "MeshSet", "FilterInfo", "FilterRunResult"]
