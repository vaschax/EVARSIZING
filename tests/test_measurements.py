import pytest

from recommender import Measurements


def valid_measurements(**overrides) -> Measurements:
    payload = {
        "neck_diameter_mm": 24.0,
        "neck_length_mm": 25.0,
        "neck_angle_deg": 30.0,
        "aortic_bifurcation_length_mm": 110.0,
        "right_iliac_diameter_mm": 13.0,
        "left_iliac_diameter_mm": 14.0,
        "right_eia_diameter_mm": 8.0,
        "left_eia_diameter_mm": 8.5,
        "right_iliac_length_mm": 115.0,
        "left_iliac_length_mm": 120.0,
        "ipsilateral_side": "right",
    }
    payload.update(overrides)
    return Measurements(**payload)


def test_measurements_reject_invalid_ipsilateral_side() -> None:
    with pytest.raises(ValueError):
        valid_measurements(ipsilateral_side="foo")


def test_measurements_reject_non_positive_diameter() -> None:
    with pytest.raises(ValueError):
        valid_measurements(neck_diameter_mm=0.0)


def test_measurements_compute_ipsilateral_and_contralateral_views() -> None:
    m = valid_measurements(ipsilateral_side="left")
    assert m.ipsilateral_diameter_mm == 14.0
    assert m.contralateral_diameter_mm == 13.0
    assert m.ipsilateral_eia_diameter_mm == 8.5
    assert m.contralateral_eia_diameter_mm == 8.0
    assert m.ipsilateral_label == "Lewa"
    assert m.contralateral_label == "Prawa"
