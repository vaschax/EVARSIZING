"""Recommendation card renderers for Streamlit."""

from __future__ import annotations

import streamlit as st

from domain.constants import BORDERLINE_OVERSIZE_MAX, BORDERLINE_OVERSIZE_MIN, IDEAL_OVERSIZE_MAX, IDEAL_OVERSIZE_MIN
from domain.models import ComponentRecommendation, Recommendation


def render_oversize_badge(value: float | None) -> None:
    if value is None:
        return
    if IDEAL_OVERSIZE_MIN <= value <= IDEAL_OVERSIZE_MAX:
        color = "#166534"
        background = "#dcfce7"
    elif BORDERLINE_OVERSIZE_MIN <= value <= BORDERLINE_OVERSIZE_MAX:
        color = "#854d0e"
        background = "#fef3c7"
    else:
        color = "#991b1b"
        background = "#fee2e2"
    st.markdown(
        f"""
        <span style="display:inline-block;padding:0.2rem 0.55rem;border-radius:999px;
        font-size:0.82rem;font-weight:700;background:{background};color:{color};margin-bottom:0.35rem;">
        Oversizing {value:.1f}%
        </span>
        """,
        unsafe_allow_html=True,
    )


def render_overlap_summary(component: ComponentRecommendation) -> None:
    badges: list[str] = []
    if component.required_overlap_mm is not None:
        badges.append(
            f"""
            <span style="display:inline-block;padding:0.18rem 0.5rem;border-radius:999px;
            font-size:0.8rem;background:#e0f2fe;color:#075985;margin-right:0.35rem;">
            Min. overlap {component.required_overlap_mm:.0f} mm
            </span>
            """
        )
    if component.predicted_overlap_range_mm is not None:
        overlap_min, overlap_max = component.predicted_overlap_range_mm
        badges.append(
            f"""
            <span style="display:inline-block;padding:0.18rem 0.5rem;border-radius:999px;
            font-size:0.8rem;background:#ede9fe;color:#5b21b6;">
            Overlap ~ {overlap_min:.0f}-{overlap_max:.0f} mm
            </span>
            """
        )
    if badges:
        st.markdown("".join(badges), unsafe_allow_html=True)


def render_recommendation_card(rec: Recommendation) -> None:
    st.markdown(
        f"""
        <div style="border:1px solid rgba(49,51,63,0.16);border-radius:18px;padding:1rem 1.1rem;
        background:linear-gradient(180deg,#f8fafc 0%,#f1f5f9 100%);margin-bottom:0.8rem;">
            <div style="display:inline-block;border-radius:999px;padding:0.15rem 0.6rem;font-size:0.8rem;
            font-weight:700;background:#dbeafe;color:#1d4ed8;margin-bottom:0.5rem;">
            {rec.manufacturer} • {rec.status} • score {rec.score}
            </div>
            <h3 style="margin:0 0 0.25rem 0;">{rec.family}</h3>
            <div style="color:#475569;font-size:0.92rem;">{rec.source}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for component in rec.components:
        official = "oficjalna tabela" if component.official else "heurystyka"
        extra = f" | katalog {component.catalogue}" if component.catalogue else ""
        with st.container(border=True):
            st.write(f"**{component.title}**")
            render_oversize_badge(component.oversize_pct)
            render_overlap_summary(component)
            st.write(component.label)
            st.caption(f"{component.details} | {official}{extra}")
    for item in rec.warnings:
        st.warning(item)
    for note in rec.notes:
        st.caption(note)
