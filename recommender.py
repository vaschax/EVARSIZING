"""Recommendation logic for the EVAR planning prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from evar_data import (
    COOK_CONTRALATERAL_LENGTHS,
    COOK_IPSILATERAL_LENGTHS,
    COOK_LEG_DIAMETERS,
    COOK_MAIN_BODY_DIAMETERS,
    COOK_MAIN_BODY_LENGTHS,
    DATA_SOURCES,
    GORE_ACTIVE_CONTROL_MAIN_BODIES,
    GORE_AORTIC_EXTENDERS,
    GORE_C3_MAIN_BODIES,
    GORE_CONTRALATERAL_LEGS,
    GORE_ILIAC_EXTENDERS,
    MEDTRONIC_AORTIC_EXTENDERS,
    MEDTRONIC_BIFURCATIONS,
    MEDTRONIC_ILIAC_EXTENDERS,
    MEDTRONIC_LIMBS,
    MEDTRONIC_SHORT_BODIES,
)


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


def in_range(value: float, band: tuple[float, float]) -> bool:
    return band[0] <= value <= band[1]


def band_label(band: tuple[float, float]) -> str:
    if band[0] == band[1]:
        return f"{band[0]:g} mm"
    return f"{band[0]:g}-{band[1]:g} mm"


def oversize_pct(device_mm: float, vessel_mm: float) -> float:
    return ((device_mm / vessel_mm) - 1.0) * 100.0


def closest_midpoint_penalty(value: float, band: tuple[float, float]) -> float:
    midpoint = (band[0] + band[1]) / 2
    return abs(value - midpoint)


def status_from_flags(exact: bool, borderline: bool) -> str:
    if exact and not borderline:
        return "Dopasowanie"
    if exact or borderline:
        return "Graniczne"
    return "Brak dopasowania"


def build_global_warnings(m: Measurements) -> list[str]:
    warnings: list[str] = []
    if m.neck_length_mm < 10:
        warnings.append("Hostile anatomy: długość szyi < 10 mm. Standardowy EVAR może być niewystarczający i może wymagać FEVAR/ChEVAR.")
    elif m.neck_length_mm < 15:
        warnings.append("Krótka szyja aorty (< 15 mm) zwiększa ryzyko i zwykle wymaga bardzo ostrożnej kwalifikacji.")
    if m.neck_angle_deg >= 60:
        warnings.append("Znaczna angulacja szyi (>= 60°) wymaga weryfikacji IFU i doświadczenia operatora.")
    if min(m.right_iliac_diameter_mm, m.left_iliac_diameter_mm) < 8:
        warnings.append("Jedna z tętnic biodrowych ma średnicę < 8 mm, co może oznaczać trudny dostęp i ryzyko okluzji.")
    if m.neck_diameter_mm > 32:
        warnings.append("Hostile anatomy: szyja > 32 mm wykracza poza typowe wskazania klasycznego infrarenal EVAR i może wymagać fenestracji/chimney.")
    if m.neck_diameter_mm < 16 or m.neck_diameter_mm > 32:
        warnings.append("Średnica szyi poza zakresem typowych standardowych systemów infrarenalnych z załączonych materiałów.")
    return warnings


def overlap_range_from_length_row(length_row: dict[str, Any]) -> tuple[float, float]:
    min_overlap = length_row["total_length_mm"] - length_row["vessel_length_mm"][1]
    max_overlap = length_row["total_length_mm"] - length_row["vessel_length_mm"][0]
    return min_overlap, max_overlap


def recommend_cook(m: Measurements) -> dict[str, Any]:
    warnings: list[str] = []
    main_body_diameter = next((item for item in COOK_MAIN_BODY_DIAMETERS if in_range(m.neck_diameter_mm, item["neck_range_mm"])), None)
    main_body_length = next((item for item in COOK_MAIN_BODY_LENGTHS if in_range(m.neck_length_mm, item["neck_length_range_mm"])), None)

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
        warnings.append("Cook Zenith Alpha: brak głównego korpusu dla podanej średnicy szyi D1.")
    if not main_body_length:
        warnings.append("Cook Zenith Alpha: długość L1 poza zakresem worksheet (75-142 mm).")
    if not contra_diameter or not contra_length:
        warnings.append(f"Cook Zenith Alpha: brak pewnego doboru odnogi kontralateralnej dla strony {m.contralateral_label.lower()}.")
    if not ipsi_diameter or not ipsi_length:
        warnings.append(f"Cook Zenith Alpha: brak pewnego doboru odnogi ipsilateralnej dla strony {m.ipsilateral_label.lower()}.")

    exact = all([main_body_diameter, main_body_length, contra_diameter, contra_length, ipsi_diameter, ipsi_length])
    components: list[dict[str, Any]] = []

    if main_body_diameter and main_body_length:
        neck_oversize = oversize_pct(main_body_diameter["graft_diameter_mm"], m.neck_diameter_mm)
        components.append(
            {
                "component": "Main body",
                "label": f"{main_body_diameter['graft_diameter_mm']} mm | CL {main_body_length['contralateral_length_mm']} mm | IL {main_body_length['ipsilateral_length_mm']} mm",
                "details": f"D1 {m.neck_diameter_mm:.1f} mm w paśmie {band_label(main_body_diameter['neck_range_mm'])}; L1 {m.neck_length_mm:.1f} mm w paśmie {band_label(main_body_length['neck_length_range_mm'])}; oversizing szyi {neck_oversize:.1f}%.",
                "official": True,
                "oversize_pct": neck_oversize,
            }
        )
    if contra_diameter and contra_length:
        contra_oversize = oversize_pct(contra_diameter["graft_diameter_mm"], m.contralateral_diameter_mm)
        overlap_min, overlap_max = overlap_range_from_length_row(contra_length)
        components.append(
            {
                "component": f"Odnogа kontralateralna ({m.contralateral_label})",
                "label": f"{contra_diameter['graft_diameter_mm']} mm | etykieta {contra_length['label_length_mm']} mm | całkowita {contra_length['total_length_mm']} mm",
                "details": f"Średnica {m.contralateral_diameter_mm:.1f} mm w paśmie {band_label(contra_diameter['iliac_range_mm'])}; długość naczynia {m.contralateral_length_mm:.1f} mm w paśmie {band_label(contra_length['vessel_length_mm'])}; oversizing landing zone {contra_oversize:.1f}%; przewidywana zakładka ~ {overlap_min:.0f}-{overlap_max:.0f} mm.",
                "official": True,
                "oversize_pct": contra_oversize,
                "overlap_range_mm": (overlap_min, overlap_max),
            }
        )
    if ipsi_diameter and ipsi_length:
        ipsi_oversize = oversize_pct(ipsi_diameter["graft_diameter_mm"], m.ipsilateral_diameter_mm)
        overlap_min, overlap_max = overlap_range_from_length_row(ipsi_length)
        components.append(
            {
                "component": f"Odnogа ipsilateralna ({m.ipsilateral_label})",
                "label": f"{ipsi_diameter['graft_diameter_mm']} mm | etykieta {ipsi_length['label_length_mm']} mm | całkowita {ipsi_length['total_length_mm']} mm",
                "details": f"Średnica {m.ipsilateral_diameter_mm:.1f} mm w paśmie {band_label(ipsi_diameter['iliac_range_mm'])}; długość naczynia {m.ipsilateral_length_mm:.1f} mm w paśmie {band_label(ipsi_length['vessel_length_mm'])}; oversizing landing zone {ipsi_oversize:.1f}%; przewidywana zakładka ~ {overlap_min:.0f}-{overlap_max:.0f} mm.",
                "official": True,
                "oversize_pct": ipsi_oversize,
                "overlap_range_mm": (overlap_min, overlap_max),
            }
        )

    score = 94 if exact else 55 - len(warnings) * 3
    return {
        "manufacturer": "Cook",
        "family": "Zenith Alpha",
        "status": status_from_flags(exact, bool(components)),
        "score": max(score, 15),
        "warnings": warnings,
        "components": components,
        "notes": [
            "Reguły oparte bezpośrednio o worksheet Zenith Alpha.",
            "Cook jako jedyny z załączonych materiałów daje prostą mapę D1/L1 oraz D2/D3/L2/L3.",
        ],
        "source": DATA_SOURCES["cook"],
    }


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
    iliac_matches = [item for item in GORE_ILIAC_EXTENDERS if in_range(m.contralateral_diameter_mm, item["iliac_range_mm"]) or in_range(m.ipsilateral_diameter_mm, item["iliac_range_mm"])]
    aortic_matches = [item for item in GORE_AORTIC_EXTENDERS if in_range(m.neck_diameter_mm, item["aortic_range_mm"])]
    if aortic_matches:
        aortic_label = ", ".join(f"{item['diameter_mm']} mm/{item['length_mm']} mm" for item in aortic_matches)
        suggestions.append(f"Aortic extender dostępny: {aortic_label}")
    if iliac_matches:
        iliac_label = ", ".join(f"{item['diameter_mm']} mm/{item['length_mm']} mm" for item in iliac_matches)
        suggestions.append(f"Iliac extender dostępny: {iliac_label}")
    return suggestions


def recommend_gore_family(pool: list[dict[str, Any]], family_label: str, m: Measurements) -> dict[str, Any]:
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
    components: list[dict[str, Any]] = []
    if main_body:
        neck_oversize = oversize_pct(main_body["aortic_diameter_mm"], m.neck_diameter_mm)
        components.append(
            {
                "component": f"Trunk + ipsilateral leg ({m.ipsilateral_label})",
                "label": f"{main_body['aortic_diameter_mm']} / {main_body['iliac_diameter_mm']} mm | długość {main_body['overall_length_mm']} mm",
                "details": f"Szyja {m.neck_diameter_mm:.1f} mm mieści się w paśmie {band_label(main_body['aortic_range_mm'])}; biodrowa ipsilateralna {m.ipsilateral_diameter_mm:.1f} mm w paśmie {band_label(main_body['iliac_range_mm'])}; oversizing szyi {neck_oversize:.1f}%.",
                "official": True,
                "catalogue": main_body.get("catalogue"),
                "oversize_pct": neck_oversize,
            }
        )
    if contra_leg:
        contra_oversize = oversize_pct(contra_leg["graft_diameter_mm"], m.contralateral_diameter_mm)
        min_overlap_mm = 22 if contra_leg["graft_diameter_mm"] >= 23 else 16
        components.append(
            {
                "component": f"Odnogа kontralateralna ({m.contralateral_label})",
                "label": f"{contra_leg['graft_diameter_mm']} mm | długość {contra_leg['length_mm']} mm",
                "details": f"Średnica {m.contralateral_diameter_mm:.1f} mm mieści się w paśmie {band_label(contra_leg['iliac_range_mm'])}; oversizing landing zone {contra_oversize:.1f}%; wymagany overlap wg uproszczenia >= {min_overlap_mm} mm.",
                "official": True,
                "catalogue": contra_leg.get("catalogue"),
                "oversize_pct": contra_oversize,
                "required_overlap_mm": min_overlap_mm,
            }
        )
        warnings.append(
            f"Gore: potwierdź overlap między korpusem a odnogą. W tej wersji przyjmuję próg orientacyjny >= {min_overlap_mm} mm zależnie od średnicy komponentu."
        )

    notes = [
        "Gore ma zintegrowaną gałąź ipsilateralną w korpusie głównym; aplikacja dobiera osobno tylko komponent kontralateralny.",
        *_gore_extenders_for(m),
    ]
    score = 92 if exact else 62 - len(warnings) * 3
    return {
        "manufacturer": "Gore",
        "family": family_label,
        "status": status_from_flags(exact, bool(components)),
        "score": max(score, 15),
        "warnings": warnings,
        "components": components,
        "notes": notes,
        "source": DATA_SOURCES["gore"],
        "alternatives": {
            "main_body_options": body_candidates[:5],
            "contralateral_leg_options": all_legs[:5],
        },
    }


def _pick_medtronic_body(pool: list[dict[str, Any]], m: Measurements) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in pool:
        neck_oversize = oversize_pct(item["proximal_diameter_mm"], m.neck_diameter_mm)
        iliac_oversize = oversize_pct(item["distal_diameter_mm"], m.ipsilateral_diameter_mm)
        if 10 <= neck_oversize <= 20 and 0 <= iliac_oversize <= 25:
            candidate = dict(item)
            candidate["neck_oversize_pct"] = neck_oversize
            candidate["iliac_oversize_pct"] = iliac_oversize
            out.append(candidate)
    out.sort(key=lambda item: (abs(item["covered_length_mm"] - m.ipsilateral_length_mm), abs(item["neck_oversize_pct"] - 15)))
    return out


def _pick_medtronic_limb(m: Measurements) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in MEDTRONIC_LIMBS:
        iliac_oversize = oversize_pct(item["distal_diameter_mm"], m.contralateral_diameter_mm)
        if 0 <= iliac_oversize <= 25:
            candidate = dict(item)
            candidate["iliac_oversize_pct"] = iliac_oversize
            out.append(candidate)
    out.sort(key=lambda item: (abs(item["covered_length_mm"] - m.contralateral_length_mm), abs(item["iliac_oversize_pct"] - 12)))
    return out


def recommend_medtronic(m: Measurements) -> dict[str, Any]:
    warnings: list[str] = [
        "Dla Medtronic załączony PDF podaje tabele rozmiarów urządzenia, ale nie podaje wprost zakresów naczyń. Dobór w tej aplikacji opiera się na heurystyce oversizingu 10-20% dla szyi i 0-25% dla dystalnego landing zone.",
    ]
    body_candidates = _pick_medtronic_body(MEDTRONIC_SHORT_BODIES + MEDTRONIC_BIFURCATIONS, m)
    main_body = next((item for item in body_candidates if item["covered_length_mm"] <= m.ipsilateral_length_mm), body_candidates[0] if body_candidates else None)

    limb_candidates = _pick_medtronic_limb(m)
    contra_limb = next((item for item in limb_candidates if item["covered_length_mm"] <= m.contralateral_length_mm), limb_candidates[0] if limb_candidates else None)

    if not main_body:
        warnings.append("Brak sensownego korpusu Endurant dla zadanych wymiarów przy przyjętej heurystyce.")
    elif main_body["covered_length_mm"] > m.ipsilateral_length_mm:
        warnings.append("Najbliższy korpus Endurant jest dłuższy niż długość strony ipsilateralnej.")
    if not contra_limb:
        warnings.append("Brak sensownej odnogi Endurant dla strony kontralateralnej przy przyjętej heurystyce.")
    elif contra_limb["covered_length_mm"] > m.contralateral_length_mm:
        warnings.append("Najkrótsza odnoga Endurant jest dłuższa niż długość strony kontralateralnej.")

    exact = bool(
        main_body
        and contra_limb
        and main_body["covered_length_mm"] <= m.ipsilateral_length_mm
        and contra_limb["covered_length_mm"] <= m.contralateral_length_mm
    )

    components: list[dict[str, Any]] = []
    if main_body:
        components.append(
            {
                "component": f"Korpus główny ({main_body['family']})",
                "label": f"{main_body['proximal_diameter_mm']} / {main_body['distal_diameter_mm']} mm | długość {main_body['covered_length_mm']} mm",
                "details": f"Oversizing szyi ~ {main_body['neck_oversize_pct']:.1f}% i dystalny landing ~ {main_body['iliac_oversize_pct']:.1f}% względem strony {m.ipsilateral_label.lower()}.",
                "official": False,
                "oversize_pct": main_body["neck_oversize_pct"],
            }
        )
    if contra_limb:
        components.append(
            {
                "component": f"Odnogа kontralateralna ({m.contralateral_label})",
                "label": f"{contra_limb['distal_diameter_mm']} mm | długość {contra_limb['covered_length_mm']} mm",
                "details": f"Oversizing landing zone ~ {contra_limb['iliac_oversize_pct']:.1f}%.",
                "official": False,
                "oversize_pct": contra_limb["iliac_oversize_pct"],
            }
        )
    if main_body and contra_limb:
        warnings.append("Medtronic: potwierdź w IFU, że połączone komponenty zapewniają minimum 30 mm zakładki (overlap).")

    extenders = [item for item in MEDTRONIC_AORTIC_EXTENDERS if 10 <= oversize_pct(item["diameter_mm"], m.neck_diameter_mm) <= 20]
    iliac_ext = [item for item in MEDTRONIC_ILIAC_EXTENDERS if 0 <= oversize_pct(item["diameter_mm"], m.contralateral_diameter_mm) <= 25]
    aortic_ext_label = ", ".join(f"{item['diameter_mm']} mm" for item in extenders[:4]) if extenders else ""
    iliac_ext_label = ", ".join(f"{item['diameter_mm']} mm" for item in iliac_ext[:4]) if iliac_ext else ""
    notes = [
        "Komponenty oznaczone jako przybliżone należy potwierdzić w pełnym IFU Endurant.",
        f"Możliwe aortic extenders: {aortic_ext_label}" if extenders else "Brak oczywistego aortic extendera w przyjętej heurystyce.",
        f"Możliwe iliac extenders: {iliac_ext_label}" if iliac_ext else "Brak oczywistego iliac extendera w przyjętej heurystyce.",
    ]
    score = 78 if exact else 44 - len(warnings) * 2
    return {
        "manufacturer": "Medtronic",
        "family": "Endurant II / IIs",
        "status": status_from_flags(exact, bool(components)),
        "score": max(score, 10),
        "warnings": warnings,
        "components": components,
        "notes": notes,
        "source": DATA_SOURCES["medtronic"],
        "alternatives": {
            "main_body_options": body_candidates[:5],
            "contralateral_limb_options": limb_candidates[:5],
        },
    }


def build_recommendations(m: Measurements) -> dict[str, Any]:
    gore_active = recommend_gore_family(GORE_ACTIVE_CONTROL_MAIN_BODIES, "EXCLUDER Conformable AAA (Active Control)", m)
    gore_c3 = recommend_gore_family(GORE_C3_MAIN_BODIES, "EXCLUDER AAA with C3", m)
    cook = recommend_cook(m)
    medtronic = recommend_medtronic(m)

    recommendations = sorted([cook, gore_active, gore_c3, medtronic], key=lambda item: item["score"], reverse=True)
    return {
        "warnings": build_global_warnings(m),
        "recommendations": recommendations,
        "sources": DATA_SOURCES,
    }
