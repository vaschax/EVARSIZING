from __future__ import annotations

import pandas as pd
import streamlit as st

from evar_data import (
    COOK_CONTRALATERAL_LENGTHS,
    COOK_IPSILATERAL_LENGTHS,
    COOK_LEG_DIAMETERS,
    COOK_MAIN_BODY_DIAMETERS,
    COOK_MAIN_BODY_LENGTHS,
    DATA_SOURCES,
    GORE_ACTIVE_CONTROL_MAIN_BODIES,
    GORE_C3_MAIN_BODIES,
    GORE_CONTRALATERAL_LEGS,
    MEDTRONIC_BIFURCATIONS,
    MEDTRONIC_LIMBS,
    MEDTRONIC_SHORT_BODIES,
)
from recommender import Measurements, build_recommendations


st.set_page_config(page_title="EVAR Sizing Prototype", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
    .app-card {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        background: linear-gradient(180deg, rgba(248,250,252,1) 0%, rgba(241,245,249,1) 100%);
        margin-bottom: 0.8rem;
    }
    .app-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 0.15rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: #dbeafe;
        color: #1d4ed8;
    }
    .app-muted {
        color: #475569;
        font-size: 0.92rem;
    }
    .app-title {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">EVAR Stentgraft Sizing Prototype</div>', unsafe_allow_html=True)
st.caption(
    "Prototyp planowania EVAR na podstawie załączonych worksheetów Gore, Medtronic i Cook. "
    "To narzędzie wspomagające, nie samodzielna decyzja kliniczna."
)

with st.sidebar:
    st.header("Pomiary")
    neck_diameter = st.number_input("D1 szyja aorty [mm]", min_value=10.0, max_value=45.0, value=24.0, step=0.5)
    neck_length = st.number_input("L1 długość szyi [mm]", min_value=0.0, max_value=200.0, value=95.0, step=1.0)
    neck_angle = st.number_input("Angulacja szyi [°]", min_value=0.0, max_value=120.0, value=35.0, step=1.0)
    st.divider()
    right_diam = st.number_input("Prawa biodrowa średnica landing zone [mm]", min_value=5.0, max_value=35.0, value=13.0, step=0.5)
    right_length = st.number_input("Prawa biodrowa długość robocza [mm]", min_value=20.0, max_value=220.0, value=115.0, step=1.0)
    left_diam = st.number_input("Lewa biodrowa średnica landing zone [mm]", min_value=5.0, max_value=35.0, value=14.0, step=0.5)
    left_length = st.number_input("Lewa biodrowa długość robocza [mm]", min_value=20.0, max_value=220.0, value=120.0, step=1.0)
    ipsi_side = st.radio("Strona ipsilateralna", options=["right", "left"], format_func=lambda x: "Prawa" if x == "right" else "Lewa")
    st.divider()
    st.warning(
        "Wynik należy zweryfikować z pełnym IFU, obrazowaniem i doświadczeniem operatora. "
        "W szczególności część logiki Medtronic jest heurystyczna."
    )

measurements = Measurements(
    neck_diameter_mm=neck_diameter,
    neck_length_mm=neck_length,
    neck_angle_deg=neck_angle,
    right_iliac_diameter_mm=right_diam,
    left_iliac_diameter_mm=left_diam,
    right_iliac_length_mm=right_length,
    left_iliac_length_mm=left_length,
    ipsilateral_side=ipsi_side,
)

result = build_recommendations(measurements)

summary_cols = st.columns(4)
summary_cols[0].metric("Szyja", f"{measurements.neck_diameter_mm:.1f} mm", f"L1 {measurements.neck_length_mm:.0f} mm")
summary_cols[1].metric("Ipsilateralna", f"{measurements.ipsilateral_label}", f"{measurements.ipsilateral_diameter_mm:.1f} mm / {measurements.ipsilateral_length_mm:.0f} mm")
summary_cols[2].metric("Kontralateralna", f"{measurements.contralateral_label}", f"{measurements.contralateral_diameter_mm:.1f} mm / {measurements.contralateral_length_mm:.0f} mm")
summary_cols[3].metric("Angulacja", f"{measurements.neck_angle_deg:.0f}°")

if result["warnings"]:
    with st.expander("Globalne ostrzeżenia", expanded=True):
        for warning in result["warnings"]:
            st.write(f"- {warning}")

tab_summary, tab_gore, tab_cook, tab_medtronic, tab_tables = st.tabs(
    ["Podsumowanie", "Gore", "Cook", "Medtronic", "Tabele źródłowe"]
)


def render_recommendation_card(rec: dict) -> None:
    st.markdown(
        f"""
        <div class="app-card">
            <div class="app-badge">{rec['manufacturer']} • {rec['status']} • score {rec['score']}</div>
            <h3 style="margin:0 0 0.25rem 0;">{rec['family']}</h3>
            <div class="app-muted">{rec['source']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if rec["components"]:
        for component in rec["components"]:
            title = component["component"]
            official = "oficjalna tabela" if component["official"] else "heurystyka"
            extra = f" | katalog {component['catalogue']}" if component.get("catalogue") else ""
            with st.container(border=True):
                st.write(f"**{title}**")
                st.write(component["label"])
                st.caption(f"{component['details']} | {official}{extra}")
    if rec["warnings"]:
        for item in rec["warnings"]:
            st.warning(item)
    if rec["notes"]:
        for note in rec["notes"]:
            st.caption(note)


with tab_summary:
    st.subheader("Ranking rodzin urządzeń")
    for rec in result["recommendations"]:
        render_recommendation_card(rec)

with tab_gore:
    gore_recs = [rec for rec in result["recommendations"] if rec["manufacturer"] == "Gore"]
    for rec in gore_recs:
        render_recommendation_card(rec)
        alt = rec.get("alternatives", {})
        if alt.get("main_body_options"):
            st.dataframe(pd.DataFrame(alt["main_body_options"]), hide_index=True, use_container_width=True)

with tab_cook:
    cook_rec = next(rec for rec in result["recommendations"] if rec["manufacturer"] == "Cook")
    render_recommendation_card(cook_rec)
    st.info(
        f"Cook liczy stronę ipsilateralną jako {measurements.ipsilateral_label.lower()}, "
        f"a kontralateralną jako {measurements.contralateral_label.lower()}."
    )

with tab_medtronic:
    medtronic_rec = next(rec for rec in result["recommendations"] if rec["manufacturer"] == "Medtronic")
    render_recommendation_card(medtronic_rec)
    alt = medtronic_rec.get("alternatives", {})
    if alt.get("main_body_options"):
        st.write("**Alternatywne korpusy**")
        st.dataframe(pd.DataFrame(alt["main_body_options"]), hide_index=True, use_container_width=True)
    if alt.get("contralateral_limb_options"):
        st.write("**Alternatywne odnogi**")
        st.dataframe(pd.DataFrame(alt["contralateral_limb_options"]), hide_index=True, use_container_width=True)

with tab_tables:
    st.subheader("Jawne tabele użyte w prototypie")
    st.caption("To są te struktury, które najłatwiej edytować dalej w VS Code.")

    with st.expander("Cook"):
        st.write("Main body diameter bands")
        st.dataframe(pd.DataFrame(COOK_MAIN_BODY_DIAMETERS), hide_index=True, use_container_width=True)
        st.write("Main body length bands")
        st.dataframe(pd.DataFrame(COOK_MAIN_BODY_LENGTHS), hide_index=True, use_container_width=True)
        st.write("Leg diameters")
        st.dataframe(pd.DataFrame(COOK_LEG_DIAMETERS), hide_index=True, use_container_width=True)
        st.write("Contralateral lengths")
        st.dataframe(pd.DataFrame(COOK_CONTRALATERAL_LENGTHS), hide_index=True, use_container_width=True)
        st.write("Ipsilateral lengths")
        st.dataframe(pd.DataFrame(COOK_IPSILATERAL_LENGTHS), hide_index=True, use_container_width=True)

    with st.expander("Gore"):
        st.write("Active Control main bodies")
        st.dataframe(pd.DataFrame(GORE_ACTIVE_CONTROL_MAIN_BODIES), hide_index=True, use_container_width=True)
        st.write("C3 main bodies")
        st.dataframe(pd.DataFrame(GORE_C3_MAIN_BODIES), hide_index=True, use_container_width=True)
        st.write("Contralateral legs")
        st.dataframe(pd.DataFrame(GORE_CONTRALATERAL_LEGS), hide_index=True, use_container_width=True)

    with st.expander("Medtronic"):
        st.write("Bifurcations")
        st.dataframe(pd.DataFrame(MEDTRONIC_BIFURCATIONS), hide_index=True, use_container_width=True)
        st.write("Short bodies")
        st.dataframe(pd.DataFrame(MEDTRONIC_SHORT_BODIES), hide_index=True, use_container_width=True)
        st.write("Limbs")
        st.dataframe(pd.DataFrame(MEDTRONIC_LIMBS), hide_index=True, use_container_width=True)

    with st.expander("Źródła"):
        st.json(DATA_SOURCES)
