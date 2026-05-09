# Open Allplan Session Sample

This VIKTOR app is the no-project-install test path. It assumes Allplan is
already open on the Windows computer with an empty project and an active drawing
file.

Run from this folder:

```powershell
viktor-cli start
```

Expected flow:

1. Open Allplan manually and keep it running.
2. Open an empty Allplan project and select an active drawing file.
3. In VIKTOR, click `Register PythonPart In Open Allplan`.
4. In Allplan, run `Open Session Pile Cap` from the PythonParts library.
5. Inspect the generated pile cap geometry in the open Allplan session.

The worker only copies these files into the Allplan local user folders:

```text
PythonParts\ViktorOpenSession\OpenSessionPileCap.pyp
PythonPartsScripts\ViktorOpenSession\OpenSessionPileCap.py
PythonPartsScripts\ViktorOpenSession\inputs.json
```

It does not install a project ZIP, start Allplan, close Allplan, or return an
Allplan project ZIP.

After manual execution, the PythonPart writes:

```text
PythonPartsScripts\ViktorOpenSession\execution_log.txt
PythonPartsScripts\ViktorOpenSession\execution_result.json
PythonPartsScripts\ViktorOpenSession\execution_done.txt
```

If execution fails, it writes:

```text
PythonPartsScripts\ViktorOpenSession\execution_error.txt
```
