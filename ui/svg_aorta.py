"""Dynamic SVG worksheet for aortic anatomy."""

from __future__ import annotations

import html

import streamlit as st

from domain.models import Measurements, Recommendation
from ui.forms import FIELD_BY_KEY, focus_options, format_focus_option


SVG_MARKERS = {
    "neck_diameter_mm": {"x": 347, "y": 154},
    "neck_length_mm": {"x": 476, "y": 168},
    "aortic_bifurcation_length_mm": {"x": 522, "y": 278},
    "neck_angle_deg": {"x": 246, "y": 132},
    "right_iliac_diameter_mm": {"x": 238, "y": 452},
    "right_iliac_length_mm": {"x": 184, "y": 526},
    "right_eia_diameter_mm": {"x": 126, "y": 626},
    "left_iliac_diameter_mm": {"x": 456, "y": 452},
    "left_iliac_length_mm": {"x": 520, "y": 526},
    "left_eia_diameter_mm": {"x": 578, "y": 626},
}


def render_focus_selector() -> str:
    st.radio(
        "Podświetl pomiar na schemacie",
        options=focus_options(),
        key="worksheet_focus",
        horizontal=True,
        format_func=format_focus_option,
    )
    return st.session_state["worksheet_focus"]


def _measurement_value(measurements: Measurements, key: str) -> str:
    value = getattr(measurements, key)
    if key == "neck_angle_deg":
        return f"{value:.0f}°"
    if "length" in key:
        return f"{value:.0f} mm"
    return f"{value:.1f} mm"


def _recommendation_overlay(rec: Recommendation | None) -> tuple[str, str, str]:
    if rec is None:
        return "", "", ""
    main_body = next((item for item in rec.components if item.component_type == "main_body"), None)
    contra = next((item for item in rec.components if item.side == "contralateral"), None)
    ipsi = next((item for item in rec.components if item.side == "ipsilateral" and item.component_type == "limb"), None)
    main_text = main_body.label if main_body else "Brak pewnego korpusu"
    contra_text = contra.label if contra else "Brak odnogi"
    ipsi_text = ipsi.label if ipsi else rec.family
    return main_text, contra_text, ipsi_text


def _label_box(x: int, y: int, title: str, value: str, active: bool) -> str:
    fill = "#fff7ed" if active else "#ffffff"
    stroke = "#f97316" if active else "#94a3b8"
    title_fill = "#9a3412" if active else "#334155"
    value_fill = "#111827"
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect width="96" height="46" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="12" y="18" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="700" fill="{title_fill}">{html.escape(title)}</text>'
        f'<text x="12" y="34" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="{value_fill}">{html.escape(value)}</text>'
        "</g>"
    )


