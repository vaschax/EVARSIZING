from evar_data import GORE_ACTIVE_CONTROL_MAIN_BODIES, GORE_C3_MAIN_BODIES
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


def test_cook_main_body_length_uses_renal_to_bifurcation_distance() -> None:
    bundle = build_recommendations(valid_measurements(neck_length_mm=8.0, aortic_bifurcation_length_mm=95.0))
    cook = next(item for item in bundle.recommendations if item.manufacturer == "Cook")
    main_body = next(item for item in cook.components if item.component_type == "main_body")
    assert "CL 84 mm | IL 108 mm" in main_body.label


def test_gore_catalogues_match_verified_pdf_suffixes() -> None:
    active_control_catalogues = {item["catalogue"] for item in GORE_ACTIVE_CONTROL_MAIN_BODIES}
    assert {"CXT231212E", "CXT261212E", "CXT281212E"}.issubset(active_control_catalogues)
    assert all(item["catalogue"].endswith("E") for item in GORE_ACTIVE_CONTROL_MAIN_BODIES)
    assert all(item.get("catalogue") for item in GORE_C3_MAIN_BODIES)


def test_medtronic_long_10_mm_limb_uses_16f_access_profile() -> None:
    bundle = build_recommendations(
        valid_measurements(
            left_iliac_diameter_mm=10.0,
            left_iliac_length_mm=170.0,
            left_eia_diameter_mm=6.0,
        )
    )
    medtronic = next(item for item in bundle.recommendations if item.manufacturer == "Medtronic")
    assert any(
        warning.severity == "critical"
        and "Medtronic contralateral limb wymaga dostępu ~ 16F" in warning.message
        and "EIA 6.0 mm" in warning.message
        for warning in medtronic.warnings
    )
