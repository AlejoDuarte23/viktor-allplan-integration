"""Allplan PythonPart script executed by the VIKTOR generic worker."""

from __future__ import annotations

import json
import os
from pathlib import Path

import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


def check_allplan_version(_build_ele, _version: float) -> bool:
    return True


def _context_path() -> Path:
    context_from_env = os.environ.get("ALLPLAN_WORKER_CONTEXT")

    if context_from_env:
        return Path(context_from_env)

    return Path(__file__).with_name("worker_context.json")


def _load_context() -> dict:
    with _context_path().open("r", encoding="utf-8") as file:
        return json.load(file)


def _load_inputs(context: dict) -> dict:
    with Path(context["inputs_path"]).open("r", encoding="utf-8") as file:
        return json.load(file)


def _create_cap(data: dict):
    placement = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(-data["cap_length"] / 2.0, -data["cap_width"] / 2.0, 0.0),
        AllplanGeo.Vector3D(1.0, 0.0, 0.0),
        AllplanGeo.Vector3D(0.0, 0.0, 1.0),
    )

    return AllplanGeo.BRep3D.CreateCuboid(
        placement,
        data["cap_length"],
        data["cap_width"],
        data["cap_height"],
    )


def _create_pile(data: dict, x: float, y: float):
    placement = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(x, y, -data["pile_depth"]),
        AllplanGeo.Vector3D(1.0, 0.0, 0.0),
        AllplanGeo.Vector3D(0.0, 0.0, 1.0),
    )

    return AllplanGeo.BRep3D.CreateCylinder(
        placement,
        data["pile_diameter"] / 2.0,
        data["pile_depth"],
    )


def create_element(_build_ele, _doc) -> CreateElementResult:
    context = _load_context()
    data = _load_inputs(context)

    elements = ModelEleList()
    elements.append_geometry_3d(_create_cap(data))

    for pile in data["pile_centers"]:
        elements.append_geometry_3d(_create_pile(data, pile["x"], pile["y"]))

    result = CreateElementResult(elements)
    result.placement_point = AllplanGeo.Point3D(0.0, 0.0, 0.0)
    result.multi_placement = False

    return result
