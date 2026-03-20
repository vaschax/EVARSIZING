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
from recommender import build_recommendations
from ui.cards import render_recommendation_card
from ui.forms import build_measurements_from_state, initialize_measurement_state, measurement_rows, render_measurement_form, reset_measurement_state
from ui.svg_aorta import render_aorta_svg, render_focus_selector


st.set_page_config(page_title="EVAR Sizing Prototype", page_icon="🩺", layout="wide")
initialize_measurement_state()

st.markdown(
    """
    <style>
    .app-shell {
        background:
            radial-gradient(circle at top left, rgba(251,191,36,0.16), transparent 26%),
            radial-gradient(circle at top right, rgba(59,130,246,0.14), transparent 30%),
            linear-gradient(180deg, #fff7ed 0%, #f8fafc 44%, #f8fafc 100%);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 24px;
        padding: 1.2rem 1.25rem;
        margin-bottom: 1rem;
    }
    .app-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin-bottom: 0.2rem;
        color: #0f172a;
    }
    .app-subtitle {
        color: #475569;
        font-size: 0.98rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Sterowanie")
    st.caption("Worksheet, formularz i ranking urządzeń korzystają z jednego stanu `session_state`.")
    if st.button("Przywróć dane przykładowe", use_container_width=True):
        reset_measurement_state()
        st.rerun()
    st.warning(
        "Wynik należy zweryfikować z pełnym IFU, obrazowaniem i doświadczeniem operatora. "
        "W szczególności część logiki Medtronic pozostaje heurystyczna."
    )
    st.info(
        "Docelowy workflow: wpisujesz pomiary w worksheet, aplikacja przelicza ranking rodzin "
        "urządzeń i pokazuje komponenty na wspólnym schemacie."
    )

measurements = build_measurements_from_state()
result = build_recommendations(measurements)
top_recommendation = result.recommendations[0] if result.recommendations else None

st.markdown('<div class="app-shell">', unsafe_allow_html=True)
st.markdown('<div class="app-title">EVAR Stentgraft Sizing Worksheet</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Prototyp planowania EVAR dla worksheetów Gore, Medtronic i Cook z jednym stanem pomiarów oraz wizualnym szkicem aorty.</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.error(
    "**OSTRZEŻENIE KLINICZNE (DISCLAIMER):** Aplikacja stanowi wyłącznie prototyp do celów edukacyjnych i nie może być używana "
    "jako jedyne narzędzie do podejmowania decyzji klinicznych. Ostateczny dobór stentgraftu musi odbywać się na stacji roboczej "
    "(np. TeraRecon, OsiriX, 3mensio) w oparciu o pełne, oficjalne IFU producenta."
)

summary_cols = st.columns(4)
summary_cols[0].metric("Szyja", f"{measurements.neck_diameter_mm:.1f} mm", f"L1 {measurements.neck_length_mm:.0f} mm")
summary_cols[1].metric("Ipsilateralna", measurements.ipsilateral_label, f"{measurements.ipsilateral_diameter_mm:.1f} mm / {measurements.ipsilateral_length_mm:.0f} mm")
summary_cols[2].metric("Kontralateralna", measurements.contralateral_label, f"{measurements.contralateral_diameter_mm:.1f} mm / {measurements.contralateral_length_mm:.0f} mm")
summary_cols[3].metric("Angulacja", f"{measurements.neck_angle_deg:.0f}°", f"L2 {measurements.aortic_bifurcation_length_mm:.0f} mm")

if result.warnings:
    with st.expander("Globalne ostrzeżenia", expanded=True):
        for warning in result.warnings:
            st.write(f"- {warning}")

tab_worksheet, tab_summary, tab_gore, tab_cook, tab_medtronic, tab_tables = st.tabs(
    ["Worksheet", "Podsumowanie", "Gore", "Cook", "Medtronic", "Tabele źródłowe"]
)

with tab_worksheet:
    render_focus_selector()
    worksheet_left, worksheet_right = st.columns([1.25, 1.0], gap="large")
    with worksheet_left:
        st.subheader("Schemat aorty i komponentów")
        render_aorta_svg(
            measurements,
            selected_key=st.session_state["worksheet_focus"],
            top_recommendation=top_recommendation,
        )
        st.caption(
            "Diagram jest renderowany z danych sesji. Focus worksheetu podświetla aktualnie edytowany wymiar, "
            "a overlay pokazuje komponenty z najwyżej ocenionej rekomendacji."
        )
    with worksheet_right:
        render_measurement_form()
        st.divider()
        st.write("**Aktualny worksheet**")
        st.dataframe(pd.DataFrame(measurement_rows()), hide_index=True, use_container_width=True)

with tab_summary:
    st.subheader("Ranking rodzin urządzeń")
    for rec in result.recommendations:
        render_recommendation_card(rec)

with tab_gore:
    gore_recs = [rec for rec in result.recommendations if rec.manufacturer == "Gore"]
    for rec in gore_recs:
        render_recommendation_card(rec)
        if rec.alternatives.get("main_body_options"):
            st.write("**Alternatywne korpusy**")
            st.dataframe(pd.DataFrame(rec.alternatives["main_body_options"]), hide_index=True, use_container_width=True)
        if rec.alternatives.get("contralateral_leg_options"):
            st.write("**Alternatywne odnogi kontralateralne**")
            st.dataframe(pd.DataFrame(rec.alternatives["contralateral_leg_options"]), hide_index=True, use_container_width=True)

with tab_cook:
    cook_rec = next(rec for rec in result.recommendations if rec.manufacturer == "Cook")
    render_recommendation_card(cook_rec)
    st.info(
        f"Cook liczy stronę ipsilateralną jako {measurements.ipsilateral_label.lower()}, "
        f"a kontralateralną jako {measurements.contralateral_label.lower()}."
    )

with tab_medtronic:
    medtronic_rec = next(rec for rec in result.recommendations if rec.manufacturer == "Medtronic")
    render_recommendation_card(medtronic_rec)
    if medtronic_rec.alternatives.get("main_body_options"):
        st.write("**Alternatywne korpusy**")
        st.dataframe(pd.DataFrame(medtronic_rec.alternatives["main_body_options"]), hide_index=True, use_container_width=True)
    if medtronic_rec.alternatives.get("contralateral_limb_options"):
        st.write("**Alternatywne odnogi**")
        st.dataframe(pd.DataFrame(medtronic_rec.alternatives["contralateral_limb_options"]), hide_index=True, use_container_width=True)

with tab_tables:
    st.subheader("Jawne tabele użyte w prototypie")
    st.caption("Dane są nadal jawne i edytowalne w repo, ale logika producentów została wydzielona do `engines/`.")

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
