# viktor-allplan-integration

## Current VIKTOR + Allplan Experiment

The VIKTOR app runs a Python worker that starts Allplan, creates the pile cap
geometry, and closes Allplan.

Expected flow:

1. `PythonAnalysis` sends `inputs.json`, `PileCapWorker.pyp`, and
   `PileCapWorker.py` to the worker.
2. `run_allplan_model.py` copies the PythonPart files into the Allplan local
   user folders.
3. Allplan runs the PythonPart from the command line.
4. The PythonPart creates the geometry directly in the active drawing file.
5. The PythonPart calls `ProjectService.CloseAllplan()`.

Run from the repo root:

```powershell
viktor-cli start
```
