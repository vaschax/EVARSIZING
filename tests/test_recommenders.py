from recommender import Measurements, build_recommendations, oversize_pct


def valid_measurements(**overrides) -> Measurements:
    payload = {
        "neck_diameter_mm": 24.0,
        "neck_length_mm": 95.0,
        "neck_angle_deg": 35.0,
        "aortic_bifurcation_length_mm": 110.0,
        "right_iliac_diameter_mm": 12.0,
        "left_iliac_diameter_mm": 12.0,
        "right_eia_diameter_mm": 8.0,
        "left_eia_diameter_mm": 8.0,
        "right_iliac_length_mm": 115.0,
        "left_iliac_length_mm": 120.0,
        "ipsilateral_side": "right",
    }
    payload.update(overrides)
    return Measurements(**payload)


def test_oversize_pct_formula() -> None:
    assert round(oversize_pct(26.0, 24.0), 2) == 8.33


def test_recommendations_are_sorted_by_score_desc() -> None:
    bundle = build_recommendations(valid_measurements())
    scores = [item.score for item in bundle.recommendations]
    assert scores == sorted(scores, reverse=True)


def test_cook_recommendation_contains_overlap_metadata() -> None:
    bundle = build_recommendations(valid_measurements())
    cook = next(item for item in bundle.recommendations if item.manufacturer == "Cook")
    limb_components = [item for item in cook.components if item.component_type == "limb"]
    assert limb_components
    assert any(component.predicted_overlap_range_mm is not None for component in limb_components)


def test_medtronic_contains_overlap_warning() -> None:
    bundle = build_recommendations(valid_measurements())
    medtronic = next(item for item in bundle.recommendations if item.manufacturer == "Medtronic")
    assert any("30 mm" in warning.message for warning in medtronic.warnings)


def test_access_warning_becomes_critical_for_narrow_eia() -> None:
    bundle = build_recommendations(valid_measurements(right_eia_diameter_mm=5.5))
    gore = next(item for item in bundle.recommendations if item.family == "EXCLUDER Conformable AAA (Active Control)")
    assert any(item.severity == "critical" and "EIA 5.5 mm" in item.message for item in gore.warnings)
