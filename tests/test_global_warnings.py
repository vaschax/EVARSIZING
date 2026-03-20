from recommender import Measurements, build_global_warnings


def valid_measurements(**overrides) -> Measurements:
    payload = {
        "neck_diameter_mm": 24.0,
        "neck_length_mm": 25.0,
        "neck_angle_deg": 30.0,
        "aortic_bifurcation_length_mm": 110.0,
        "right_iliac_diameter_mm": 13.0,
        "left_iliac_diameter_mm": 14.0,
        "right_iliac_length_mm": 115.0,
        "left_iliac_length_mm": 120.0,
        "ipsilateral_side": "right",
    }
    payload.update(overrides)
    return Measurements(**payload)


def test_hostile_anatomy_short_neck_warning() -> None:
    warnings = build_global_warnings(valid_measurements(neck_length_mm=8.0))
    assert any("Hostile anatomy: długość szyi < 10 mm" in item for item in warnings)


def test_hostile_large_neck_warning() -> None:
    warnings = build_global_warnings(valid_measurements(neck_diameter_mm=33.0))
    assert any("szyja > 32 mm" in item for item in warnings)


def test_no_global_warning_for_standard_case() -> None:
    warnings = build_global_warnings(valid_measurements())
    assert warnings == []
