import json
import traceback
from pathlib import Path

import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList

# Remember to create an empty project with this name in the Allplan project administration.
PROJECT_NAME = "viktor-template"
DRAWING_FILE_NUMBER = 1


def logMessage(message: str):
    log_path = Path(__file__).with_name("worker_log.txt")
    with log_path.open("a", encoding="utf-8") as file:
        file.write(f"{message}\n")


def writeError(error: BaseException):
    error_path = Path(__file__).with_name("worker_error.txt")
    error_path.write_text(
        "".join(traceback.format_exception(type(error), error, error.__traceback__)),
        encoding="utf-8",
    )


def check_allplan_version(build_ele, version: float) -> bool:
    return True


def loadInputs() -> dict:
    with Path(__file__).with_name("inputs.json").open("r", encoding="utf-8") as file:
        return json.load(file)


def openProject(doc):
    current_project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()

    if current_project_name == PROJECT_NAME:
        logMessage(f"Project '{PROJECT_NAME}' is already active.")
        return

    open_result = AllplanBaseElements.ProjectService.OpenProject(
        doc,
        host_name,
        PROJECT_NAME,
    )

    logMessage(f"OpenProject returned: {open_result}")

    if open_result not in ("Project opened", "Active project", "project opened"):
        raise RuntimeError(
            f"Could not open Allplan project '{PROJECT_NAME}'. "
            f"Current project was '{current_project_name}'. "
            f"Allplan returned: '{open_result}'."
        )


def loadDrawingFile(doc):
    drawing_service = AllplanBaseElements.DrawingFileService()

    drawing_service.LoadFile(
        doc,
        DRAWING_FILE_NUMBER,
        AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
    )


def createModelElements(data: dict) -> ModelEleList:
    elements = ModelEleList()

    cap_placement = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(-data["cap_length"] / 2.0, -data["cap_width"] / 2.0, 0.0),
        AllplanGeo.Vector3D(1.0, 0.0, 0.0),
        AllplanGeo.Vector3D(0.0, 0.0, 1.0),
    )
    elements.append_geometry_3d(
        AllplanGeo.BRep3D.CreateCuboid(
            cap_placement,
            data["cap_length"],
            data["cap_width"],
            data["cap_height"],
        )
    )

    for pile in data["pile_centers"]:
        pile_placement = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(pile["x"], pile["y"], -data["pile_depth"]),
            AllplanGeo.Vector3D(1.0, 0.0, 0.0),
            AllplanGeo.Vector3D(0.0, 0.0, 1.0),
        )
        elements.append_geometry_3d(
            AllplanGeo.BRep3D.CreateCylinder(
                pile_placement,
                data["pile_diameter"] / 2.0,
                data["pile_depth"],
            )
        )

    return elements


def create_element(build_ele, doc) -> CreateElementResult:
    try:
        logMessage("PythonPart started.")

        data = loadInputs()
        run_id = data["run_id"]

        done_marker = Path(__file__).with_name("worker_done.txt")
        result_path = Path(__file__).with_name("result.json")

        logMessage(f"Run ID: {run_id}.")
        logMessage("Opening project.")
        openProject(doc)

        logMessage("Project opened.")
        logMessage(f"Loading drawing file {DRAWING_FILE_NUMBER}.")
        loadDrawingFile(doc)

        elements = createModelElements(data)

        logMessage("Writing elements to Allplan document.")
        AllplanBaseElements.CreateElements(
            doc,
            AllplanGeo.Matrix3D(),
            elements,
            [],
            None,
        )

        logMessage("CreateElements finished.")

        result = {
            "run_id": run_id,
            "project_name": PROJECT_NAME,
            "drawing_file_number": DRAWING_FILE_NUMBER,
            "created": {
                "pile_cap": 1,
                "piles": len(data["pile_centers"]),
                "total_geometry": 1 + len(data["pile_centers"]),
            },
            "inputs": data,
        }

        result_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        logMessage("result.json written.")

        done_marker.write_text("done", encoding="utf-8")
        logMessage("worker_done.txt written. Allplan close was not requested.")

        return CreateElementResult()

    except BaseException as error:
        logMessage(f"Worker failed: {error}")
        writeError(error)
        raise
