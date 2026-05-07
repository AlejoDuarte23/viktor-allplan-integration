# Simple Allplan PythonPart Test

This is the smallest useful test for running Python logic directly in Allplan,
without VIKTOR.

I cannot run this on macOS because Allplan is a Windows desktop application.
Copy these files to a Windows machine with Allplan 2026 installed.

## Files

- `SimpleCube.pyp`: Allplan PythonPart definition.
- `SimpleCube.py`: Python logic that creates one 1000 x 1000 x 1000 mm cube.

## Install In Allplan

Copy:

```text
SimpleCube.pyp
```

to your user PythonParts folder, for example:

```text
C:\ProgramData\Nemetschek\Allplan\2026\Usr\Local\PythonParts\SimpleCube.pyp
```

Copy:

```text
SimpleCube.py
```

to your user PythonPartsScripts folder, for example:

```text
C:\ProgramData\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\SimpleCube.py
```

Then open Allplan, find `Simple Cube Test` in the PythonParts library, and place it
in a drawing file.

## Optional Command Line Start

On Windows, you can also try:

```powershell
& "C:\Program Files\Allplan\2026\Prg\Allplan_2026.exe" -o "@C:\ProgramData\Nemetschek\Allplan\2026\Usr\Local\PythonParts\SimpleCube.pyp"
```

## Reference

Allplan 2026 docs say a PythonPart has two essential pieces:

- a `.pyp` file with metadata and a script reference
- a `.py` file with the business logic

The standard PythonPart script needs:

- `check_allplan_version`
- `create_element`

The cube uses `Polyhedron3D.CreateCuboid`, which is the simple solid example in
the Allplan geometry docs.
