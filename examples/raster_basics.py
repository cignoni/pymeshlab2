"""Show the raster-related MeshSet API on an empty document."""

from __future__ import annotations

import argparse

import pymeshlab2


def main(argv: list[str] | None = None) -> tuple[int, int]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    meshset = pymeshlab2.MeshSet()
    raster_state = (meshset.raster_count(), meshset.current_raster())

    print(f"raster_count={raster_state[0]}")
    print(f"current_raster={raster_state[1]}")

    return raster_state


if __name__ == "__main__":
    main()
