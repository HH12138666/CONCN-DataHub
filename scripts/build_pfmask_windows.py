"""Build the official ParFlow 3.13 mask converter with the PyPI Zig compiler.

Run with the project venv. Source stays in ignored .local/tools; no global install.
The unused Tcl display function is omitted; numerical converter code is unchanged.
"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "77316043227b95215744e58fe9005d35145432ab"


def main():
    source = ROOT / ".local/tools/parflow-source"
    if not source.exists():
        subprocess.run(["git", "clone", "--depth", "1", "--branch", "v3.13.0",
                        "https://github.com/parflow/parflow.git", str(source)], check=True)
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    if actual != COMMIT:
        raise RuntimeError("Unexpected ParFlow source revision")
    build = ROOT / ".local/tools/pfmask-build"
    build.mkdir(parents=True, exist_ok=True)
    upstream = source / "pftools"
    # The standalone converter does not use Tcl. Omit only its unused display API.
    code = (upstream / "databox.c").read_text()
    start = code.index("void            GetDataboxGrid(")
    end = code.index("\n}", start) + 2
    (build / "databox.c").write_text(code[:start] + code[end:])
    (build / "tcl.h").write_text("typedef struct Tcl_Interp Tcl_Interp;\n")
    (build / "parflow_config.h").write_text("/* Standalone, little-endian; optional I/O libraries disabled. */\n")
    objects = []
    for name in ("databox", "readdatabox", "tools_io"):
        path = build / "databox.c" if name == "databox" else upstream / (name + ".c")
        obj = build / (name + ".o")
        subprocess.run([sys.executable, "-m", "ziglang", "cc", "-O2", "-I", str(build),
                        "-I", str(upstream), "-c", str(path), "-o", str(obj)], check=True)
        objects.append(str(obj))
    output = build / "pfmask-to-pfsol.exe"
    subprocess.run([sys.executable, "-m", "ziglang", "c++", "-O2", "-std=c++11",
                    "-I", str(build), "-I", str(upstream / "third_party"),
                    str(upstream / "pfmask-to-pfsol.cpp"), *objects, "-o", str(output)], check=True)
    shutil.copy2(source / "LICENSE.txt", build / "LICENSE.txt")
    print(output)


if __name__ == "__main__":
    main()
