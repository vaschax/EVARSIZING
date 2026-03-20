"""Worksheet image renderer backed by the user's static EVAR schema."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from domain.models import Measurements, Recommendation
from ui.forms import FIELD_BY_KEY, focus_options, format_focus_option


SCHEMA_IMAGE_PATH = Path(__file__).resolve().parents[1] / "assets" / "evar-schema.png"
OVERLAY_FIELDS = {
    "neck_diameter_mm": {"left_pct": 50.8, "top_pct": 16.6, "width_pct": 10.8, "height_pct": 8.0},
    "neck_length_mm": {"left_pct": 71.5, "top_pct": 24.1, "width_pct": 10.8, "height_pct": 8.0},
    "aortic_bifurcation_length_mm": {"left_pct": 71.5, "top_pct": 38.2, "width_pct": 11.2, "height_pct": 8.2},
    "right_iliac_diameter_mm": {"left_pct": 27.8, "top_pct": 58.4, "width_pct": 10.6, "height_pct": 8.0},
    "left_iliac_diameter_mm": {"left_pct": 74.8, "top_pct": 58.4, "width_pct": 10.6, "height_pct": 8.0},
    "right_iliac_length_mm": {"left_pct": 23.3, "top_pct": 70.4, "width_pct": 10.6, "height_pct": 8.0},
    "left_iliac_length_mm": {"left_pct": 78.3, "top_pct": 70.4, "width_pct": 10.6, "height_pct": 8.0},
    "right_eia_diameter_mm": {"left_pct": 18.4, "top_pct": 82.1, "width_pct": 11.2, "height_pct": 8.2},
    "left_eia_diameter_mm": {"left_pct": 84.6, "top_pct": 82.1, "width_pct": 11.2, "height_pct": 8.2},
}


def render_focus_selector() -> str:
    st.radio(
        "Wybierz aktywny pomiar",
        options=focus_options(),
        key="worksheet_focus",
        horizontal=True,
        format_func=format_focus_option,
    )
    st.caption("Możesz też kliknąć odpowiednie pole bezpośrednio na schemacie.")
    return st.session_state["worksheet_focus"]


def _measurement_value(measurements: Measurements, key: str) -> str:
    value = getattr(measurements, key)
    if key == "neck_angle_deg":
        return f"{value:.0f}°"
    if "length" in key:
        return f"{value:.0f} mm"
    return f"{value:.1f} mm"


def _top_component_lines(rec: Recommendation | None) -> tuple[str, str]:
    if rec is None:
        return "Brak", "Brak"
    main_body = next((item for item in rec.components if item.component_type == "main_body"), None)
    contra = next((item for item in rec.components if item.side == "contralateral"), None)
    return main_body.label if main_body else "Brak pewnego korpusu", contra.label if contra else "Brak odnogi"


def render_aorta_svg(measurements: Measurements, *, selected_key: str, top_recommendation: Recommendation | None) -> None:
    field = FIELD_BY_KEY[selected_key] if selected_key in FIELD_BY_KEY else FIELD_BY_KEY["neck_diameter_mm"]
    main_body_label, contra_label = _top_component_lines(top_recommendation)

    if SCHEMA_IMAGE_PATH.exists():
        image_base64 = base64.b64encode(SCHEMA_IMAGE_PATH.read_bytes()).decode("ascii")
        hotspot_buttons: list[str] = []
        overlay_boxes: list[str] = []
        for key, hotspot in OVERLAY_FIELDS.items():
            hotspot_field = FIELD_BY_KEY[key]
            outline = "2px solid rgba(249,115,22,0.45)" if key == field.key else "1px dashed rgba(148,163,184,0.22)"
            hotspot_buttons.append(
                f"""
                <button
                    type="button"
                    aria-label="Wybierz {html.escape(hotspot_field.anatomy_code)}"
                    onclick="selectFocus('{html.escape(hotspot_field.anatomy_code)}')"
                    style="
                        position:absolute;
                        left:{hotspot['left_pct']}%;
                        top:{hotspot['top_pct']}%;
                        transform:translate(-50%, -50%);
                        width:{hotspot['width_pct']}%;
                        height:{hotspot['height_pct']}%;
                        border-radius:14px;
                        border:{outline};
                        background:rgba(255,255,255,0.01);
                        cursor:pointer;
                        z-index:3;
                    "
                    onmouseover="this.style.borderColor='rgba(249,115,22,0.75)'"
                    onmouseout="this.style.borderColor='{('rgba(249,115,22,0.45)' if key == field.key else 'rgba(148,163,184,0.22)')}'"
                ></button>
                """
            )
            box_border = "#f97316" if key == field.key else "#94a3b8"
            box_shadow = "0 0 0 3px rgba(249,115,22,0.16)" if key == field.key else "none"
            overlay_boxes.append(
                f"""
                <div style="
                    position:absolute;
                    left:{hotspot['left_pct']}%;
                    top:{hotspot['top_pct']}%;
                    transform:translate(-50%, -50%);
                    min-width:74px;
                    max-width:92px;
                    padding:0.28rem 0.42rem;
                    border-radius:13px;
                    border:2px solid {box_border};
                    box-shadow:{box_shadow};
                    background:rgba(255,255,255,0.96);
                    color:#111827;
                    font-family:Helvetica, Arial, sans-serif;
                    line-height:1.08;
                    text-align:left;
                    pointer-events:none;
                    z-index:4;
                ">
                    <div style="font-size:0.72rem;font-weight:700;color:#334155;">{html.escape(hotspot_field.anatomy_code)}</div>
                    <div style="font-size:0.86rem;font-weight:700;margin-top:0.12rem;">{html.escape(_measurement_value(measurements, key))}</div>
                </div>
                """
            )
        html_code = f"""
        <div style="width:100%;">
            <div style="position:relative;width:100%;aspect-ratio:2816 / 1536;overflow:hidden;border-radius:22px;background:#fff;">
                <script>
                    function selectFocus(code) {{
                        const parentDoc = window.parent.document;
                        const candidates = Array.from(parentDoc.querySelectorAll("label, button"));
                        const target = candidates.find((element) => {{
                            const text = (element.innerText || "").trim();
                            return text.startsWith(code + " •");
                        }});
                        if (target) {{
                            target.click();
                        }}
                    }}
                </script>
                <img src="data:image/png;base64,{image_base64}" style="width:100%;height:100%;display:block;object-fit:contain;" />
                {''.join(hotspot_buttons)}
                {''.join(overlay_boxes)}
            </div>
        </div>
        """
        components.html(html_code, height=1080, scrolling=False)
    else:
        st.error(f"Brak pliku schematu: {SCHEMA_IMAGE_PATH}")

    info_col, recommendation_col = st.columns([0.95, 1.05], gap="large")
    with info_col:
        st.markdown("**Aktywny pomiar**")
        with st.container(border=True):
            st.write(f"**{field.anatomy_code}**")
            st.write(field.label)
            st.caption(f"Aktualna wartość: {_measurement_value(measurements, field.key)}")
    with recommendation_col:
        st.markdown("**Wybrany system stentgraftu**")
        with st.container(border=True):
            if top_recommendation is None:
                st.write("Brak wybranego systemu")
                st.caption("Wybierz typ stentgraftu z listy, aby zobaczyć dopasowane komponenty.")
            else:
                st.write(f"**{top_recommendation.manufacturer}**")
                st.caption(top_recommendation.family)
                st.write(f"Main body: {main_body_label}")
                st.write(f"Contra limb: {contra_label}")
