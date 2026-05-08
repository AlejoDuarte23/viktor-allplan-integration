from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ALLPLAN_BUILD_TIMEOUT_SECONDS = 840


def _allplan_exe() -> Path:
    return Path(
        os.environ.get(
            "ALLPLAN_EXE",
            r"C:\Program Files\Allplan\Allplan 2026\Prg\Allplan_2026.exe",
        )
    )


def _allplan_local() -> Path:
    return Path(
        os.environ.get(
            "ALLPLAN_LOCAL",
            Path.home() / "Documents" / "Nemetschek" / "Allplan" / "2026" / "Usr" / "Local",
        )
    )


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    workdir = Path.cwd()
    inputs_path = workdir / "inputs.json"
    pyp_source = workdir / "PileCapWorker.pyp"
    py_source = workdir / "PileCapWorker.py"

    allplan_exe = _allplan_exe()
    allplan_local = _allplan_local()

    if not allplan_exe.is_file():
        raise FileNotFoundError(f"Allplan executable not found: {allplan_exe}")

    for path in [inputs_path, pyp_source, py_source]:
        if not path.is_file():
            raise FileNotFoundError(f"Missing worker file: {path}")

    python_parts_dir = allplan_local / "PythonParts" / "ViktorWorker"
    python_scripts_dir = allplan_local / "PythonPartsScripts" / "ViktorWorker"
    python_parts_dir.mkdir(parents=True, exist_ok=True)
    python_scripts_dir.mkdir(parents=True, exist_ok=True)

    pyp_target = python_parts_dir / "PileCapWorker.pyp"
    py_target = python_scripts_dir / "PileCapWorker.py"
    inputs_target = python_scripts_dir / "inputs.json"
    context_path = python_scripts_dir / "worker_context.json"
    done_path = python_scripts_dir / f"pile_cap_done_{int(time.time())}_{os.getpid()}.json"

    shutil.copy2(pyp_source, pyp_target)
    shutil.copy2(py_source, py_target)
    shutil.copy2(inputs_path, inputs_target)

    if done_path.exists():
        done_path.unlink()

    _write_json(
        context_path,
        {
            "inputs_path": str(inputs_target),
            "done_path": str(done_path),
        },
    )

    env = os.environ.copy()
    env["ALLPLAN_WORKER_CONTEXT"] = str(context_path)

    process = subprocess.Popen(
        [str(allplan_exe), "-o", f"@{pyp_target}"],
        cwd=str(workdir),
        env=env,
    )

    deadline = time.time() + ALLPLAN_BUILD_TIMEOUT_SECONDS

    while time.time() < deadline:
        if done_path.is_file():
            done_data = json.loads(done_path.read_text(encoding="utf-8"))
            if done_data.get("status") != "ok":
                raise RuntimeError(done_data.get("message", "Allplan PythonPart failed."))
            return 0

        if process.poll() not in (None, 0):
            raise RuntimeError(f"Allplan failed to start. Return code: {process.returncode}")

        time.sleep(1)

    raise TimeoutError("Allplan did not finish creating the pile cap before timeout.")


if __name__ == "__main__":
    sys.exit(main())
