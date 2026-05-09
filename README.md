# viktor-allplan-integration

## Current VIKTOR + Allplan Experiment

The main VIKTOR app runs a Python worker that installs the template project,
starts Allplan, creates the pile cap geometry, and leaves Allplan open for
inspection.

Expected flow:

1. `PythonAnalysis` sends `inputs.json`, `PileCapWorker.pyp`, and
   `PileCapWorker.py` to the worker.
2. `run_allplan_model.py` copies the PythonPart files into the Allplan local
   user folders.
3. Allplan runs the PythonPart from the command line.
4. The PythonPart creates the geometry directly in the active drawing file.
5. The PythonPart writes `result.json`, `worker_log.txt`, and `worker_done.txt`.
6. The worker returns `result_project.zip` to VIKTOR.

Run from the repo root:

```powershell
viktor-cli start
```

## Open Session Sample

The `sample_open_allplan_app` folder contains the upcoming Windows test version
that does not install a project ZIP and does not start or close Allplan. It only
registers the PythonPart and assumes Allplan is already open with an empty
project and active drawing file.

Run it from the sample folder:

```powershell
cd sample_open_allplan_app
viktor-cli start
```
