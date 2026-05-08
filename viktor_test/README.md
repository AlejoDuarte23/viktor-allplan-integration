# VIKTOR Pile Cap Test

This folder is a separate VIKTOR app scaffold for a parametric four-pile pile
cap.

The app does two things:

- shows the pile cap and four piles in a VIKTOR `GeometryView`
- sends the same parameters to Allplan through a Python worker action

It does not retrieve results from Allplan. The worker only starts Allplan and
waits for a local completion marker from the PythonPart.

## Local VIKTOR Run

From this folder:

```powershell
viktor-cli start
```

Open the local app URL shown by VIKTOR.

## Worker Setup

This app uses the VIKTOR Python worker through `viktor.external.python.PythonAnalysis`.

The app config already declares the worker integration:

```toml
worker_integrations = [
    "python"
]
```

No executable key configuration is used.

## Allplan Flow

When the `Create geometry in Allplan` button is clicked:

1. VIKTOR sends `inputs.json`, `run_allplan_model.py`, `PileCapWorker.pyp`, and
   `PileCapWorker.py` to the Python worker.
2. The worker copies the PythonPart files and inputs to:

```text
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\ViktorWorker
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\ViktorWorker
```

3. The worker starts:

```powershell
& "C:\Program Files\Allplan\Allplan 2026\Prg\Allplan_2026.exe" -o "@$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\ViktorWorker\PileCapWorker.pyp"
```

4. Allplan loads the PythonPart and creates one pile cap with four piles.
5. The PythonPart writes a local done marker, and the Python worker returns.

## Current Model

- one rectangular pile cap
- four cylindrical piles
- parametric dimensions and pile spacing
- no rebar yet
- no returned output file
- local completion marker only, not returned to VIKTOR
