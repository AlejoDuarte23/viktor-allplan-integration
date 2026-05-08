import json
import uuid
from pathlib import Path

import viktor as vkt
from viktor.external.python import PythonAnalysis


APP_DIR = Path(__file__).parent
ALLPLAN_WORKER_DIR = APP_DIR / "worker"


class Parametrization(vkt.Parametrization):
    geometry = vkt.Section("Geometry", initially_expanded=True)
    geometry.intro = vkt.Text(
        "# Four Pile Cap\n\n"
        "Parametric CAD test for one rectangular pile cap supported by four piles.\n"
        "Dimensions are in millimeters."
    )
    geometry.cap_length = vkt.NumberField("Pile cap length", default=4000.0, min=1000.0, suffix="mm", flex=50)
    geometry.cap_width = vkt.NumberField("Pile cap width", default=3000.0, min=1000.0, suffix="mm", flex=50)
    geometry.cap_height = vkt.NumberField("Pile cap height", default=800.0, min=200.0, suffix="mm", flex=50)
    geometry.pile_diameter = vkt.NumberField("Pile diameter", default=600.0, min=100.0, suffix="mm", flex=50)
    geometry.pile_depth = vkt.NumberField("Pile depth", default=3000.0, min=500.0, suffix="mm", flex=50)
    geometry.pile_spacing_x = vkt.NumberField("Pile spacing X", default=2600.0, min=500.0, suffix="mm", flex=50)
    geometry.pile_spacing_y = vkt.NumberField("Pile spacing Y", default=1800.0, min=500.0, suffix="mm", flex=50)

    allplan = vkt.Section("Allplan", initially_expanded=True)
    allplan.download = vkt.DownloadButton(
        "Download Allplan project",
        method="download_allplan_project",
        longpoll=True,
        flex=100,
    )


class Controller(vkt.Controller):
    label = "Pile Cap"
    parametrization = Parametrization(width=35)

    @vkt.GeometryView("Geometry", duration_guess=1, x_axis_to_right=True)
    def geometry_view(self, params, **kwargs):
        concrete = vkt.Material("Concrete", color=(190, 190, 185), opacity=0.75)
        pile_material = vkt.Material("Pile concrete", color=(145, 145, 140), opacity=0.85)

        cap = vkt.RectangularExtrusion(
            params.geometry.cap_length,
            params.geometry.cap_width,
            vkt.Line(vkt.Point(0.0, 0.0, 0.0), vkt.Point(0.0, 0.0, params.geometry.cap_height)),
            material=concrete,
            identifier="pile-cap",
        )

        geometry = [cap]

        for pile in self.get_pile_centers(params.geometry.pile_spacing_x, params.geometry.pile_spacing_y):
            line = vkt.Line(
                vkt.Point(pile["x"], pile["y"], -params.geometry.pile_depth),
                vkt.Point(pile["x"], pile["y"], 0.0),
            )
            geometry.append(
                vkt.CircularExtrusion(
                    params.geometry.pile_diameter,
                    line,
                    material=pile_material,
                    identifier=pile["id"],
                )
            )

        return vkt.GeometryResult(geometry=geometry)

    def download_allplan_project(self, params, **kwargs):
        run_id = uuid.uuid4().hex
        worker_input = {
            "run_id": run_id,
            "cap_length": params.geometry.cap_length,
            "cap_width": params.geometry.cap_width,
            "cap_height": params.geometry.cap_height,
            "pile_diameter": params.geometry.pile_diameter,
            "pile_depth": params.geometry.pile_depth,
            "pile_centers": self.get_pile_centers(params.geometry.pile_spacing_x, params.geometry.pile_spacing_y),
        }

        files = [
            ("inputs.json", vkt.File.from_data(json.dumps(worker_input, indent=2))),
            ("template_project.zip", vkt.File.from_path(ALLPLAN_WORKER_DIR / "viktor-template.prj.zip")),
            ("PileCapWorker.pyp", vkt.File.from_path(ALLPLAN_WORKER_DIR / "PileCapWorker.pyp")),
            ("PileCapWorker.py", vkt.File.from_path(ALLPLAN_WORKER_DIR / "PileCapWorker.py")),
        ]

        analysis = PythonAnalysis(
            script=vkt.File.from_path(ALLPLAN_WORKER_DIR / "run_allplan_model.py"),
            files=files,
            output_filenames=["result_project.zip", "result.json", "worker_log.txt"],
        )
        vkt.progress_message("Starting Allplan worker.")
        analysis.execute(timeout=900)
        result_project_zip = analysis.get_output_file("result_project.zip")
        analysis.get_output_file("result.json")
        analysis.get_output_file("worker_log.txt")

        return vkt.DownloadResult(result_project_zip, f"result_project_{run_id}.zip")

    @staticmethod
    def get_pile_centers(pile_spacing_x: float, pile_spacing_y: float) -> list[dict[str, float | str]]:
        half_x = pile_spacing_x / 2.0
        half_y = pile_spacing_y / 2.0

        return [
            {"id": "P1", "x": -half_x, "y": -half_y},
            {"id": "P2", "x": half_x, "y": -half_y},
            {"id": "P3", "x": -half_x, "y": half_y},
            {"id": "P4", "x": half_x, "y": half_y},
        ]
