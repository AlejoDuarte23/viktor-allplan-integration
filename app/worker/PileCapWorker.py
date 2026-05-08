import json
from pathlib import Path

import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


PROJECT_NAME = "viktor-template"
DRAWING_FILE_NUMBER = 1


def check_allplan_version(build_ele, version: float) -> bool:
    return True


def _load_inputs() -> dict:
    with Path(__file__).with_name("inputs.json").open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def _open_project(doc):
    current_project_name, host_name = AllplanBaseElements.ProjectService.GetCurrentProjectNameAndHost()

    open_result = AllplanBaseElements.ProjectService.OpenProject(
        doc,
        host_name,
        PROJECT_NAME,
    )

    if open_result not in ("Project opened", "Active project", "project opened"):
        raise RuntimeError(
            f"Could not open ALLPLAN project '{PROJECT_NAME}'. "
            f"Current project was '{current_project_name}'. "
            f"ALLPLAN returned: '{open_result}'."
        )


def _load_drawing_file(doc):
    AllplanBaseElements.DrawingFileService.LoadFile(
        doc,
        DRAWING_FILE_NUMBER,
        AllplanBaseElements.DrawingFileLoadState.ActiveForeground,
    )


def _create_model_elements(data: dict) -> ModelEleList:
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
    data = _load_inputs()
    done_marker = Path(__file__).with_name("worker_done.txt")
    result_path = Path(__file__).with_name("result.json")

    _open_project(doc)
    _load_drawing_file(doc)
    AllplanBaseElements.DrawingFileService.DeleteDocument(doc)

    elements = _create_model_elements(data)

    AllplanBaseElements.CreateElements(
        doc,
        AllplanGeo.Matrix3D(),
        elements,
        [],
        None,
    )

    result = {
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
    done_marker.write_text("done", encoding="utf-8")

    return CreateElementResult()
