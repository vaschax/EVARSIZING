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
    NumericField("aortic_bifurcation_length_mm", "L2", "Nerki → rozwidlenie [mm]", 20.0, 250.0, 110.0, 1.0, "Aorta", "%.0f"),
    NumericField("neck_angle_deg", "A1", "Angulacja szyi [°]", 0.0, 120.0, 35.0, 1.0, "Aorta", "%.0f"),
    NumericField("right_iliac_diameter_mm", "D-R", "Prawa biodrowa landing zone [mm]", 5.0, 35.0, 13.0, 0.5, "Prawa biodrowa"),
    NumericField("right_eia_diameter_mm", "EIA-R", "Prawa EIA dostęp [mm]", 4.0, 25.0, 8.0, 0.5, "Prawa biodrowa"),
    NumericField("right_iliac_length_mm", "L-R", "Prawa biodrowa długość robocza [mm]", 20.0, 220.0, 115.0, 1.0, "Prawa biodrowa", "%.0f"),
    NumericField("left_iliac_diameter_mm", "D-L", "Lewa biodrowa landing zone [mm]", 5.0, 35.0, 14.0, 0.5, "Lewa biodrowa"),
    NumericField("left_eia_diameter_mm", "EIA-L", "Lewa EIA dostęp [mm]", 4.0, 25.0, 8.0, 0.5, "Lewa biodrowa"),
    NumericField("left_iliac_length_mm", "L-L", "Lewa biodrowa długość robocza [mm]", 20.0, 220.0, 120.0, 1.0, "Lewa biodrowa", "%.0f"),
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


def render_measurement_form() -> None:
    st.subheader("Worksheet pomiarowy")
    st.caption("Pomiary są trzymane w `st.session_state`, więc zmiana focusu i dalsze rekomendacje korzystają z tego samego stanu.")

    section_columns = st.columns(3)
    for column, section in zip(section_columns, SECTION_ORDER):
        with column:
            st.markdown(f"**{section}**")
            for field in NUMERIC_FIELDS:
                if field.section != section:
                    continue
                st.number_input(
                    f"{field.anatomy_code} {field.label}",
                    min_value=field.min_value,
                    max_value=field.max_value,
                    step=field.step,
                    format=field.format_string,
                    key=field.key,
                )

    st.radio(
        "Strona ipsilateralna",
        options=["right", "left"],
        format_func=lambda item: "Prawa" if item == "right" else "Lewa",
        horizontal=True,
        key="ipsilateral_side",
    )
