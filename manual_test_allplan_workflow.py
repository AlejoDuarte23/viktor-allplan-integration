import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).parent
WORKER_DIR = ROOT_DIR / "app" / "worker"
LOCAL_LOG = WORKER_DIR / "local_workflow_log.txt"


def get_pile_centers(pile_spacing_x: float, pile_spacing_y: float) -> list[dict[str, float | str]]:
    half_x = pile_spacing_x / 2.0
    half_y = pile_spacing_y / 2.0

    return [
        {"id": "P1", "x": -half_x, "y": -half_y},
        {"id": "P2", "x": half_x, "y": -half_y},
        {"id": "P3", "x": -half_x, "y": half_y},
        {"id": "P4", "x": half_x, "y": half_y},
    ]


def log(message: str):
    with LOCAL_LOG.open("a", encoding="utf-8") as file:
        file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def main():
    for filename in [
        "inputs.json",
        "template_project.zip",
        "result.json",
        "result_project.zip",
        "worker_log.txt",
        "local_workflow_log.txt",
    ]:
        path = WORKER_DIR / filename
        if path.exists():
            path.unlink()

    worker_input = {
        "cap_length": 4000.0,
        "cap_width": 3000.0,
        "cap_height": 800.0,
        "pile_diameter": 600.0,
        "pile_depth": 3000.0,
        "pile_centers": get_pile_centers(2600.0, 1800.0),
    }

    log("Local workflow started.")
    (WORKER_DIR / "inputs.json").write_text(json.dumps(worker_input, indent=2), encoding="utf-8")
    shutil.copy2(WORKER_DIR / "viktor-template.prj.zip", WORKER_DIR / "template_project.zip")
    log("Wrote inputs.json and template_project.zip.")
    log("Starting run_allplan_model.py.")

    subprocess.run(
        [sys.executable, "run_allplan_model.py"],
        cwd=str(WORKER_DIR),
        check=True,
    )

    log("run_allplan_model.py finished.")
    print(f"Local log: {LOCAL_LOG}")
    print(f"Allplan/PythonPart log: {WORKER_DIR / 'worker_log.txt'}")
    print(f"Result JSON: {WORKER_DIR / 'result.json'}")
    print(f"Result project ZIP: {WORKER_DIR / 'result_project.zip'}")


if __name__ == "__main__":
    main()
