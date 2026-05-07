from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PileCapParameters:
    cap_length: float = 4000.0
    cap_width: float = 3000.0
    cap_height: float = 800.0
    pile_diameter: float = 600.0
    pile_depth: float = 3000.0
    pile_spacing_x: float = 2600.0
    pile_spacing_y: float = 1800.0

    @classmethod
    def from_params(cls, params) -> "PileCapParameters":
        geometry = params.geometry

        return cls(
            cap_length=float(geometry.cap_length),
            cap_width=float(geometry.cap_width),
            cap_height=float(geometry.cap_height),
            pile_diameter=float(geometry.pile_diameter),
            pile_depth=float(geometry.pile_depth),
            pile_spacing_x=float(geometry.pile_spacing_x),
            pile_spacing_y=float(geometry.pile_spacing_y),
        )

    @property
    def pile_radius(self) -> float:
        return self.pile_diameter / 2.0

    @property
    def pile_centers(self) -> list[dict[str, float]]:
        half_x = self.pile_spacing_x / 2.0
        half_y = self.pile_spacing_y / 2.0

        return [
            {"id": "P1", "x": -half_x, "y": -half_y},
            {"id": "P2", "x": half_x, "y": -half_y},
            {"id": "P3", "x": -half_x, "y": half_y},
            {"id": "P4", "x": half_x, "y": half_y},
        ]

    def to_worker_input(self) -> dict:
        data = asdict(self)
        data["pile_centers"] = self.pile_centers
        return data


def get_default_parameters() -> PileCapParameters:
    return PileCapParameters()
