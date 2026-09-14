try:
	from ._meshlab import FilterInfo, FilterRunResult, Mesh, MeshSet
except ModuleNotFoundError:
	# Local development fallback: import extension directly from build directory.
	from _meshlab import FilterInfo, FilterRunResult, Mesh, MeshSet

__all__ = ["Mesh", "MeshSet", "FilterInfo", "FilterRunResult"]