def render_aorta_svg(measurements: Measurements, *, selected_key: str, top_recommendation: Recommendation | None) -> None:
    overlay_main, overlay_contra, overlay_ipsi = _recommendation_overlay(top_recommendation)
    selected = selected_key if selected_key in SVG_MARKERS else "neck_diameter_mm"

    boxes: list[str] = []
    connectors: list[str] = []
    for key, marker in SVG_MARKERS.items():
        field = FIELD_BY_KEY[key]
        active = key == selected
        stroke = "#f97316" if active else "#475569"
        stroke_width = "4" if active else "2.2"
        x = marker["x"]
        y = marker["y"]

        box_x = x + 18 if x < 360 else x - 114
        box_y = y - 24
        if key in {"right_iliac_length_mm", "right_eia_diameter_mm"}:
            box_x = 18
        if key in {"left_iliac_length_mm", "left_eia_diameter_mm"}:
            box_x = 588
        box_x = max(18, min(box_x, 646))
        box_y = max(66, min(box_y, 650))

        box_anchor_x = box_x if box_x > x else box_x + 96
        box_anchor_y = box_y + 23
        connectors.append(
            f'<path d="M {x} {y} L {box_anchor_x} {box_anchor_y}" fill="none" stroke="{stroke}" stroke-width="{stroke_width}" opacity="0.95"/>'
        )
        connectors.append(
            f'<circle cx="{x}" cy="{y}" r="9" fill="#ffffff" stroke="{stroke}" stroke-width="{stroke_width}" />'
        )
        boxes.append(_label_box(box_x, box_y, field.anatomy_code, _measurement_value(measurements, key), active))

    svg_code = f"""
    <svg viewBox="0 0 760 720" width="100%" height="700px" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#fffaf3"/>
                <stop offset="100%" stop-color="#f8fafc"/>
            </linearGradient>
            <linearGradient id="aortaCore" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#fca5a5"/>
                <stop offset="50%" stop-color="#d97766"/>
                <stop offset="100%" stop-color="#b91c1c"/>
            </linearGradient>
            <linearGradient id="stent" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#93c5fd"/>
                <stop offset="100%" stop-color="#1d4ed8"/>
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#bg)" rx="28"/>

        <text x="34" y="40" font-family="Helvetica, Arial, sans-serif" font-size="19" font-weight="700" fill="#111827">
            Schemat i formularz danych dla EVAR
        </text>
        <text x="34" y="64" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#475569">
            Wartości po prawej stronie są sprzężone z tym schematem i automatycznie przeliczają ranking urządzeń.
        </text>

        <path d="M 332 46
                 C 327 72, 327 92, 334 110
                 L 280 138
                 L 196 118
                 L 190 130
                 L 272 156
                 L 332 142
                 C 330 188, 296 208, 276 244
                 C 252 286, 250 352, 302 410
                 C 327 436, 338 464, 344 484
                 L 248 652
                 L 278 664
                 L 370 506
                 L 374 506
                 L 466 664
                 L 496 652
                 L 400 484
                 C 406 464, 417 436, 442 410
                 C 494 352, 492 286, 468 244
                 C 448 208, 414 188, 412 142
                 L 472 156
                 L 554 130
                 L 548 118
                 L 464 138
                 L 410 110
                 C 417 92, 417 72, 412 46 Z"
              fill="url(#aortaCore)" opacity="0.92" stroke="#7f1d1d" stroke-width="4"/>

        <path d="M 350 484 L 286 632 L 304 640 L 370 522 L 436 640 L 454 632 L 390 484 Z"
              fill="url(#stent)" opacity="0.78" stroke="#1d4ed8" stroke-width="4"/>

        <path d="M 346 506 L 284 406 L 262 450 L 304 618" fill="none" stroke="#1d4ed8" stroke-width="10" stroke-linecap="round"/>
        <path d="M 394 506 L 456 406 L 478 450 L 436 618" fill="none" stroke="#1d4ed8" stroke-width="10" stroke-linecap="round"/>

        <text x="66" y="126" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">Tętnice nerkowe</text>
        <text x="580" y="126" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#111827">Tętnice nerkowe</text>
        <text x="41" y="254" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">Aortic neck</text>
        <text x="36" y="276" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">diameter / length</text>
        <text x="546" y="364" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="#111827">Bifurkacja</text>
        <text x="30" y="420" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">Prawa wspólna</text>
        <text x="33" y="440" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">landing zone</text>
        <text x="595" y="420" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">Lewa wspólna</text>
        <text x="611" y="440" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">landing zone</text>
        <text x="28" y="656" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">Prawa EIA</text>
        <text x="613" y="656" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#111827">Lewa EIA</text>

        <line x1="305" y1="153" x2="389" y2="153" stroke="#111827" stroke-width="2.5"/>
        <line x1="311" y1="126" x2="311" y2="180" stroke="#111827" stroke-width="2.5"/>
        <line x1="383" y1="126" x2="383" y2="180" stroke="#111827" stroke-width="2.5"/>
        <line x1="445" y1="124" x2="445" y2="182" stroke="#111827" stroke-width="2.5"/>
        <line x1="474" y1="124" x2="474" y2="182" stroke="#111827" stroke-width="2.5"/>
        <line x1="460" y1="124" x2="460" y2="182" stroke="#111827" stroke-width="2.5"/>
        <line x1="517" y1="124" x2="517" y2="375" stroke="#111827" stroke-width="2.5"/>
        <line x1="500" y1="124" x2="534" y2="124" stroke="#111827" stroke-width="2.5"/>
        <line x1="500" y1="375" x2="534" y2="375" stroke="#111827" stroke-width="2.5"/>

        <line x1="284" y1="414" x2="225" y2="468" stroke="#111827" stroke-width="2.5"/>
        <line x1="258" y1="458" x2="182" y2="572" stroke="#111827" stroke-width="2.5"/>
        <line x1="270" y1="584" x2="150" y2="634" stroke="#111827" stroke-width="2.5"/>
        <line x1="455" y1="414" x2="513" y2="468" stroke="#111827" stroke-width="2.5"/>
        <line x1="481" y1="458" x2="556" y2="572" stroke="#111827" stroke-width="2.5"/>
        <line x1="469" y1="584" x2="589" y2="634" stroke="#111827" stroke-width="2.5"/>

        {''.join(connectors)}
        {''.join(boxes)}

        <g transform="translate(488,78)">
            <rect width="246" height="166" rx="18" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"/>
            <text x="16" y="28" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#0f172a">Najwyżej oceniona rekomendacja</text>
            <text x="16" y="54" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#334155">{html.escape(top_recommendation.manufacturer if top_recommendation else "Brak")}</text>
            <text x="16" y="74" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#475569">{html.escape(top_recommendation.family if top_recommendation else "")}</text>
            <text x="16" y="102" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="700" fill="#1d4ed8">Main body</text>
            <text x="16" y="119" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#1e293b">{html.escape(overlay_main)}</text>
            <text x="16" y="142" font-family="Helvetica, Arial, sans-serif" font-size="12" font-weight="700" fill="#1d4ed8">Contra limb</text>
            <text x="16" y="159" font-family="Helvetica, Arial, sans-serif" font-size="11" fill="#1e293b">{html.escape(overlay_contra)}</text>
        </g>
    </svg>
    """
    st.markdown(svg_code, unsafe_allow_html=True)
