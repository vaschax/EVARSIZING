"""Public recommendation API kept as a stable import layer for the app and tests."""

from __future__ import annotations

from evar_data import DATA_SOURCES
from domain.models import ComponentRecommendation, Measurements, Recommendation, RecommendationBundle, WarningMessage
from engines import recommend_cook, recommend_gore_active_control, recommend_gore_c3, recommend_medtronic
from engines.common import build_global_warnings, oversize_pct

__all__ = [
    "ComponentRecommendation",
    "Measurements",
    "Recommendation",
    "RecommendationBundle",
    "WarningMessage",
    "build_global_warnings",
    "build_recommendations",
    "oversize_pct",
]


def build_recommendations(m: Measurements) -> RecommendationBundle:
    recommendations = sorted(
        [
            recommend_cook(m),
            recommend_gore_active_control(m),
            recommend_gore_c3(m),
            recommend_medtronic(m),
        ],
        key=lambda item: item.score,
        reverse=True,
    )
    return RecommendationBundle(
        warnings=tuple(build_global_warnings(m)),
        recommendations=tuple(recommendations),
        sources=DATA_SOURCES,
    )
