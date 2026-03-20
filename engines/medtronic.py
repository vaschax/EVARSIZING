"""Medtronic Endurant recommendation engine."""

from __future__ import annotations

from typing import Any

from evar_data import DATA_SOURCES, MEDTRONIC_AORTIC_EXTENDERS, MEDTRONIC_BIFURCATIONS, MEDTRONIC_ILIAC_EXTENDERS, MEDTRONIC_LIMBS, MEDTRONIC_SHORT_BODIES
from domain.constants import (
    HEURISTIC_PENALTY_PER_WARNING,
    IDEAL_OVERSIZE_MAX,
    IDEAL_OVERSIZE_MIN,
    ILIAC_OVERSIZE_MAX,
    MEDTRONIC_REQUIRED_OVERLAP_MM,
    SCORE_BASE_HEURISTIC,
    SCORE_MIN_HEURISTIC,
    TARGET_ILIAC_OVERSIZE,
    TARGET_NECK_OVERSIZE,
)
from domain.models import ComponentRecommendation, Measurements, Recommendation, WarningMessage
from engines.common import build_access_warning, make_warning, oversize_pct, profile_fr_from_item, score_recommendation, status_from_flags


def _pick_medtronic_body(pool: list[dict[str, Any]], m: Measurements) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in pool:
        neck_oversize = oversize_pct(item["proximal_diameter_mm"], m.neck_diameter_mm)
        iliac_oversize = oversize_pct(item["distal_diameter_mm"], m.ipsilateral_diameter_mm)
        if IDEAL_OVERSIZE_MIN <= neck_oversize <= IDEAL_OVERSIZE_MAX and 0 <= iliac_oversize <= ILIAC_OVERSIZE_MAX:
            candidate = dict(item)
            candidate["neck_oversize_pct"] = neck_oversize
            candidate["iliac_oversize_pct"] = iliac_oversize
            out.append(candidate)
    out.sort(key=lambda item: (abs(item["covered_length_mm"] - m.ipsilateral_length_mm), abs(item["neck_oversize_pct"] - TARGET_NECK_OVERSIZE)))
    return out


def _pick_medtronic_limb(m: Measurements) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in MEDTRONIC_LIMBS:
        iliac_oversize = oversize_pct(item["distal_diameter_mm"], m.contralateral_diameter_mm)
        if 0 <= iliac_oversize <= ILIAC_OVERSIZE_MAX:
            candidate = dict(item)
            candidate["iliac_oversize_pct"] = iliac_oversize
            out.append(candidate)
    out.sort(key=lambda item: (abs(item["covered_length_mm"] - m.contralateral_length_mm), abs(item["iliac_oversize_pct"] - TARGET_ILIAC_OVERSIZE)))
    return out


