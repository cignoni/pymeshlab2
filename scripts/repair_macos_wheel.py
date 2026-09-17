#!/usr/bin/env python3

import base64
import csv
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile


QT_FRAMEWORK_RE = re.compile(r"(?:^|/)(Qt[^/]+\.framework)/(Versions/[^/]+/[^/]+)$")


def command(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        args,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout if capture else ""


def dependencies(binary: Path) -> list[str]:
    output = command("otool", "-L", str(binary), capture=True)
    return [line.strip().split(" (", 1)[0] for line in output.splitlines()[1:]]


def add_rpath(binary: Path, rpath: str) -> None:
    output = command("otool", "-l", str(binary), capture=True)
    if f"path {rpath} " not in output:
        command("install_name_tool", "-add_rpath", rpath, str(binary))


def framework_source(dependency: str, qt_root: Path) -> tuple[Path, str, str]:
    match = QT_FRAMEWORK_RE.search(dependency)
    if match is None:
        raise ValueError(f"Not a Qt framework dependency: {dependency}")

    framework, binary_suffix = match.groups()
    if dependency.startswith("/"):
        source = Path(dependency[: dependency.index(framework) + len(framework)])
    else:
        source = qt_root / "lib" / framework
    return source.resolve(), framework, binary_suffix


def copy_framework(source: Path, destination: Path, binary_name: str) -> None:
    shutil.copytree(source, destination)

    # Wheels do not preserve framework symlinks consistently. copytree expands
    # them, so discard the duplicate binary trees while retaining root Resources.
    top_level_binary = destination / binary_name
    if top_level_binary.exists():
        top_level_binary.unlink()
    current_version = destination / "Versions" / "Current"
    if current_version.exists():
        shutil.rmtree(current_version)


def bundle_qt_frameworks(package_dir: Path, qt_root: Path) -> None:
    extension = next(package_dir.glob("_meshlab*.so"))
    frameworks_dir = package_dir / "Frameworks"
    frameworks_dir.mkdir()

    queue: list[tuple[Path, str]] = [(extension, "@loader_path/Frameworks")]
    visited: set[Path] = set()
    while queue:
        binary, rpath = queue.pop()
        if binary in visited:
            continue
        visited.add(binary)

        for dependency in dependencies(binary):
            match = QT_FRAMEWORK_RE.search(dependency)
            if match is None:
                continue

            source, framework, binary_suffix = framework_source(dependency, qt_root)
            destination = frameworks_dir / framework
            if not destination.exists():
                copy_framework(source, destination, Path(binary_suffix).name)

            bundled_binary = destination / binary_suffix
            bundled_name = f"@rpath/{framework}/{binary_suffix}"
            if dependency != bundled_name:
                command(
                    "install_name_tool", "-change", dependency, bundled_name, str(binary)
                )
            command("install_name_tool", "-id", bundled_name, str(bundled_binary))
            queue.append((bundled_binary, "@loader_path/../../.."))

        add_rpath(binary, rpath)

    for binary in reversed(list(visited)):
        command("codesign", "--force", "--sign", "-", str(binary))


def extract_wheel(wheel: Path, destination: Path) -> Path:
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(destination)
        for info in archive.infolist():
            mode = info.external_attr >> 16
            if mode:
                os.chmod(destination / info.filename, mode)
    return destination


def update_record(root: Path) -> None:
    record = next(root.glob("*.dist-info/RECORD"))
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if path == record:
            rows.append((relative, "", ""))
            continue
        data = path.read_bytes()
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
        rows.append((relative, f"sha256={digest.decode()}", str(len(data))))

    with record.open("w", encoding="utf-8", newline="") as output:
        csv.writer(output).writerows(rows)


def pack_wheel(root: Path, output: Path) -> None:
    update_record(root)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            archive.write(path, path.relative_to(root).as_posix())


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: repair_macos_wheel.py WHEEL DESTINATION")

    wheel = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2]).resolve()
    qt_root = Path(os.environ["QT_ROOT_DIR"]).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temporary:
        root = extract_wheel(wheel, Path(temporary) / "wheel")
        bundle_qt_frameworks(root / "pymeshlab2", qt_root)
        intermediate = Path(temporary) / wheel.name
        pack_wheel(root, intermediate)
        command(
            "delocate-wheel",
            "--require-archs",
            "arm64",
            "--no-sanitize-rpaths",
            "--wheel-dir",
            str(destination),
            str(intermediate),
        )


if __name__ == "__main__":
    main()
