"""Core domain models for the EVAR sizing prototype."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from domain.constants import VALID_IPSILATERAL_SIDES


@dataclass(frozen=True)
class Measurements:
    neck_diameter_mm: float
    neck_length_mm: float
    neck_angle_deg: float
    aortic_bifurcation_length_mm: float
    right_iliac_diameter_mm: float
    left_iliac_diameter_mm: float
    right_iliac_length_mm: float
    left_iliac_length_mm: float
    ipsilateral_side: str

    def __post_init__(self) -> None:
        positive_fields = {
            "neck_diameter_mm": self.neck_diameter_mm,
            "neck_length_mm": self.neck_length_mm,
            "aortic_bifurcation_length_mm": self.aortic_bifurcation_length_mm,
            "right_iliac_diameter_mm": self.right_iliac_diameter_mm,
            "left_iliac_diameter_mm": self.left_iliac_diameter_mm,
            "right_iliac_length_mm": self.right_iliac_length_mm,
            "left_iliac_length_mm": self.left_iliac_length_mm,
        }
        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} musi być większe od zera.")
        if not 0 <= self.neck_angle_deg <= 180:
            raise ValueError("neck_angle_deg musi być w zakresie 0-180.")
        if self.ipsilateral_side not in VALID_IPSILATERAL_SIDES:
            raise ValueError("ipsilateral_side musi być 'right' albo 'left'.")

    @property
    def ipsilateral_label(self) -> str:
        return "Prawa" if self.ipsilateral_side == "right" else "Lewa"

    @property
    def contralateral_label(self) -> str:
        return "Lewa" if self.ipsilateral_side == "right" else "Prawa"

    @property
    def ipsilateral_diameter_mm(self) -> float:
        return self.right_iliac_diameter_mm if self.ipsilateral_side == "right" else self.left_iliac_diameter_mm

    @property
    def contralateral_diameter_mm(self) -> float:
        return self.left_iliac_diameter_mm if self.ipsilateral_side == "right" else self.right_iliac_diameter_mm

    @property
    def ipsilateral_length_mm(self) -> float:
        return self.right_iliac_length_mm if self.ipsilateral_side == "right" else self.left_iliac_length_mm

    @property
    def contralateral_length_mm(self) -> float:
        return self.left_iliac_length_mm if self.ipsilateral_side == "right" else self.right_iliac_length_mm


@dataclass(frozen=True)
class ComponentRecommendation:
    title: str
    component_type: str
    side: str | None
    label: str
    details: str
    official: bool
    catalogue: str | None = None
    oversize_pct: float | None = None
    required_overlap_mm: float | None = None
    predicted_overlap_range_mm: tuple[float, float] | None = None
    proximal_diameter_mm: float | None = None
    distal_diameter_mm: float | None = None
    covered_length_mm: float | None = None


@dataclass(frozen=True)
class Recommendation:
    manufacturer: str
    family: str
    status: str
    score: int
    warnings: tuple[str, ...]
    components: tuple[ComponentRecommendation, ...]
    notes: tuple[str, ...]
    source: str
    alternatives: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


@dataclass(frozen=True)
class RecommendationBundle:
    warnings: tuple[str, ...]
    recommendations: tuple[Recommendation, ...]
    sources: dict[str, str]
