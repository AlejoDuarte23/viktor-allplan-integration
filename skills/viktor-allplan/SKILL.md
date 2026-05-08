---
name: viktor-allplan
description: Build or modify VIKTOR apps that preview parametric geometry and launch Allplan PythonParts through a Windows Python worker. Use when creating VIKTOR + Allplan integration scaffolds, PythonAnalysis worker flows, PythonPart .pyp/.py files, or Allplan command-line launch scripts.
---

# VIKTOR + Allplan

Use this skill to create a simple VIKTOR-to-Allplan flow:

1. Build parametric inputs in VIKTOR.
2. Preview the model with `GeometryView`.
3. Send the same parameters to a Windows Python worker with `PythonAnalysis`.
4. Send a template Allplan project ZIP to the worker.
5. Install the template project into Allplan's real project folder.
6. Copy a PythonPart into Allplan user folders.
7. Start Allplan directly from the Python launcher.
8. Open the project, load drawing file slot 1, create geometry, and write a done marker.
9. When the marker exists, return `result.json` and zip the generated Allplan project back to VIKTOR.

Keep the first version small: geometry first, then reinforcement or exports later.
Prefer one obvious worker path over configurable fallbacks. Do not add environment
overrides, preflight file checks, helper scripts, or adapter
objects unless the user asks for them or the app actually needs a second runtime
path.

## Folder Template

```text
.
├── app/
│   ├── __init__.py
│   ├── app.py
│   └── worker/
│       ├── run_allplan_model.py
│       ├── PileCapWorker.pyp
│       ├── PileCapWorker.py
│       └── viktor-template.prj.zip
├── requirements.txt
├── manual_test_allplan_workflow.py
└── viktor.config.toml
```

## VIKTOR Pattern

Use `viktor.external.python.PythonAnalysis`, not `GenericAnalysis`, when the app
is configured with the Python worker.

```python
from pathlib import Path
import json
import viktor as vkt
from viktor.external.python import PythonAnalysis

WORKER_DIR = Path(__file__).parent / "worker"


class Controller(vkt.Controller):
    @staticmethod
    def pile_centers(pile_spacing_x, pile_spacing_y):
        half_x = pile_spacing_x / 2.0
        half_y = pile_spacing_y / 2.0

        return [
            {"id": "P1", "x": -half_x, "y": -half_y},
            {"id": "P2", "x": half_x, "y": -half_y},
            {"id": "P3", "x": -half_x, "y": half_y},
            {"id": "P4", "x": half_x, "y": half_y},
        ]

    @vkt.GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def geometry_view(self, params, **kwargs):
        # Build a lightweight VIKTOR geometry preview directly from params.
        return vkt.GeometryResult(geometry=[])

    def create_in_allplan(self, params, **kwargs):
        data = {
            "cap_length": params.geometry.cap_length,
            "pile_centers": self.pile_centers(params.geometry.pile_spacing_x, params.geometry.pile_spacing_y),
        }

        analysis = PythonAnalysis(
            script=vkt.File.from_path(WORKER_DIR / "run_allplan_model.py"),
            files=[
                ("inputs.json", vkt.File.from_data(json.dumps(data, indent=2))),
                ("template_project.zip", vkt.File.from_path(WORKER_DIR / "viktor-template.prj.zip")),
                ("PileCapWorker.pyp", vkt.File.from_path(WORKER_DIR / "PileCapWorker.pyp")),
                ("PileCapWorker.py", vkt.File.from_path(WORKER_DIR / "PileCapWorker.py")),
            ],
            output_filenames=["result_project.zip", "result.json", "worker_log.txt"],
        )
        analysis.execute(timeout=900)
        analysis.get_output_file("result_project.zip")
        analysis.get_output_file("result.json")
        analysis.get_output_file("worker_log.txt")
        vkt.UserMessage.success("Allplan project generated.")
```

Use this config:

```toml
app_type = "simple"
python_version = "3.12"
worker_integrations = [
    "python"
]
```

Expose the controller from `app/__init__.py`:

```python
from .app import Controller
```

Use this requirement:

```text
viktor>=14.17.0
```

## Local Workflow Test

Add `manual_test_allplan_workflow.py` at the repository root to test the worker
outside VIKTOR. It is a runnable manual test, not pytest. It should use
`app/worker` directly, write `inputs.json`, copy `viktor-template.prj.zip` as
`template_project.zip`, run `run_allplan_model.py`, and leave these outputs in
`app/worker`:

```text
local_workflow_log.txt
worker_log.txt
result.json
result_project.zip
```

Run it on the Windows machine with Allplan installed:

```powershell
python manual_test_allplan_workflow.py
```

## Worker Pattern

The Python worker script should:

1. Receive `template_project.zip`, `inputs.json`, `.pyp`, and `.py`.
2. Extract the template ZIP into Allplan's real project folder.
3. Copy `.pyp`, `.py`, and `inputs.json` into Allplan user folders.
4. Start Allplan directly with `subprocess.Popen`.
5. Wait for `worker_done.txt` next to the copied PythonPart script.
6. Copy `result.json` and `worker_log.txt` back to the worker folder and zip the generated project folder as `result_project.zip`.
7. Leave Allplan open for inspection.

Default Allplan paths:

```text
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\ViktorWorker
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\ViktorWorker
C:\Data\Allplan\Allplan 2026\Prj\viktor-template.prj
```

## Launcher Command

Do not add a separate `run_allplan_model.cmd` file. Keep the command in
`run_allplan_model.py`. Avoid `cmd.exe /c start`; it adds Windows shell parsing
and can misread quoted paths.

```python
ALLPLAN_EXE = Path(r"C:\Program Files\Allplan\Allplan 2026\Prg\Allplan_2026.exe")
ALLPLAN_PROJECTS_DIR = Path(r"C:\Data\Allplan\Allplan 2026\Prj")
PROJECT_NAME = "viktor-template"
PROJECT_DIR = ALLPLAN_PROJECTS_DIR / f"{PROJECT_NAME}.prj"

process = subprocess.Popen(
    [
        str(ALLPLAN_EXE),
        "-o",
        f"@{pyp_target}",
    ],
    cwd=str(workdir),
)

while not done_marker.exists():
    if process.poll() is not None:
        raise RuntimeError("Allplan closed before the worker finished.")
    time.sleep(1)

shutil.make_archive(
    base_name=str(output_zip.with_suffix("")),
    format="zip",
    root_dir=str(PROJECT_DIR),
)
```

The PythonPart writes `result.json` after `CreateElements(...)` succeeds, then
writes the marker. The marker is the worker finish signal, so the worker does
not need to wait for Allplan to close.

## PythonPart Pattern

`.pyp` points to the script in `PythonPartsScripts`:

```xml
<Element>
    <Script>
        <Name>ViktorWorker\PileCapWorker.py</Name>
        <Title>VIKTOR Pile Cap Worker</Title>
        <Version>1.0</Version>
    </Script>
</Element>
```

`.py` should implement:

```python
def check_allplan_version(build_ele, version):
    return True


def create_element(build_ele, doc):
    # Read inputs, open project viktor-template, load drawing slot 1, create
    # Allplan geometry, then write result.json and worker_done.txt.
    ...
```
