"""Streamlit form helpers backed by session state."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from domain.models import Measurements


@dataclass(frozen=True)
class NumericField:
    key: str
    anatomy_code: str
    label: str
    min_value: float
    max_value: float
    default: float
    step: float
    section: str
    format_string: str = "%.1f"


NUMERIC_FIELDS = (
    NumericField("neck_diameter_mm", "D1", "Średnica szyi aorty [mm]", 10.0, 45.0, 24.0, 0.5, "Aorta"),
    NumericField("neck_length_mm", "L1", "Długość szyi [mm]", 1.0, 200.0, 95.0, 1.0, "Aorta", "%.0f"),
    NumericField("aortic_bifurcation_length_mm", "L2", "Nerkowe → bifurkacja [mm]", 20.0, 250.0, 110.0, 1.0, "Aorta", "%.0f"),
    NumericField("neck_angle_deg", "A1", "Angulacja szyi [°]", 0.0, 120.0, 35.0, 1.0, "Aorta", "%.0f"),
    NumericField("right_iliac_diameter_mm", "RD1", "Prawa wspólna landing diameter [mm]", 5.0, 35.0, 13.0, 0.5, "Prawa biodrowa"),
    NumericField("right_iliac_length_mm", "RL1", "Prawa wspólna landing length [mm]", 20.0, 220.0, 115.0, 1.0, "Prawa biodrowa", "%.0f"),
    NumericField("right_eia_diameter_mm", "RED1", "Prawa EIA diameter [mm]", 4.0, 25.0, 8.0, 0.5, "Prawa biodrowa"),
    NumericField("left_iliac_diameter_mm", "LD1", "Lewa wspólna landing diameter [mm]", 5.0, 35.0, 14.0, 0.5, "Lewa biodrowa"),
    NumericField("left_iliac_length_mm", "LL1", "Lewa wspólna landing length [mm]", 20.0, 220.0, 120.0, 1.0, "Lewa biodrowa", "%.0f"),
    NumericField("left_eia_diameter_mm", "LED1", "Lewa EIA diameter [mm]", 4.0, 25.0, 8.0, 0.5, "Lewa biodrowa"),
)

FIELD_BY_KEY = {field.key: field for field in NUMERIC_FIELDS}
SECTION_ORDER = ("Aorta", "Prawa biodrowa", "Lewa biodrowa")


def initialize_measurement_state() -> None:
    for field in NUMERIC_FIELDS:
        st.session_state.setdefault(field.key, field.default)
    st.session_state.setdefault("ipsilateral_side", "right")
    st.session_state.setdefault("worksheet_focus", "neck_diameter_mm")


def reset_measurement_state() -> None:
    for field in NUMERIC_FIELDS:
        st.session_state[field.key] = field.default
    st.session_state["ipsilateral_side"] = "right"
    st.session_state["worksheet_focus"] = "neck_diameter_mm"


def build_measurements_from_state() -> Measurements:
    return Measurements(
        neck_diameter_mm=float(st.session_state["neck_diameter_mm"]),
        neck_length_mm=float(st.session_state["neck_length_mm"]),
        neck_angle_deg=float(st.session_state["neck_angle_deg"]),
        aortic_bifurcation_length_mm=float(st.session_state["aortic_bifurcation_length_mm"]),
        right_iliac_diameter_mm=float(st.session_state["right_iliac_diameter_mm"]),
        left_iliac_diameter_mm=float(st.session_state["left_iliac_diameter_mm"]),
        right_eia_diameter_mm=float(st.session_state["right_eia_diameter_mm"]),
        left_eia_diameter_mm=float(st.session_state["left_eia_diameter_mm"]),
        right_iliac_length_mm=float(st.session_state["right_iliac_length_mm"]),
        left_iliac_length_mm=float(st.session_state["left_iliac_length_mm"]),
        ipsilateral_side=str(st.session_state["ipsilateral_side"]),
    )


def measurement_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for field in NUMERIC_FIELDS:
        value = st.session_state[field.key]
        value_label = f"{value:.1f}" if field.format_string == "%.1f" else f"{value:.0f}"
        suffix = "°" if "angle" in field.key else "mm"
        rows.append({"Kod": field.anatomy_code, "Pomiar": field.label, "Wartość": f"{value_label} {suffix}"})
    rows.append(
        {
            "Kod": "IPSI",
            "Pomiar": "Strona ipsilateralna",
            "Wartość": "Prawa" if st.session_state["ipsilateral_side"] == "right" else "Lewa",
        }
    )
    return rows


def focus_options() -> list[str]:
    return [field.key for field in NUMERIC_FIELDS]


def format_focus_option(key: str) -> str:
    field = FIELD_BY_KEY[key]
    return f"{field.anatomy_code} • {field.label}"


def _single_field_row(field: NumericField) -> None:
    label_col, input_col = st.columns([2.7, 1.0], gap="small")
    with label_col:
        st.markdown(f"**{field.label}**")
    with input_col:
        st.number_input(
            field.label,
            min_value=field.min_value,
            max_value=field.max_value,
            step=field.step,
            format=field.format_string,
            key=field.key,
            label_visibility="collapsed",
        )


def render_field_card(key: str, *, compact: bool = False) -> None:
    field = FIELD_BY_KEY[key]
    with st.container(border=True):
        st.caption(field.anatomy_code)
        st.markdown(f"**{field.label}**")
        st.number_input(
            field.label,
            min_value=field.min_value,
            max_value=field.max_value,
            step=field.step,
            format=field.format_string,
            key=field.key,
            label_visibility="collapsed",
        )
        if not compact:
            st.caption(f"Zakres: {field.min_value:g}-{field.max_value:g}")


def _bilateral_field_row(label: str, right_field: NumericField, left_field: NumericField) -> None:
    label_col, right_col, left_col = st.columns([2.5, 1.0, 1.0], gap="small")
    with label_col:
        st.markdown(f"**{label}**")
        st.caption(f"{right_field.anatomy_code} / {left_field.anatomy_code}")
    with right_col:
        st.number_input(
            right_field.label,
            min_value=right_field.min_value,
            max_value=right_field.max_value,
            step=right_field.step,
            format=right_field.format_string,
            key=right_field.key,
            label_visibility="collapsed",
        )
    with left_col:
        st.number_input(
            left_field.label,
            min_value=left_field.min_value,
            max_value=left_field.max_value,
            step=left_field.step,
            format=left_field.format_string,
            key=left_field.key,
            label_visibility="collapsed",
        )


def render_measurement_form() -> None:
    st.subheader("Dane wymiarowania dla aplikacji EVAR")
    st.caption("Wpisuj wartości w komórki. Po każdej zmianie aplikacja automatycznie przelicza rekomendacje urządzeń.")
    st.info("Cook: długość korpusu głównego jest liczona z pomiaru L2 `nerkowe -> bifurkacja`, mimo że L1 pozostaje długością szyi na schemacie.")

    with st.container(border=True):
        st.markdown("### Aorta")
        _single_field_row(FIELD_BY_KEY["neck_diameter_mm"])
        _single_field_row(FIELD_BY_KEY["neck_length_mm"])
        _single_field_row(FIELD_BY_KEY["aortic_bifurcation_length_mm"])
        _single_field_row(FIELD_BY_KEY["neck_angle_deg"])

        st.divider()
        st.markdown("### Tętnice biodrowe")
        header_cols = st.columns([2.5, 1.0, 1.0], gap="small")
        header_cols[1].markdown("**Prawa**")
        header_cols[2].markdown("**Lewa**")
        _bilateral_field_row(
            "Średnica wspólnej (Landing D) [mm]",
            FIELD_BY_KEY["right_iliac_diameter_mm"],
            FIELD_BY_KEY["left_iliac_diameter_mm"],
        )
        _bilateral_field_row(
            "Długość wspólnej (Landing L) [mm]",
            FIELD_BY_KEY["right_iliac_length_mm"],
            FIELD_BY_KEY["left_iliac_length_mm"],
        )
        _bilateral_field_row(
            "Średnica zewnętrznej (EIA D) [mm]",
            FIELD_BY_KEY["right_eia_diameter_mm"],
            FIELD_BY_KEY["left_eia_diameter_mm"],
        )

        st.divider()
    st.radio(
        "Strona ipsilateralna / planowana introdukcja",
        options=["right", "left"],
        format_func=lambda item: "Prawa" if item == "right" else "Lewa",
        horizontal=True,
        key="ipsilateral_side",
    )
