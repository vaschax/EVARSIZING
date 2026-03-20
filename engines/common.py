"""Shared helpers for EVAR recommendation engines."""

from __future__ import annotations

from domain.constants import (
    ACCESS_MARGIN_MM,
    BORDERLINE_OVERSIZE_MAX,
    BORDERLINE_OVERSIZE_MIN,
    CRITICAL_PENALTY_WEIGHT,
    HOSTILE_NECK_ANGLE_DEG,
    HOSTILE_NECK_DIAMETER_MM,
    HOSTILE_NECK_LENGTH_MM,
    IDEAL_OVERSIZE_MAX,
    IDEAL_OVERSIZE_MIN,
    INFO_PENALTY_WEIGHT,
    MAX_STANDARD_NECK_DIAMETER_MM,
    MIN_ILIAC_ACCESS_MM,
    MIN_STANDARD_NECK_DIAMETER_MM,
    PENALTY_PER_WARNING,
    SCORE_BASE_PARTIAL,
    SCORE_EXACT_MATCH,
    SCORE_MIN_RECOMMENDATION,
    SHORT_NECK_LENGTH_MM,
    WARNING_PENALTY_WEIGHT,
)
from domain.models import Measurements, WarningMessage


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
    warnings: list[WarningMessage] | tuple[WarningMessage, ...],
    *,
    exact_score: int = SCORE_EXACT_MATCH,
    partial_score: int = SCORE_BASE_PARTIAL,
    min_score: int = SCORE_MIN_RECOMMENDATION,
    penalty_per_warning: int = PENALTY_PER_WARNING,
) -> int:
    severity_weights = {
        "info": INFO_PENALTY_WEIGHT,
        "warning": WARNING_PENALTY_WEIGHT,
        "critical": CRITICAL_PENALTY_WEIGHT,
    }
    penalty_units = sum(severity_weights[item.severity] for item in warnings)
    score = (exact_score if exact else partial_score) - penalty_units * penalty_per_warning
    return max(score, min_score)


def make_warning(message: str, severity: str = "warning", *, code: str | None = None) -> WarningMessage:
    return WarningMessage(message=message, severity=severity, code=code)


def build_global_warnings(m: Measurements) -> list[WarningMessage]:
    warnings: list[WarningMessage] = []
    if m.neck_length_mm < HOSTILE_NECK_LENGTH_MM:
        warnings.append(
            make_warning(
                "Hostile anatomy: długość szyi < 10 mm. Standardowy EVAR może być niewystarczający i może wymagać FEVAR/ChEVAR.",
                "critical",
                code="hostile_neck_length",
            )
        )
    elif m.neck_length_mm < SHORT_NECK_LENGTH_MM:
        warnings.append(make_warning("Krótka szyja aorty (< 15 mm) zwiększa ryzyko i zwykle wymaga bardzo ostrożnej kwalifikacji.", code="short_neck"))
    if m.neck_angle_deg >= HOSTILE_NECK_ANGLE_DEG:
        warnings.append(make_warning("Znaczna angulacja szyi (>= 60°) wymaga weryfikacji IFU i doświadczenia operatora.", code="neck_angulation"))
    if min(m.right_iliac_diameter_mm, m.left_iliac_diameter_mm) < MIN_ILIAC_ACCESS_MM:
        warnings.append(make_warning("Jedna z tętnic biodrowych ma średnicę < 8 mm, co może oznaczać trudny dostęp i ryzyko okluzji.", code="small_iliac"))
    if m.neck_diameter_mm > HOSTILE_NECK_DIAMETER_MM:
        warnings.append(
            make_warning(
                "Hostile anatomy: szyja > 32 mm wykracza poza typowe wskazania klasycznego infrarenal EVAR i może wymagać fenestracji/chimney.",
                "critical",
                code="hostile_neck_diameter",
            )
        )
    if not MIN_STANDARD_NECK_DIAMETER_MM <= m.neck_diameter_mm <= MAX_STANDARD_NECK_DIAMETER_MM:
        warnings.append(make_warning("Średnica szyi poza zakresem typowych standardowych systemów infrarenalnych z załączonych materiałów.", code="neck_out_of_range"))
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


def profile_fr_from_item(item: dict[str, float | str]) -> float | None:
    for key in ("introducer_fr", "catheter_fr", "sheath_fr"):
        value = item.get(key)
        if value is not None:
            return float(value)
    return None


def required_access_diameter_mm(profile_fr: float) -> float:
    return profile_fr / 3.0 + ACCESS_MARGIN_MM


def access_diameter_for_side(m: Measurements, side: str | None) -> float | None:
    if side == "ipsilateral":
        return m.ipsilateral_eia_diameter_mm
    if side == "contralateral":
        return m.contralateral_eia_diameter_mm
    return None


def build_access_warning(
    *,
    manufacturer: str,
    component_label: str,
    side_label: str,
    profile_fr: float | None,
    eia_diameter_mm: float | None,
) -> WarningMessage | None:
    if profile_fr is None or eia_diameter_mm is None:
        return None
    required_mm = required_access_diameter_mm(profile_fr)
    if eia_diameter_mm >= required_mm:
        return None
    return make_warning(
        (
            f"CRITICAL ACCESS WARNING: {manufacturer} {component_label} wymaga dostępu ~ {profile_fr:.0f}F "
            f"(orientacyjnie >= {required_mm:.1f} mm), ale strona {side_label.lower()} ma EIA {eia_diameter_mm:.1f} mm. "
            "Rozważ iliac conduit lub system o niższym profilu."
        ),
        "critical",
        code="access_vessel_too_small",
    )
