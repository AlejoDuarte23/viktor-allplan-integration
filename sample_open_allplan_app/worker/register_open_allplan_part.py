import json
import shutil
import time
from pathlib import Path


ALLPLAN_LOCAL = Path.home() / "Documents" / "Nemetschek" / "Allplan" / "2026" / "Usr" / "Local"


def log(log_path: Path, message: str):
    with log_path.open("a", encoding="utf-8") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def main():
    workdir = Path.cwd()
    log_path = workdir / "worker_log.txt"
    result_path = workdir / "registration_result.json"

    if log_path.exists():
        log_path.unlink()

    if result_path.exists():
        result_path.unlink()

    python_parts_dir = ALLPLAN_LOCAL / "PythonParts" / "ViktorOpenSession"
    python_scripts_dir = ALLPLAN_LOCAL / "PythonPartsScripts" / "ViktorOpenSession"
    python_parts_dir.mkdir(parents=True, exist_ok=True)
    python_scripts_dir.mkdir(parents=True, exist_ok=True)

    pyp_target = python_parts_dir / "OpenSessionPileCap.pyp"
    py_target = python_scripts_dir / "OpenSessionPileCap.py"
    inputs_target = python_scripts_dir / "inputs.json"
    execution_log_target = python_scripts_dir / "execution_log.txt"
    execution_result_target = python_scripts_dir / "execution_result.json"
    execution_done_target = python_scripts_dir / "execution_done.txt"
    execution_error_target = python_scripts_dir / "execution_error.txt"

    for stale_output in (
        execution_log_target,
        execution_result_target,
        execution_done_target,
        execution_error_target,
    ):
        if stale_output.exists():
            stale_output.unlink()

    shutil.copy2(workdir / "OpenSessionPileCap.pyp", pyp_target)
    shutil.copy2(workdir / "OpenSessionPileCap.py", py_target)
    shutil.copy2(workdir / "inputs.json", inputs_target)

    data = json.loads(inputs_target.read_text(encoding="utf-8"))

    log(log_path, f"Registered PythonPart at {pyp_target}.")
    log(log_path, f"Registered script at {py_target}.")
    log(log_path, f"Wrote inputs at {inputs_target}.")
    log(log_path, "This sample does not start or close Allplan.")
    log(log_path, "Assumption: Allplan is already open with an empty project and active drawing file.")
    log(log_path, "Next step: execute 'Open Session Pile Cap' from the PythonParts library in the open Allplan session.")

    result = {
        "run_id": data["run_id"],
        "pythonpart_name": "Open Session Pile Cap",
        "pythonpart_path": str(pyp_target),
        "script_path": str(py_target),
        "inputs_path": str(inputs_target),
        "execution_log_path": str(execution_log_target),
        "execution_result_path": str(execution_result_target),
        "execution_done_path": str(execution_done_target),
        "execution_error_path": str(execution_error_target),
        "assumptions": [
            "Allplan is already open.",
            "An empty project is already open.",
            "An active drawing file is selected.",
            "The user will execute the PythonPart manually from the open Allplan session.",
        ],
    }
    result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
