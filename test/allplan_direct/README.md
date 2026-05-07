# Simple Allplan PythonPart Test

This is the smallest useful test for running Python logic directly in Allplan,
without VIKTOR.

I cannot run this on macOS because Allplan is a Windows desktop application.
Copy these files to a Windows machine with Allplan 2026 installed.

## Files

- `SimpleCube.pyp`: Allplan PythonPart definition.
- `SimpleCube.py`: Python logic that creates one 1000 x 1000 x 1000 mm cube.
- `install_simple_cube.ps1`: Windows helper that copies the files into Allplan.
- `PileCapTest.pyp`: Allplan PythonPart definition for a pile cap test.
- `PileCapTest.py`: Python logic that creates one cap and four piles.
- `install_pile_cap.ps1`: Windows helper that copies the pile cap test into Allplan.

## Run On Windows

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\allplan_direct\install_simple_cube.ps1
```

This copies the files to:

```text
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\SimpleCube.pyp
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\SimpleCube.py
```

Then open Allplan, find `Simple Cube Test` in the PythonParts library, and place it
in a drawing file.

To copy the files and start Allplan in one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\allplan_direct\install_simple_cube.ps1 -StartAllplan
```

## Run The Pile Cap Test

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\allplan_direct\install_pile_cap.ps1
```

This copies:

```text
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\PileCapTest.pyp
$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonPartsScripts\PileCapTest.py
```

Then open Allplan, find `Pile Cap Test` in the PythonParts library, and place it
in a drawing file. It creates:

- one 4000 x 3000 x 800 mm pile cap
- four 600 mm diameter piles, 3000 mm deep

To copy the files and start Allplan in one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\allplan_direct\install_pile_cap.ps1 -StartAllplan
```

If your Allplan local folder is different, pass it explicitly:

```powershell
powershell -ExecutionPolicy Bypass -File .\test\allplan_direct\install_simple_cube.ps1 -AllplanLocal "C:\Users\AlejandroDuarteVendr\Documents\Nemetschek\Allplan\2026\Usr\Local"
```

## Optional Command Line Start

After running the install script, you can also start it manually:

```powershell
& "C:\Program Files\Allplan\2026\Prg\Allplan_2026.exe" -o "@$HOME\Documents\Nemetschek\Allplan\2026\Usr\Local\PythonParts\SimpleCube.pyp"
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
