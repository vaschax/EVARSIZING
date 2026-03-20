import importlib.util

import pytest

from recommender import Measurements, build_recommendations
from ui.report_pdf import build_plan_pdf


def valid_measurements() -> Measurements:
    return Measurements(
        neck_diameter_mm=24.0,
        neck_length_mm=95.0,
        neck_angle_deg=35.0,
        aortic_bifurcation_length_mm=110.0,
        right_iliac_diameter_mm=12.0,
        left_iliac_diameter_mm=12.0,
        right_eia_diameter_mm=8.0,
        left_eia_diameter_mm=8.0,
        right_iliac_length_mm=115.0,
        left_iliac_length_mm=120.0,
        ipsilateral_side="right",
    )


@pytest.mark.skipif(importlib.util.find_spec("fpdf") is None, reason="fpdf2 not installed in current interpreter")
def test_build_plan_pdf_returns_bytes() -> None:
    measurements = valid_measurements()
    result = build_recommendations(measurements)
    pdf_bytes = build_plan_pdf(
        patient_id="TEST-001",
        operator_notes="standard case",
        measurements=measurements,
        result=result,
        top_recommendation=result.recommendations[0],
    )
    assert pdf_bytes.startswith(b"%PDF")
