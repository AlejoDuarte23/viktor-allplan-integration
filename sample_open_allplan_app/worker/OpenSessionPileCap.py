import json
import traceback
from pathlib import Path

import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


def _log(message: str):
    log_path = Path(__file__).with_name("execution_log.txt")
    with log_path.open("a", encoding="utf-8") as file:
        file.write(f"{message}\n")


def _write_error(error: BaseException):
    error_path = Path(__file__).with_name("execution_error.txt")
    error_path.write_text(
        "".join(traceback.format_exception(type(error), error, error.__traceback__)),
        encoding="utf-8",
    )


def check_allplan_version(build_ele, version: float) -> bool:
    return True


def _load_inputs() -> dict:
    return json.loads(Path(__file__).with_name("inputs.json").read_text(encoding="utf-8"))


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
    try:
        _log("PythonPart execution started.")
        data = _load_inputs()
        elements = _create_model_elements(data)

        result_path = Path(__file__).with_name("execution_result.json")
        done_marker = Path(__file__).with_name("execution_done.txt")

        result_path.write_text(
            json.dumps(
                {
                    "run_id": data["run_id"],
                    "mode": "open_allplan_session",
                    "created": {
                        "pile_cap": 1,
                        "piles": len(data["pile_centers"]),
                        "total_geometry": 1 + len(data["pile_centers"]),
                    },
                    "inputs": data,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        done_marker.write_text("done", encoding="utf-8")
        _log("Geometry created in active document.")
        _log("execution_result.json and execution_done.txt written.")

        result = CreateElementResult(elements)
        result.placement_point = AllplanGeo.Point3D(0.0, 0.0, 0.0)
        result.multi_placement = False
        return result

    except BaseException as error:
        _log(f"PythonPart execution failed: {error}")
        _write_error(error)
        raise
