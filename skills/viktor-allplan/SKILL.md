---
name: viktor-allplan
description: Build or modify VIKTOR apps that preview parametric geometry and launch Allplan PythonParts through a Windows Python worker. Use when creating VIKTOR + Allplan integration scaffolds, PythonAnalysis worker flows, PythonPart .pyp/.py files, or Allplan command-line launch scripts.
---

# VIKTOR + Allplan

Use this skill to create a simple VIKTOR-to-Allplan flow:

1. Build parametric inputs in VIKTOR.
2. Preview the model with `GeometryView`.
3. Send the same parameters to a Windows Python worker with `PythonAnalysis`.
4. Copy a PythonPart into Allplan user folders.
5. Start Allplan through `cmd.exe` with a simple `start /wait` command from the Python launcher.

Keep the first version small: geometry first, then reinforcement or exports later.
Prefer one obvious worker path over configurable fallbacks. Do not add environment
overrides, context indirection, preflight file checks, helper scripts, or adapter
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
│       └── PileCapWorker.py
├── requirements.txt
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
                ("PileCapWorker.pyp", vkt.File.from_path(WORKER_DIR / "PileCapWorker.pyp")),
                ("PileCapWorker.py", vkt.File.from_path(WORKER_DIR / "PileCapWorker.py")),
            ],
        )
        analysis.execute(timeout=900)
        vkt.UserMessage.success("Allplan command finished.")
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

## Worker Pattern

The Python worker script should:

1. Read `inputs.json` from the worker directory.
2. Copy `.pyp`, `.py`, and `inputs.json` into Allplan user folders.
3. Call `cmd.exe /c` with the simple blocking Allplan command.

Default Allplan paths:

```text
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\ViktorWorker
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\ViktorWorker
```

## Launcher Command

Do not add a separate `run_allplan_model.cmd` file. Keep the command in
`run_allplan_model.py`.

```python
ALLPLAN_EXE = Path(r"C:\Program Files\Allplan\Allplan 2026\Prg\Allplan_2026.exe")

subprocess.run(
    [
        "cmd.exe",
        "/c",
        f'start "" /wait "{ALLPLAN_EXE}" -o "@{pyp_target}" & exit /b %ERRORLEVEL%',
    ],
    cwd=str(workdir),
    check=True,
)
```

Important tradeoff: `start /wait` waits for the Allplan process, not necessarily
the PythonPart function. If Allplan stays open, the worker stays blocked.

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
    # Read inputs.json next to this file, create Allplan geometry, and return
    # CreateElementResult. Keep simple worker scripts in this entry point unless
    # the geometry becomes large enough to justify helpers.
    ...
```