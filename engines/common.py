"""Shared helpers for EVAR recommendation engines."""

from __future__ import annotations

from domain.constants import (
    BORDERLINE_OVERSIZE_MAX,
    BORDERLINE_OVERSIZE_MIN,
    HOSTILE_NECK_ANGLE_DEG,
    HOSTILE_NECK_DIAMETER_MM,
    HOSTILE_NECK_LENGTH_MM,
    IDEAL_OVERSIZE_MAX,
    IDEAL_OVERSIZE_MIN,
    MAX_STANDARD_NECK_DIAMETER_MM,
    MIN_ILIAC_ACCESS_MM,
    MIN_STANDARD_NECK_DIAMETER_MM,
    PENALTY_PER_WARNING,
    SCORE_BASE_PARTIAL,
    SCORE_EXACT_MATCH,
    SCORE_MIN_RECOMMENDATION,
    SHORT_NECK_LENGTH_MM,
)
from domain.models import Measurements


def in_range(value: float, band: tuple[float, float]) -> bool:
    return band[0] <= value <= band[1]


def band_label(band: tuple[float, float]) -> str:
    if band[0] == band[1]:
        return f"{band[0]:g} mm"
    return f"{band[0]:g}-{band[1]:g} mm"


def oversize_pct(device_mm: float, vessel_mm: float) -> float:
    if vessel_mm <= 0:
        raise ValueError("vessel_mm musi być większe od zera.")
    return ((device_mm - vessel_mm) / vessel_mm) * 100.0


def closest_midpoint_penalty(value: float, band: tuple[float, float]) -> float:
    midpoint = (band[0] + band[1]) / 2
    return abs(value - midpoint)


def status_from_flags(exact: bool, borderline: bool) -> str:
    if exact and not borderline:
        return "Dopasowanie"
    if exact or borderline:
        return "Graniczne"
    return "Brak dopasowania"


def score_recommendation(
    exact: bool,
    warning_count: int,
    *,
    exact_score: int = SCORE_EXACT_MATCH,
    partial_score: int = SCORE_BASE_PARTIAL,
    min_score: int = SCORE_MIN_RECOMMENDATION,
    penalty_per_warning: int = PENALTY_PER_WARNING,
) -> int:
    score = exact_score if exact else partial_score - warning_count * penalty_per_warning
    return max(score, min_score)


def build_global_warnings(m: Measurements) -> list[str]:
    warnings: list[str] = []
    if m.neck_length_mm < HOSTILE_NECK_LENGTH_MM:
        warnings.append("Hostile anatomy: długość szyi < 10 mm. Standardowy EVAR może być niewystarczający i może wymagać FEVAR/ChEVAR.")
    elif m.neck_length_mm < SHORT_NECK_LENGTH_MM:
        warnings.append("Krótka szyja aorty (< 15 mm) zwiększa ryzyko i zwykle wymaga bardzo ostrożnej kwalifikacji.")
    if m.neck_angle_deg >= HOSTILE_NECK_ANGLE_DEG:
        warnings.append("Znaczna angulacja szyi (>= 60°) wymaga weryfikacji IFU i doświadczenia operatora.")
    if min(m.right_iliac_diameter_mm, m.left_iliac_diameter_mm) < MIN_ILIAC_ACCESS_MM:
        warnings.append("Jedna z tętnic biodrowych ma średnicę < 8 mm, co może oznaczać trudny dostęp i ryzyko okluzji.")
    if m.neck_diameter_mm > HOSTILE_NECK_DIAMETER_MM:
        warnings.append("Hostile anatomy: szyja > 32 mm wykracza poza typowe wskazania klasycznego infrarenal EVAR i może wymagać fenestracji/chimney.")
    if not MIN_STANDARD_NECK_DIAMETER_MM <= m.neck_diameter_mm <= MAX_STANDARD_NECK_DIAMETER_MM:
        warnings.append("Średnica szyi poza zakresem typowych standardowych systemów infrarenalnych z załączonych materiałów.")
    return warnings


def overlap_range_from_length_row(length_row: dict[str, float | tuple[float, float]]) -> tuple[float, float]:
    vessel_range = length_row["vessel_length_mm"]
    total_length = length_row["total_length_mm"]
    min_overlap = total_length - vessel_range[1]
    max_overlap = total_length - vessel_range[0]
    return float(min_overlap), float(max_overlap)


def oversize_band(value: float | None) -> str:
    if value is None:
        return "unknown"
    if IDEAL_OVERSIZE_MIN <= value <= IDEAL_OVERSIZE_MAX:
        return "ideal"
    if BORDERLINE_OVERSIZE_MIN <= value <= BORDERLINE_OVERSIZE_MAX:
        return "borderline"
    return "out_of_range"
