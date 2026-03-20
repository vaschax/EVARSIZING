"""Cook Zenith Alpha recommendation engine."""

from __future__ import annotations

from evar_data import (
    COOK_CONTRALATERAL_LENGTHS,
    COOK_IPSILATERAL_LENGTHS,
    COOK_LEG_DIAMETERS,
    COOK_MAIN_BODY_DIAMETERS,
    COOK_MAIN_BODY_LENGTHS,
    DATA_SOURCES,
)
from domain.models import ComponentRecommendation, Measurements, Recommendation, WarningMessage
from engines.common import band_label, in_range, overlap_range_from_length_row, oversize_pct, score_recommendation, status_from_flags, make_warning


def _cook_main_body_access_requirement_mm(graft_diameter_mm: float) -> float | None:
    if 22 <= graft_diameter_mm <= 32:
        return 6.0
    if graft_diameter_mm == 36:
        return 6.5
    return None


def recommend_cook(m: Measurements) -> Recommendation:
    warnings: list[WarningMessage] = []
    main_body_diameter = next((item for item in COOK_MAIN_BODY_DIAMETERS if in_range(m.neck_diameter_mm, item["neck_range_mm"])), None)
    main_body_length = next((item for item in COOK_MAIN_BODY_LENGTHS if in_range(m.aortic_bifurcation_length_mm, item["aortic_length_range_mm"])), None)

    contra_diameter = next((item for item in COOK_LEG_DIAMETERS if in_range(m.contralateral_diameter_mm, item["iliac_range_mm"])), None)
    ipsi_diameter = next((item for item in COOK_LEG_DIAMETERS if in_range(m.ipsilateral_diameter_mm, item["iliac_range_mm"])), None)

    contra_length = next(
        (
            item
            for item in COOK_CONTRALATERAL_LENGTHS
            if in_range(m.contralateral_length_mm, item["vessel_length_mm"])
            and in_range(contra_diameter["graft_diameter_mm"], item["diameter_range_mm"])
        ),
        None,
    ) if contra_diameter else None

    ipsi_length = next(
        (
            item
            for item in COOK_IPSILATERAL_LENGTHS
            if in_range(m.ipsilateral_length_mm, item["vessel_length_mm"])
            and in_range(ipsi_diameter["graft_diameter_mm"], item["diameter_range_mm"])
        ),
        None,
    ) if ipsi_diameter else None

    if not main_body_diameter:
        warnings.append(make_warning("Cook Zenith Alpha: brak głównego korpusu dla podanej średnicy szyi D1.", code="cook_no_main_body"))
    if not main_body_length:
        warnings.append(
            make_warning(
                "Cook Zenith Alpha: odległość od nerkowych do rozwidlenia aorty poza zakresem worksheetu dla doboru main body (75-142 mm).",
                code="cook_length_out_of_range",
            )
        )
    if not contra_diameter or not contra_length:
        warnings.append(make_warning(f"Cook Zenith Alpha: brak pewnego doboru odnogi kontralateralnej dla strony {m.contralateral_label.lower()}.", code="cook_no_contra_limb"))
    if not ipsi_diameter or not ipsi_length:
        warnings.append(make_warning(f"Cook Zenith Alpha: brak pewnego doboru odnogi ipsilateralnej dla strony {m.ipsilateral_label.lower()}.", code="cook_no_ipsi_limb"))

    exact = all([main_body_diameter, main_body_length, contra_diameter, contra_length, ipsi_diameter, ipsi_length])
    components: list[ComponentRecommendation] = []

    if main_body_diameter and main_body_length:
        neck_oversize = oversize_pct(main_body_diameter["graft_diameter_mm"], m.neck_diameter_mm)
        access_requirement_mm = _cook_main_body_access_requirement_mm(main_body_diameter["graft_diameter_mm"])
        components.append(
            ComponentRecommendation(
                title="Main body",
                component_type="main_body",
                side=None,
                label=f"{main_body_diameter['graft_diameter_mm']} mm | CL {main_body_length['contralateral_length_mm']} mm | IL {main_body_length['ipsilateral_length_mm']} mm",
                details=(
                    f"D1 {m.neck_diameter_mm:.1f} mm w paśmie {band_label(main_body_diameter['neck_range_mm'])}; "
                    f"renal-to-bifurcation {m.aortic_bifurcation_length_mm:.1f} mm w paśmie {band_label(main_body_length['aortic_length_range_mm'])}; "
                    f"oversizing szyi {neck_oversize:.1f}%."
                ),
                official=True,
                oversize_pct=neck_oversize,
                proximal_diameter_mm=main_body_diameter["graft_diameter_mm"],
                covered_length_mm=main_body_length["ipsilateral_length_mm"],
                required_access_diameter_mm=access_requirement_mm,
            )
        )
        if access_requirement_mm is not None and m.ipsilateral_eia_diameter_mm < access_requirement_mm:
            warnings.append(
                make_warning(
                    (
                        f"CRITICAL ACCESS WARNING: Cook main body {main_body_diameter['graft_diameter_mm']:.0f} mm wymaga introducera "
                        f"~ {access_requirement_mm:.1f} mm OD, ale strona {m.ipsilateral_label.lower()} ma EIA {m.ipsilateral_eia_diameter_mm:.1f} mm. "
                        "Rozważ iliac conduit lub inny system."
                    ),
                    "critical",
                    code="cook_access_vessel_too_small",
                )
            )
    if contra_diameter and contra_length:
        contra_oversize = oversize_pct(contra_diameter["graft_diameter_mm"], m.contralateral_diameter_mm)
        overlap_min, overlap_max = overlap_range_from_length_row(contra_length)
        components.append(
            ComponentRecommendation(
                title=f"Odnoga kontralateralna ({m.contralateral_label})",
                component_type="limb",
                side="contralateral",
                label=f"{contra_diameter['graft_diameter_mm']} mm | etykieta {contra_length['label_length_mm']} mm | całkowita {contra_length['total_length_mm']} mm",
                details=(
                    f"Średnica {m.contralateral_diameter_mm:.1f} mm w paśmie {band_label(contra_diameter['iliac_range_mm'])}; "
                    f"długość naczynia {m.contralateral_length_mm:.1f} mm w paśmie {band_label(contra_length['vessel_length_mm'])}; "
                    f"oversizing landing zone {contra_oversize:.1f}%; przewidywana zakładka ~ {overlap_min:.0f}-{overlap_max:.0f} mm."
                ),
                official=True,
                oversize_pct=contra_oversize,
                predicted_overlap_range_mm=(overlap_min, overlap_max),
                distal_diameter_mm=contra_diameter["graft_diameter_mm"],
                covered_length_mm=contra_length["total_length_mm"],
            )
        )
    if ipsi_diameter and ipsi_length:
        ipsi_oversize = oversize_pct(ipsi_diameter["graft_diameter_mm"], m.ipsilateral_diameter_mm)
        overlap_min, overlap_max = overlap_range_from_length_row(ipsi_length)
        components.append(
            ComponentRecommendation(
                title=f"Odnoga ipsilateralna ({m.ipsilateral_label})",
                component_type="limb",
                side="ipsilateral",
                label=f"{ipsi_diameter['graft_diameter_mm']} mm | etykieta {ipsi_length['label_length_mm']} mm | całkowita {ipsi_length['total_length_mm']} mm",
                details=(
                    f"Średnica {m.ipsilateral_diameter_mm:.1f} mm w paśmie {band_label(ipsi_diameter['iliac_range_mm'])}; "
                    f"długość naczynia {m.ipsilateral_length_mm:.1f} mm w paśmie {band_label(ipsi_length['vessel_length_mm'])}; "
                    f"oversizing landing zone {ipsi_oversize:.1f}%; przewidywana zakładka ~ {overlap_min:.0f}-{overlap_max:.0f} mm."
                ),
                official=True,
                oversize_pct=ipsi_oversize,
                predicted_overlap_range_mm=(overlap_min, overlap_max),
                distal_diameter_mm=ipsi_diameter["graft_diameter_mm"],
                covered_length_mm=ipsi_length["total_length_mm"],
            )
        )

    return Recommendation(
        manufacturer="Cook",
        family="Zenith Alpha",
        status=status_from_flags(exact, bool(components)),
        score=score_recommendation(exact, warnings),
        warnings=tuple(warnings),
        components=tuple(components),
        notes=(
            "Reguły oparte bezpośrednio o worksheet Zenith Alpha.",
            "Dla Cook długość korpusu głównego jest dobierana z odległości nerki -> rozwidlenie aorty, a nie z długości szyi proksymalnej.",
            "Worksheet Cook podaje też profil dostępu: 6.0 mm OD dla graftów 22-32 mm oraz 6.5 mm OD dla 36 mm.",
        ),
        source=DATA_SOURCES["cook"],
    )
