"""Gore Excluder recommendation engines."""

from __future__ import annotations

from typing import Any

from evar_data import (
    DATA_SOURCES,
    GORE_ACTIVE_CONTROL_MAIN_BODIES,
    GORE_AORTIC_EXTENDERS,
    GORE_C3_MAIN_BODIES,
    GORE_CONTRALATERAL_LEGS,
    GORE_ILIAC_EXTENDERS,
)
from domain.constants import GORE_REQUIRED_OVERLAP_LARGE_MM, GORE_REQUIRED_OVERLAP_SMALL_MM
from domain.models import ComponentRecommendation, Measurements, Recommendation
from engines.common import (
    band_label,
    closest_midpoint_penalty,
    in_range,
    oversize_pct,
    score_recommendation,
    status_from_flags,
)


def _pick_gore_main_body(pool: list[dict[str, Any]], m: Measurements) -> list[dict[str, Any]]:
    candidates = [
        item
        for item in pool
        if in_range(m.neck_diameter_mm, item["aortic_range_mm"]) and in_range(m.ipsilateral_diameter_mm, item["iliac_range_mm"])
    ]
    candidates.sort(
        key=lambda item: (
            abs(item["overall_length_mm"] - m.ipsilateral_length_mm),
            closest_midpoint_penalty(m.neck_diameter_mm, item["aortic_range_mm"]),
        )
    )
    return candidates


def _pick_gore_leg(m: Measurements) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    all_matches = [item for item in GORE_CONTRALATERAL_LEGS if in_range(m.contralateral_diameter_mm, item["iliac_range_mm"])]
    exact = [item for item in all_matches if item["length_mm"] <= m.contralateral_length_mm]
    exact.sort(key=lambda item: abs(item["length_mm"] - m.contralateral_length_mm))
    if exact:
        return exact[0], exact
    if not all_matches:
        return None, []
    all_matches.sort(key=lambda item: item["length_mm"])
    return all_matches[0], all_matches


def _gore_extenders_for(m: Measurements) -> list[str]:
    suggestions: list[str] = []
    iliac_matches = [
        item for item in GORE_ILIAC_EXTENDERS if in_range(m.contralateral_diameter_mm, item["iliac_range_mm"]) or in_range(m.ipsilateral_diameter_mm, item["iliac_range_mm"])
    ]
    aortic_matches = [item for item in GORE_AORTIC_EXTENDERS if in_range(m.neck_diameter_mm, item["aortic_range_mm"])]
    if aortic_matches:
        aortic_label = ", ".join(f"{item['diameter_mm']} mm/{item['length_mm']} mm" for item in aortic_matches)
        suggestions.append(f"Aortic extender dostępny: {aortic_label}")
    if iliac_matches:
        iliac_label = ", ".join(f"{item['diameter_mm']} mm/{item['length_mm']} mm" for item in iliac_matches)
        suggestions.append(f"Iliac extender dostępny: {iliac_label}")
    return suggestions


