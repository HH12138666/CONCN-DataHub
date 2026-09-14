"""Clipping subprocess entry point; released archives always use real source data."""

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import zipfile
from ..config import ROOT
from ..package_content import EXCLUDED_PACKAGE_FILES, public_metadata

sys.path.insert(0, str(ROOT))
from concnshare.config import ClipConfig
from concnshare.run_two import run_basin_clip


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build(snapshot, workdir):
    cfg = ClipConfig()
    files = snapshot["files"]
    sources = [f for f in files if f["file_kind"] == "source"]
    # The present scientific pipeline requires its complete set of five named inputs.
    if {Path(f["storage_key"]).name for f in sources} != set(cfg.pfb_inputs):
        raise ValueError("Source manifest does not match the full clipping pipeline")
    for source in sources:
        path = cfg.input_pfb_dir / Path(source["storage_key"]).name
        if (
            not source.get("source_sha256")
            or file_hash(path) != source["source_sha256"]
        ):
            raise ValueError("Source digest mismatch")
    grid = snapshot["grid"]
    for asset in grid.get("source_assets", []):
        # Only the selected basin's level is used by this clipping task.
        if Path(asset["name"]).stem != f"PFBAS{snapshot['pfbas_level']}":
            continue
        folder = cfg.shp_dir if asset["kind"] == "shp" else cfg.tif_dir
        if file_hash(folder / Path(asset["name"]).name) != asset["sha256"]:
            raise ValueError("Boundary/template digest mismatch")
    for name, expected in grid.get("pipeline_sha256", {}).items():
        if file_hash(ROOT / "concnshare" / Path(name).name) != expected:
            raise ValueError("Clipping pipeline differs from published version")
    if grid.get("pfmask_sha256") and file_hash(cfg.pfmask_cmd) != grid["pfmask_sha256"]:
        raise ValueError("Domain converter differs from published version")
    values = {
        key: grid[key]
        for key in (
            "dx",
            "dy",
            "dz",
            "expand",
            "z_top",
            "z_bottom",
            "bottom_patch_label",
            "side_patch_label",
        )
        if key in grid
    }
    cfg = replace(cfg, **values, data_version=snapshot["version_code"])
    folder = run_basin_clip(snapshot["basin_code"], workdir / "outputs", config=cfg)
    metadata_path = folder / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = public_metadata(metadata)
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for file in folder.iterdir():
        if file.is_file() and file.name.lower() in EXCLUDED_PACKAGE_FILES:
            file.unlink()
    manifest = []
    for file in sorted(folder.iterdir()):
        if file.is_file():
            manifest.append(
                {
                    "name": file.name,
                    "bytes": file.stat().st_size,
                    "sha256": file_hash(file),
                }
            )
    expected = {
        f["output_name_template"].replace("{basin_code}", snapshot["basin_code"])
        for f in files if f["output_name_template"].lower() not in EXCLUDED_PACKAGE_FILES
    }
    if not expected.issubset({p.name for p in folder.iterdir()}):
        raise ValueError("Incomplete output package")
    archive = workdir / "result.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for file in sorted(folder.iterdir()):
            if file.is_file():
                z.write(file, arcname=f"{snapshot['basin_code']}/{file.name}")
    result = {
        "byte_size": archive.stat().st_size,
        "sha256": file_hash(archive),
        "files": manifest,
    }
    (workdir / "result.json").write_text(json.dumps(result), encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("snapshot")
    args = p.parse_args()
    path = Path(args.snapshot).resolve()
    build(json.loads(path.read_text(encoding="utf-8")), path.parent)
