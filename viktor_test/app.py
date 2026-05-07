from __future__ import annotations

import json
import textwrap
from pathlib import Path

import viktor as vkt
from viktor.external.python import PythonAnalysis

from pile_cap_model import PileCapParameters


APP_DIR = Path(__file__).parent
ALLPLAN_WORKER_DIR = APP_DIR / "worker" / "allplan"


class Parametrization(vkt.Parametrization):
    geometry = vkt.Section("Geometry", initially_expanded=True)
    geometry.intro = vkt.Text(
        textwrap.dedent(
            """\
            # Four Pile Cap

            Parametric CAD test for one rectangular pile cap supported by four piles.
            Dimensions are in millimeters.
            """
        )
    )
    geometry.cap_length = vkt.NumberField("Pile cap length", default=4000.0, min=1000.0, suffix="mm", flex=50)
    geometry.cap_width = vkt.NumberField("Pile cap width", default=3000.0, min=1000.0, suffix="mm", flex=50)
    geometry.cap_height = vkt.NumberField("Pile cap height", default=800.0, min=200.0, suffix="mm", flex=50)
    geometry.pile_diameter = vkt.NumberField("Pile diameter", default=600.0, min=100.0, suffix="mm", flex=50)
    geometry.pile_depth = vkt.NumberField("Pile depth", default=3000.0, min=500.0, suffix="mm", flex=50)
    geometry.pile_spacing_x = vkt.NumberField("Pile spacing X", default=2600.0, min=500.0, suffix="mm", flex=50)
    geometry.pile_spacing_y = vkt.NumberField("Pile spacing Y", default=1800.0, min=500.0, suffix="mm", flex=50)

    allplan = vkt.Section("Allplan", initially_expanded=True)
    allplan.create = vkt.ActionButton(
        "Create geometry in Allplan",
        method="create_in_allplan",
        longpoll=True,
        flex=100,
    )


class Controller(vkt.Controller):
    label = "Pile Cap"
    parametrization = Parametrization(width=35)

    @vkt.GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def geometry_view(self, params, **kwargs):
        model = PileCapParameters.from_params(params)

        concrete = vkt.Material("Concrete", color=(190, 190, 185), opacity=0.75)
        pile_material = vkt.Material("Pile concrete", color=(145, 145, 140), opacity=0.85)

        cap = vkt.RectangularExtrusion(
            model.cap_length,
            model.cap_width,
            vkt.Line(vkt.Point(0.0, 0.0, 0.0), vkt.Point(0.0, 0.0, model.cap_height)),
            material=concrete,
            identifier="pile-cap",
        )

        geometry = [cap]

        for pile in model.pile_centers:
            line = vkt.Line(
                vkt.Point(pile["x"], pile["y"], -model.pile_depth),
                vkt.Point(pile["x"], pile["y"], 0.0),
            )
            geometry.append(
                vkt.CircularExtrusion(
                    model.pile_diameter,
                    line,
                    material=pile_material,
                    identifier=pile["id"],
                )
            )

        return vkt.GeometryResult(geometry=geometry)

    def create_in_allplan(self, params, **kwargs) -> None:
        model = PileCapParameters.from_params(params)

        files = [
            ("inputs.json", vkt.File.from_data(json.dumps(model.to_worker_input(), indent=2))),
            ("PileCapWorker.pyp", vkt.File.from_path(ALLPLAN_WORKER_DIR / "PileCapWorker.pyp")),
            ("PileCapWorker.py", vkt.File.from_path(ALLPLAN_WORKER_DIR / "PileCapWorker.py")),
        ]

        analysis = PythonAnalysis(
            script=vkt.File.from_path(ALLPLAN_WORKER_DIR / "run_allplan_model.py"),
            files=files,
        )
        vkt.progress_message("Starting Allplan Python worker.")
        analysis.execute(timeout=900)

        vkt.UserMessage.success("Allplan launch command finished. Check Allplan for the generated geometry.")
