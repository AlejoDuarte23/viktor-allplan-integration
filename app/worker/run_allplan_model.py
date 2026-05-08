import shutil
import subprocess
import time
from pathlib import Path


ALLPLAN_EXE = Path(r"C:\Program Files\Allplan\Allplan 2026\Prg\Allplan_2026.exe")
ALLPLAN_LOCAL = Path.home() / "Documents" / "Nemetschek" / "Allplan" / "2026" / "Usr" / "Local"
ALLPLAN_PROJECTS_DIR = Path(r"C:\Data\Allplan\Allplan 2026\Prj")
PROJECT_NAME = "viktor-template"
PROJECT_DIR = ALLPLAN_PROJECTS_DIR / f"{PROJECT_NAME}.prj"


def install_template_project(template_zip: Path):
    extract_dir = template_zip.parent / "_template_project_extract"

    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    if PROJECT_DIR.exists():
        shutil.rmtree(PROJECT_DIR)

    extract_dir.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(str(template_zip), str(extract_dir), "zip")

    project_folder_inside_zip = extract_dir / f"{PROJECT_NAME}.prj"
    if project_folder_inside_zip.exists():
        shutil.copytree(project_folder_inside_zip, PROJECT_DIR)
    else:
        shutil.copytree(extract_dir, PROJECT_DIR)

    shutil.rmtree(extract_dir)


def main():
    workdir = Path.cwd()
    template_zip = workdir / "template_project.zip"
    inputs_path = workdir / "inputs.json"
    pyp_source = workdir / "PileCapWorker.pyp"
    py_source = workdir / "PileCapWorker.py"
    output_zip = workdir / "result_project.zip"

    if output_zip.exists():
        output_zip.unlink()

    install_template_project(template_zip)

    python_parts_dir = ALLPLAN_LOCAL / "PythonParts" / "ViktorWorker"
    python_scripts_dir = ALLPLAN_LOCAL / "PythonPartsScripts" / "ViktorWorker"
    python_parts_dir.mkdir(parents=True, exist_ok=True)
    python_scripts_dir.mkdir(parents=True, exist_ok=True)

    pyp_target = python_parts_dir / "PileCapWorker.pyp"
    py_target = python_scripts_dir / "PileCapWorker.py"
    inputs_target = python_scripts_dir / "inputs.json"
    done_marker = python_scripts_dir / "worker_done.txt"
    result_source = python_scripts_dir / "result.json"
    output_json = workdir / "result.json"

    if done_marker.exists():
        done_marker.unlink()

    if result_source.exists():
        result_source.unlink()

    if output_json.exists():
        output_json.unlink()

    shutil.copy2(pyp_source, pyp_target)
    shutil.copy2(py_source, py_target)
    shutil.copy2(inputs_path, inputs_target)

    process = subprocess.Popen(
        [
            str(ALLPLAN_EXE),
            "-o",
            f"@{pyp_target}",
        ],
        cwd=str(workdir),
    )

    deadline = time.time() + 840
    while not done_marker.exists():
        if process.poll() is not None:
            raise RuntimeError(f"Allplan closed before the worker finished. Exit code: {process.returncode}")

        if time.time() > deadline:
            process.terminate()
            raise TimeoutError("Allplan worker did not finish within 840 seconds.")

        time.sleep(1)

    shutil.copy2(result_source, output_json)

    shutil.make_archive(
        base_name=str(output_zip.with_suffix("")),
        format="zip",
        root_dir=str(PROJECT_DIR),
    )


if __name__ == "__main__":
    main()
