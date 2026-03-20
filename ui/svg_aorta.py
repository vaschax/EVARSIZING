"""Dynamic SVG worksheet for aortic anatomy."""

from __future__ import annotations

import html

import streamlit as st

from domain.models import Measurements, Recommendation
from ui.forms import FIELD_BY_KEY, focus_options, format_focus_option


SVG_MARKERS = {
    "neck_diameter_mm": {"x": 250, "y": 88},
    "neck_length_mm": {"x": 345, "y": 102},
    "aortic_bifurcation_length_mm": {"x": 348, "y": 176},
    "neck_angle_deg": {"x": 116, "y": 94},
    "right_iliac_diameter_mm": {"x": 92, "y": 388},
    "right_iliac_length_mm": {"x": 112, "y": 432},
    "left_iliac_diameter_mm": {"x": 548, "y": 388},
    "left_iliac_length_mm": {"x": 526, "y": 432},
}


def render_focus_selector() -> str:
    st.radio(
        "Focus worksheetu",
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


def render_aorta_svg(measurements: Measurements, *, selected_key: str, top_recommendation: Recommendation | None) -> None:
    overlay_main, overlay_contra, overlay_ipsi = _recommendation_overlay(top_recommendation)
    selected = selected_key if selected_key in SVG_MARKERS else "neck_diameter_mm"
    marker_fragments: list[str] = []
    label_fragments: list[str] = []
    for key, position in SVG_MARKERS.items():
        field = FIELD_BY_KEY[key]
        active = key == selected
        stroke = "#f97316" if active else "#0f172a"
        fill = "#ffedd5" if active else "#ffffff"
        label_fill = "#9a3412" if active else "#1e293b"
        marker_fragments.append(
            f'<circle cx="{position["x"]}" cy="{position["y"]}" r="10" fill="{fill}" stroke="{stroke}" stroke-width="3" />'
        )
        label_fragments.append(
            f'<text x="{position["x"]}" y="{position["y"] - 18}" font-family="Helvetica, Arial, sans-serif" font-size="13" text-anchor="middle" fill="{label_fill}">{field.anatomy_code}: {html.escape(_measurement_value(measurements, key))}</text>'
        )

    svg_code = f"""
    <svg viewBox="0 0 640 560" width="100%" height="520px" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="#fff7ed"/>
                <stop offset="100%" stop-color="#f8fafc"/>
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#bg)" rx="24"/>
        <text x="32" y="34" font-family="Helvetica, Arial, sans-serif" font-size="22" font-weight="700" fill="#111827">Interaktywny worksheet aorty</text>
        <text x="32" y="58" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#475569">Highlight pokazuje aktualnie edytowany pomiar.</text>

        <path d="M 260 70 L 260 150 Q 260 175 280 195 Q 300 215 320 240 L 382 400 L 344 414 L 292 270 Q 285 250 268 230 Q 245 205 225 180 Q 210 160 210 138 L 210 70 Z"
              fill="#bfdbfe" opacity="0.95" stroke="#2563eb" stroke-width="3"/>
        <path d="M 260 70 L 260 150 Q 260 175 240 195 Q 220 215 200 240 L 138 400 L 176 414 L 228 270 Q 235 250 252 230 Q 275 205 295 180 Q 310 160 310 138 L 310 70 Z"
              fill="#fecaca" opacity="0.70" stroke="#dc2626" stroke-width="3"/>

        <path d="M 246 64 Q 200 82 164 128" fill="none" stroke="#fb923c" stroke-width="5" stroke-linecap="round"/>

        <rect x="372" y="82" width="224" height="94" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
        <text x="388" y="108" font-family="Helvetica, Arial, sans-serif" font-size="14" font-weight="700" fill="#0f172a">Top recommendation</text>
        <text x="388" y="132" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#334155">{html.escape(top_recommendation.manufacturer if top_recommendation else "Brak")}</text>
        <text x="388" y="152" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#475569">{html.escape(top_recommendation.family if top_recommendation else "")}</text>

        <rect x="356" y="212" width="248" height="132" rx="18" fill="#ffffff" stroke="#cbd5e1"/>
        <text x="372" y="238" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">Overlay komponentów</text>
        <text x="372" y="264" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#1d4ed8">Main body: {html.escape(overlay_main)}</text>
        <text x="372" y="288" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#1d4ed8">Contra limb: {html.escape(overlay_contra)}</text>
        <text x="372" y="312" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#1d4ed8">Ipsi branch: {html.escape(overlay_ipsi)}</text>

        <text x="126" y="470" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#475569">Prawa biodrowa</text>
        <text x="466" y="470" font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#475569">Lewa biodrowa</text>

        {''.join(marker_fragments)}
        {''.join(label_fragments)}
    </svg>
    """
    st.markdown(svg_code, unsafe_allow_html=True)
