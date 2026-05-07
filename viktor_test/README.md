# VIKTOR Pile Cap Test

This folder is a separate VIKTOR app scaffold for a parametric four-pile pile
cap.

The app does two things:

- shows the pile cap and four piles in a VIKTOR `GeometryView`
- sends the same parameters to Allplan through a generic worker action

It does not retrieve results from Allplan. The worker only starts Allplan and
asks it to create the geometry.

## Local VIKTOR Run

From this folder:

```powershell
viktor-cli start
```

Open the local app URL shown by VIKTOR.

## Worker Config

Copy this example into the generic worker `config.yaml`:

```yaml
executables:
  allplan_pile_cap:
    path: 'C:\Program Files\Allplan\Allplan 2026\Prg\Python\python.exe'
    arguments:
      - 'run_allplan_model.py'
maxParallelProcesses: 1
```

Restart the generic worker after changing `config.yaml`.

## Allplan Flow

When the `Create geometry in Allplan` button is clicked:

1. VIKTOR sends `inputs.json`, `run_allplan_model.py`, `PileCapWorker.pyp`, and
   `PileCapWorker.py` to the generic worker.
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

## Current Model

- one rectangular pile cap
- four cylindrical piles
- parametric dimensions and pile spacing
- no rebar yet
- no returned output file
