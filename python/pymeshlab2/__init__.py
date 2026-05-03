try:
	from ._pymeshlab2 import FilterInfo, FilterRunResult, MeshSet
except ModuleNotFoundError:
	# Local development fallback: import extension directly from build directory.
	from _pymeshlab2 import FilterInfo, FilterRunResult, MeshSet

__all__ = ["MeshSet", "FilterInfo", "FilterRunResult"]
