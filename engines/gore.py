"""Gore Excluder recommendation engines."""

from __future__ import annotations

from typing import Any

from evar_data import (
    DATA_SOURCES,
    GORE_ACTIVE_CONTROL_MAIN_BODIES,
    GORE_ACTIVE_CONTROL_AORTIC_EXTENDERS,
    GORE_C3_AORTIC_EXTENDERS,
    GORE_C3_MAIN_BODIES,
    GORE_CONTRALATERAL_LEGS,
    GORE_ILIAC_EXTENDERS,
)
from domain.models import ComponentRecommendation, Measurements, Recommendation, WarningMessage
from engines.common import (
    build_access_warning,
    band_label,
    closest_midpoint_penalty,
    in_range,
    oversize_pct,
    profile_fr_from_item,
    score_recommendation,
    status_from_flags,
    make_warning,
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


def _gore_family_overlap_warning(family_label: str) -> str:
    if "Active Control" in family_label:
        return (
            "Gore Active Control: potwierdź overlap wg IFU. Załączony worksheet podaje minimum 2.2 cm lub 3.0 cm "
            "zależnie od konfiguracji korpusu i aortic extendera; aplikacja nie liczy tego automatycznie."
        )
    return "Gore C3: potwierdź overlap komponentów bezpośrednio w IFU; w tej wersji nie jest on liczony automatycznie."


def _gore_angulation_note(family_label: str) -> str:
    if "Active Control" in family_label:
        return "Gore Active Control: potwierdź IFU dla angulacji szyi. Materiały producenta dopuszczają do 90° przy szyi >= 10 mm."
    return "Gore C3: potwierdź IFU dla angulacji szyi. Materiały producenta dla standardowego EXCLUDER C3 wskazują do 60° przy szyi >= 15 mm."


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


def _gore_extenders_for(m: Measurements, *, aortic_extenders: list[dict[str, Any]]) -> list[str]:
    suggestions: list[str] = []
    iliac_matches = [
        item for item in GORE_ILIAC_EXTENDERS if in_range(m.contralateral_diameter_mm, item["iliac_range_mm"]) or in_range(m.ipsilateral_diameter_mm, item["iliac_range_mm"])
    ]
    aortic_matches = [item for item in aortic_extenders if in_range(m.neck_diameter_mm, item["aortic_range_mm"])]
    if aortic_matches:
        aortic_label = ", ".join(f"{item['catalogue']} ({item['diameter_mm']} mm/{item['length_mm']} mm)" for item in aortic_matches)
        suggestions.append(f"Aortic extender dostępny: {aortic_label}")
    if iliac_matches:
        iliac_label = ", ".join(f"{item['catalogue']} ({item['diameter_mm']} mm/{item['length_mm']} mm)" for item in iliac_matches)
        suggestions.append(f"Iliac extender dostępny: {iliac_label}")
    return suggestions


def recommend_gore_family(
    pool: list[dict[str, Any]],
    family_label: str,
    m: Measurements,
    *,
    source: str,
    aortic_extenders: list[dict[str, Any]],
) -> Recommendation:
    warnings: list[WarningMessage] = []
    body_candidates = _pick_gore_main_body(pool, m)
    main_body = next((item for item in body_candidates if item["overall_length_mm"] <= m.ipsilateral_length_mm), body_candidates[0] if body_candidates else None)
    if not body_candidates:
        warnings.append(make_warning("Brak głównego korpusu Gore dla kombinacji szyi i strony ipsilateralnej.", code="gore_no_main_body"))
    elif main_body and main_body["overall_length_mm"] > m.ipsilateral_length_mm:
        warnings.append(make_warning("Najbliższy korpus Gore jest dłuższy niż zadeklarowana długość strony ipsilateralnej.", code="gore_body_too_long"))

    contra_leg, all_legs = _pick_gore_leg(m)
    if not contra_leg:
        warnings.append(make_warning("Brak odnogi kontralateralnej Gore dla podanej średnicy biodrowej.", code="gore_no_contra_limb"))
    elif contra_leg["length_mm"] > m.contralateral_length_mm:
        warnings.append(make_warning("Najkrótsza odnoga kontralateralna Gore jest dłuższa niż zadeklarowana długość naczynia.", code="gore_limb_too_long"))

    exact = bool(main_body and contra_leg and main_body["overall_length_mm"] <= m.ipsilateral_length_mm and contra_leg["length_mm"] <= m.contralateral_length_mm)
    components: list[ComponentRecommendation] = []
    if main_body:
        neck_oversize = oversize_pct(main_body["aortic_diameter_mm"], m.neck_diameter_mm)
        main_body_profile = profile_fr_from_item(main_body)
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
                access_profile_fr=main_body_profile,
                required_access_diameter_mm=(main_body_profile / 3.0 + 1.0) if main_body_profile is not None else None,
            )
        )
        access_warning = build_access_warning(
            manufacturer="Gore",
            component_label="main body",
            side_label=m.ipsilateral_label,
            profile_fr=main_body_profile,
            eia_diameter_mm=m.ipsilateral_eia_diameter_mm,
        )
        if access_warning:
            warnings.append(access_warning)
    if contra_leg:
        contra_oversize = oversize_pct(contra_leg["graft_diameter_mm"], m.contralateral_diameter_mm)
        contra_profile = profile_fr_from_item(contra_leg)
        components.append(
            ComponentRecommendation(
                title=f"Odnoga kontralateralna ({m.contralateral_label})",
                component_type="limb",
                side="contralateral",
                label=f"{contra_leg['graft_diameter_mm']} mm | długość {contra_leg['length_mm']} mm",
                details=(
                    f"Średnica {m.contralateral_diameter_mm:.1f} mm mieści się w paśmie {band_label(contra_leg['iliac_range_mm'])}; "
                    f"oversizing landing zone {contra_oversize:.1f}%."
                ),
                official=True,
                catalogue=contra_leg.get("catalogue"),
                oversize_pct=contra_oversize,
                distal_diameter_mm=contra_leg["graft_diameter_mm"],
                covered_length_mm=contra_leg["length_mm"],
                access_profile_fr=contra_profile,
                required_access_diameter_mm=(contra_profile / 3.0 + 1.0) if contra_profile is not None else None,
            )
        )
        access_warning = build_access_warning(
            manufacturer="Gore",
            component_label="contralateral limb",
            side_label=m.contralateral_label,
            profile_fr=contra_profile,
            eia_diameter_mm=m.contralateral_eia_diameter_mm,
        )
        if access_warning:
            warnings.append(access_warning)
    if main_body and contra_leg:
        warnings.append(make_warning(_gore_family_overlap_warning(family_label), code="gore_overlap_check"))

    notes = [
        "Gore ma zintegrowaną gałąź ipsilateralną w korpusie głównym; aplikacja dobiera osobno tylko komponent kontralateralny.",
        _gore_angulation_note(family_label),
        *_gore_extenders_for(m, aortic_extenders=aortic_extenders),
    ]
    return Recommendation(
        manufacturer="Gore",
        family=family_label,
        status=status_from_flags(exact, bool(components)),
        score=score_recommendation(exact, warnings),
        warnings=tuple(warnings),
        components=tuple(components),
        notes=tuple(notes),
        source=source,
        alternatives={
            "main_body_options": body_candidates[:5],
            "contralateral_leg_options": all_legs[:5],
        },
    )


def recommend_gore_active_control(m: Measurements) -> Recommendation:
    return recommend_gore_family(
        GORE_ACTIVE_CONTROL_MAIN_BODIES,
        "EXCLUDER Conformable AAA (Active Control)",
        m,
        source=DATA_SOURCES["gore_active_control"],
        aortic_extenders=GORE_ACTIVE_CONTROL_AORTIC_EXTENDERS,
    )


def recommend_gore_c3(m: Measurements) -> Recommendation:
    return recommend_gore_family(
        GORE_C3_MAIN_BODIES,
        "EXCLUDER AAA with C3",
        m,
        source=DATA_SOURCES["gore_c3"],
        aortic_extenders=GORE_C3_AORTIC_EXTENDERS,
    )
