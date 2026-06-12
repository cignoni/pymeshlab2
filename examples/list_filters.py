"""List the filters currently exposed by pymeshlab2."""

from __future__ import annotations

import argparse

import pymeshlab2


def main(argv: list[str] | None = None) -> list[pymeshlab2.FilterInfo]:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only-applicable",
        action="store_true",
        help="show only filters that can run on the current empty MeshSet",
    )
    args = parser.parse_args(argv)

    meshset = pymeshlab2.MeshSet()
    filters = meshset.list_filters()
    if args.only_applicable:
        filters = [item for item in filters if item.applicable]

    for item in filters:
        print(f"{item.key}\t{item.python_name}\t{item.name}")

    return filters


if __name__ == "__main__":
    main()