def recommend_medtronic(m: Measurements) -> Recommendation:
    warnings: list[WarningMessage] = [
        make_warning(
            "Dla Medtronic załączony PDF podaje tabele rozmiarów urządzenia, ale nie podaje wprost zakresów naczyń. Dobór w tej aplikacji opiera się na heurystyce oversizingu 10-20% dla szyi i 0-25% dla dystalnego landing zone.",
            "info",
            code="medtronic_heuristic",
        ),
    ]
    body_candidates = _pick_medtronic_body(MEDTRONIC_SHORT_BODIES + MEDTRONIC_BIFURCATIONS, m)
    main_body = next((item for item in body_candidates if item["covered_length_mm"] <= m.ipsilateral_length_mm), body_candidates[0] if body_candidates else None)

    limb_candidates = _pick_medtronic_limb(m)
    contra_limb = next((item for item in limb_candidates if item["covered_length_mm"] <= m.contralateral_length_mm), limb_candidates[0] if limb_candidates else None)

    if not main_body:
        warnings.append(make_warning("Brak sensownego korpusu Endurant dla zadanych wymiarów przy przyjętej heurystyce.", code="medtronic_no_body"))
    elif main_body["covered_length_mm"] > m.ipsilateral_length_mm:
        warnings.append(make_warning("Najbliższy korpus Endurant jest dłuższy niż długość strony ipsilateralnej.", code="medtronic_body_too_long"))
    if not contra_limb:
        warnings.append(make_warning("Brak sensownej odnogi Endurant dla strony kontralateralnej przy przyjętej heurystyce.", code="medtronic_no_limb"))
    elif contra_limb["covered_length_mm"] > m.contralateral_length_mm:
        warnings.append(make_warning("Najkrótsza odnoga Endurant jest dłuższa niż długość strony kontralateralnej.", code="medtronic_limb_too_long"))

    exact = bool(
        main_body
        and contra_limb
        and main_body["covered_length_mm"] <= m.ipsilateral_length_mm
        and contra_limb["covered_length_mm"] <= m.contralateral_length_mm
    )

    components: list[ComponentRecommendation] = []
    if main_body:
        main_body_profile = profile_fr_from_item(main_body)
        components.append(
            ComponentRecommendation(
                title=f"Korpus główny ({main_body['family']})",
                component_type="main_body",
                side="ipsilateral",
                label=f"{main_body['proximal_diameter_mm']} / {main_body['distal_diameter_mm']} mm | długość {main_body['covered_length_mm']} mm",
                details=(
                    f"Oversizing szyi ~ {main_body['neck_oversize_pct']:.1f}% i dystalny landing ~ "
                    f"{main_body['iliac_oversize_pct']:.1f}% względem strony {m.ipsilateral_label.lower()}."
                ),
                official=False,
                oversize_pct=main_body["neck_oversize_pct"],
                required_overlap_mm=MEDTRONIC_REQUIRED_OVERLAP_MM,
                proximal_diameter_mm=main_body["proximal_diameter_mm"],
                distal_diameter_mm=main_body["distal_diameter_mm"],
                covered_length_mm=main_body["covered_length_mm"],
                access_profile_fr=main_body_profile,
                required_access_diameter_mm=(main_body_profile / 3.0 + 1.0) if main_body_profile is not None else None,
            )
        )
        access_warning = build_access_warning(
            manufacturer="Medtronic",
            component_label="main body",
            side_label=m.ipsilateral_label,
            profile_fr=main_body_profile,
            eia_diameter_mm=m.ipsilateral_eia_diameter_mm,
        )
        if access_warning:
            warnings.append(access_warning)
    if contra_limb:
        contra_profile = profile_fr_from_item(contra_limb)
        components.append(
            ComponentRecommendation(
                title=f"Odnoga kontralateralna ({m.contralateral_label})",
                component_type="limb",
                side="contralateral",
                label=f"{contra_limb['distal_diameter_mm']} mm | długość {contra_limb['covered_length_mm']} mm",
                details=f"Oversizing landing zone ~ {contra_limb['iliac_oversize_pct']:.1f}%.",
                official=False,
                oversize_pct=contra_limb["iliac_oversize_pct"],
                required_overlap_mm=MEDTRONIC_REQUIRED_OVERLAP_MM,
                distal_diameter_mm=contra_limb["distal_diameter_mm"],
                covered_length_mm=contra_limb["covered_length_mm"],
                access_profile_fr=contra_profile,
                required_access_diameter_mm=(contra_profile / 3.0 + 1.0) if contra_profile is not None else None,
            )
        )
        access_warning = build_access_warning(
            manufacturer="Medtronic",
            component_label="contralateral limb",
            side_label=m.contralateral_label,
            profile_fr=contra_profile,
            eia_diameter_mm=m.contralateral_eia_diameter_mm,
        )
        if access_warning:
            warnings.append(access_warning)
    if main_body and contra_limb:
        warnings.append(make_warning(f"Medtronic: potwierdź w IFU, że połączone komponenty zapewniają minimum {MEDTRONIC_REQUIRED_OVERLAP_MM:.0f} mm zakładki (overlap).", code="medtronic_overlap_check"))

    extenders = [item for item in MEDTRONIC_AORTIC_EXTENDERS if IDEAL_OVERSIZE_MIN <= oversize_pct(item["diameter_mm"], m.neck_diameter_mm) <= IDEAL_OVERSIZE_MAX]
    iliac_ext = [item for item in MEDTRONIC_ILIAC_EXTENDERS if 0 <= oversize_pct(item["diameter_mm"], m.contralateral_diameter_mm) <= ILIAC_OVERSIZE_MAX]
    aortic_ext_label = ", ".join(f"{item['diameter_mm']} mm" for item in extenders[:4]) if extenders else ""
    iliac_ext_label = ", ".join(f"{item['diameter_mm']} mm" for item in iliac_ext[:4]) if iliac_ext else ""
    notes = [
        "Komponenty oznaczone jako przybliżone należy potwierdzić w pełnym IFU Endurant.",
        f"Możliwe aortic extenders: {aortic_ext_label}" if extenders else "Brak oczywistego aortic extendera w przyjętej heurystyce.",
        f"Możliwe iliac extenders: {iliac_ext_label}" if iliac_ext else "Brak oczywistego iliac extendera w przyjętej heurystyce.",
    ]
    return Recommendation(
        manufacturer="Medtronic",
        family="Endurant II / IIs",
        status=status_from_flags(exact, bool(components)),
        score=score_recommendation(
            exact,
            warnings,
            partial_score=SCORE_BASE_HEURISTIC,
            min_score=SCORE_MIN_HEURISTIC,
            penalty_per_warning=HEURISTIC_PENALTY_PER_WARNING,
        ),
        warnings=tuple(warnings),
        components=tuple(components),
        notes=tuple(notes),
        source=DATA_SOURCES["medtronic"],
        alternatives={
            "main_body_options": body_candidates[:5],
            "contralateral_limb_options": limb_candidates[:5],
        },
    )
