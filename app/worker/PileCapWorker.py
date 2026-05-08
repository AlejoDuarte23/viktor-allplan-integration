import json
from pathlib import Path

import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


def check_allplan_version(build_ele, version: float) -> bool:
    return True


def create_element(build_ele, doc) -> CreateElementResult:
    with Path(__file__).with_name("inputs.json").open("r", encoding="utf-8") as file:
        data = json.load(file)

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

    result = CreateElementResult(elements)
    result.placement_point = AllplanGeo.Point3D(0.0, 0.0, 0.0)
    result.multi_placement = False

    return result
