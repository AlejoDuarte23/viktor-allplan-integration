"""Minimal Allplan PythonPart test.

Copy this file to an Allplan 2026 PythonPartsScripts folder and run the
matching SimpleCube.pyp from Allplan.
"""

from __future__ import annotations

import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


def check_allplan_version(_build_ele, _version: float) -> bool:
    return True


def create_element(_build_ele, _doc) -> CreateElementResult:
    cube = AllplanGeo.Polyhedron3D.CreateCuboid(
        length=1000.0,
        width=1000.0,
        height=1000.0,
    )

    elements = ModelEleList()
    elements.append_geometry_3d(cube)

    return CreateElementResult(elements)