def recommend_gore_family(pool: list[dict[str, Any]], family_label: str, m: Measurements) -> Recommendation:
    warnings: list[str] = []
    body_candidates = _pick_gore_main_body(pool, m)
    main_body = next((item for item in body_candidates if item["overall_length_mm"] <= m.ipsilateral_length_mm), body_candidates[0] if body_candidates else None)
    if not body_candidates:
        warnings.append("Brak głównego korpusu Gore dla kombinacji szyi i strony ipsilateralnej.")
    elif main_body and main_body["overall_length_mm"] > m.ipsilateral_length_mm:
        warnings.append("Najbliższy korpus Gore jest dłuższy niż zadeklarowana długość strony ipsilateralnej.")

    contra_leg, all_legs = _pick_gore_leg(m)
    if not contra_leg:
        warnings.append("Brak odnogi kontralateralnej Gore dla podanej średnicy biodrowej.")
    elif contra_leg["length_mm"] > m.contralateral_length_mm:
        warnings.append("Najkrótsza odnoga kontralateralna Gore jest dłuższa niż zadeklarowana długość naczynia.")

    exact = bool(main_body and contra_leg and main_body["overall_length_mm"] <= m.ipsilateral_length_mm and contra_leg["length_mm"] <= m.contralateral_length_mm)
    components: list[ComponentRecommendation] = []
    if main_body:
        neck_oversize = oversize_pct(main_body["aortic_diameter_mm"], m.neck_diameter_mm)
        components.append(
            ComponentRecommendation(
                title=f"Trunk + ipsilateral leg ({m.ipsilateral_label})",
                component_type="main_body",
                side="ipsilateral",
                label=f"{main_body['aortic_diameter_mm']} / {main_body['iliac_diameter_mm']} mm | długość {main_body['overall_length_mm']} mm",
                details=(
                    f"Szyja {m.neck_diameter_mm:.1f} mm mieści się w paśmie {band_label(main_body['aortic_range_mm'])}; "
                    f"biodrowa ipsilateralna {m.ipsilateral_diameter_mm:.1f} mm w paśmie {band_label(main_body['iliac_range_mm'])}; "
                    f"oversizing szyi {neck_oversize:.1f}%."
                ),
                official=True,
                catalogue=main_body.get("catalogue"),
                oversize_pct=neck_oversize,
                proximal_diameter_mm=main_body["aortic_diameter_mm"],
                distal_diameter_mm=main_body["iliac_diameter_mm"],
                covered_length_mm=main_body["overall_length_mm"],
            )
        )
    if contra_leg:
        contra_oversize = oversize_pct(contra_leg["graft_diameter_mm"], m.contralateral_diameter_mm)
        min_overlap_mm = GORE_REQUIRED_OVERLAP_LARGE_MM if contra_leg["graft_diameter_mm"] >= 23 else GORE_REQUIRED_OVERLAP_SMALL_MM
        components.append(
            ComponentRecommendation(
                title=f"Odnoga kontralateralna ({m.contralateral_label})",
                component_type="limb",
                side="contralateral",
                label=f"{contra_leg['graft_diameter_mm']} mm | długość {contra_leg['length_mm']} mm",
                details=(
                    f"Średnica {m.contralateral_diameter_mm:.1f} mm mieści się w paśmie {band_label(contra_leg['iliac_range_mm'])}; "
                    f"oversizing landing zone {contra_oversize:.1f}%; wymagany overlap wg uproszczenia >= {min_overlap_mm:.0f} mm."
                ),
                official=True,
                catalogue=contra_leg.get("catalogue"),
                oversize_pct=contra_oversize,
                required_overlap_mm=min_overlap_mm,
                distal_diameter_mm=contra_leg["graft_diameter_mm"],
                covered_length_mm=contra_leg["length_mm"],
            )
        )
        warnings.append(
            f"Gore: potwierdź overlap między korpusem a odnogą. W tej wersji przyjmuję próg orientacyjny >= {min_overlap_mm:.0f} mm zależnie od średnicy komponentu."
        )

    notes = [
        "Gore ma zintegrowaną gałąź ipsilateralną w korpusie głównym; aplikacja dobiera osobno tylko komponent kontralateralny.",
        *_gore_extenders_for(m),
    ]
    return Recommendation(
        manufacturer="Gore",
        family=family_label,
        status=status_from_flags(exact, bool(components)),
        score=score_recommendation(exact, len(warnings)),
        warnings=tuple(warnings),
        components=tuple(components),
        notes=tuple(notes),
        source=DATA_SOURCES["gore"],
        alternatives={
            "main_body_options": body_candidates[:5],
            "contralateral_leg_options": all_legs[:5],
        },
    )


def recommend_gore_active_control(m: Measurements) -> Recommendation:
    return recommend_gore_family(GORE_ACTIVE_CONTROL_MAIN_BODIES, "EXCLUDER Conformable AAA (Active Control)", m)


def recommend_gore_c3(m: Measurements) -> Recommendation:
    return recommend_gore_family(GORE_C3_MAIN_BODIES, "EXCLUDER AAA with C3", m)
