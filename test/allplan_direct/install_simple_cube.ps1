param(
    [string]$AllplanLocal = (Join-Path $HOME "Documents\Nemetschek\Allplan\2026\Usr\Local"),
    [string]$AllplanExe = "C:\Program Files\Allplan\2026\Prg\Allplan_2026.exe",
    [switch]$StartAllplan
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$pypSource = Join-Path $scriptDir "SimpleCube.pyp"
$pySource = Join-Path $scriptDir "SimpleCube.py"

$pythonPartsDir = Join-Path $AllplanLocal "PythonParts"
$pythonPartsScriptsDir = Join-Path $AllplanLocal "PythonPartsScripts"

$pypTarget = Join-Path $pythonPartsDir "SimpleCube.pyp"
$pyTarget = Join-Path $pythonPartsScriptsDir "SimpleCube.py"

if (-not (Test-Path $pypSource)) {
    throw "Missing source file: $pypSource"
}

if (-not (Test-Path $pySource)) {
    throw "Missing source file: $pySource"
}

New-Item -ItemType Directory -Force -Path $pythonPartsDir | Out-Null
New-Item -ItemType Directory -Force -Path $pythonPartsScriptsDir | Out-Null

Copy-Item -Force $pypSource $pypTarget
Copy-Item -Force $pySource $pyTarget

Write-Host "Copied PythonPart files:"
Write-Host "  $pypTarget"
Write-Host "  $pyTarget"

if ($StartAllplan) {
    if (-not (Test-Path $AllplanExe)) {
        throw "Allplan executable not found: $AllplanExe"
    }

    Write-Host "Starting Allplan:"
    Write-Host "  $AllplanExe -o `"@$pypTarget`""
    & $AllplanExe "-o" "@$pypTarget"
}
else {
    Write-Host ""
    Write-Host "To start Allplan with this PythonPart, run:"
    Write-Host "  & `"$AllplanExe`" -o `"@$pypTarget`""
}
