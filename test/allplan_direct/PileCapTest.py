"""Minimal pile cap and pile solids test for Allplan 2026."""

from __future__ import annotations

import NemAll_Python_Geometry as AllplanGeo
from CreateElementResult import CreateElementResult
from TypeCollections.ModelEleList import ModelEleList


CAP_LENGTH = 4000.0
CAP_WIDTH = 3000.0
CAP_HEIGHT = 800.0

PILE_DIAMETER = 600.0
PILE_DEPTH = 3000.0

PILE_OFFSET_X = 1300.0
PILE_OFFSET_Y = 900.0


def check_allplan_version(_build_ele, _version: float) -> bool:
    return True


def create_element(_build_ele, _doc) -> CreateElementResult:
    elements = ModelEleList()

    cap_placement = AllplanGeo.AxisPlacement3D(
        AllplanGeo.Point3D(-CAP_LENGTH / 2.0, -CAP_WIDTH / 2.0, 0.0),
        AllplanGeo.Vector3D(1.0, 0.0, 0.0),
        AllplanGeo.Vector3D(0.0, 0.0, 1.0),
    )
    cap = AllplanGeo.BRep3D.CreateCuboid(
        cap_placement,
        CAP_LENGTH,
        CAP_WIDTH,
        CAP_HEIGHT,
    )
    elements.append_geometry_3d(cap)

    pile_radius = PILE_DIAMETER / 2.0
    pile_centers = (
        (-PILE_OFFSET_X, -PILE_OFFSET_Y),
        (PILE_OFFSET_X, -PILE_OFFSET_Y),
        (-PILE_OFFSET_X, PILE_OFFSET_Y),
        (PILE_OFFSET_X, PILE_OFFSET_Y),
    )

    for x, y in pile_centers:
        placement = AllplanGeo.AxisPlacement3D(
            AllplanGeo.Point3D(x, y, -PILE_DEPTH),
            AllplanGeo.Vector3D(1.0, 0.0, 0.0),
            AllplanGeo.Vector3D(0.0, 0.0, 1.0),
        )
        pile = AllplanGeo.BRep3D.CreateCylinder(placement, pile_radius, PILE_DEPTH)
        elements.append_geometry_3d(pile)

    result = CreateElementResult(elements)

    # Insert immediately at global coordinates X=0, Y=0, Z=0.
    result.placement_point = AllplanGeo.Point3D(0.0, 0.0, 0.0)
    result.multi_placement = False

    return result
