"""PDF report generator for the EVAR planning worksheet."""

from __future__ import annotations

from datetime import datetime
import unicodedata

from domain.models import Measurements, Recommendation, RecommendationBundle, WarningMessage


def _ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii")


def _warning_line(item: WarningMessage) -> str:
    return f"[{item.severity.upper()}] {item.message}"


def build_plan_pdf(
    *,
    patient_id: str,
    operator_notes: str,
    measurements: Measurements,
    result: RecommendationBundle,
    top_recommendation: Recommendation | None,
) -> bytes:
    try:
        from fpdf import FPDF
    except ImportError as exc:
        raise RuntimeError("Brakuje zaleznosci fpdf2. Zainstaluj pakiet, aby generowac PDF.") from exc

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    text_width = pdf.epw
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _ascii("EVAR Planning Sheet"), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(text_width, 6, _ascii(f"Patient ID: {patient_id or 'N/A'} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
    if top_recommendation:
        pdf.multi_cell(
            text_width,
            6,
            _ascii(f"Top recommendation: {top_recommendation.manufacturer} | {top_recommendation.family} | score {top_recommendation.score}"),
        )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, _ascii("Measurements"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    measurement_lines = [
        f"D1 neck diameter: {measurements.neck_diameter_mm:.1f} mm",
        f"Neck length: {measurements.neck_length_mm:.0f} mm",
        f"Cook L1 renal to bifurcation: {measurements.aortic_bifurcation_length_mm:.0f} mm",
        f"Right iliac landing / EIA: {measurements.right_iliac_diameter_mm:.1f} mm / {measurements.right_eia_diameter_mm:.1f} mm",
        f"Left iliac landing / EIA: {measurements.left_iliac_diameter_mm:.1f} mm / {measurements.left_eia_diameter_mm:.1f} mm",
        f"Right iliac length: {measurements.right_iliac_length_mm:.0f} mm",
        f"Left iliac length: {measurements.left_iliac_length_mm:.0f} mm",
        f"Ipsilateral side: {measurements.ipsilateral_label}",
    ]
    for line in measurement_lines:
        pdf.multi_cell(text_width, 6, _ascii(line))

    if top_recommendation:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _ascii("Selected components"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for component in top_recommendation.components:
            access_text = ""
            if component.access_profile_fr is not None and component.required_access_diameter_mm is not None:
                access_text = f" | access {component.access_profile_fr:.0f}F (~{component.required_access_diameter_mm:.1f} mm)"
            pdf.multi_cell(
                text_width,
                6,
                _ascii(f"{component.title}: {component.label} | catalogue {component.catalogue or 'N/A'}{access_text}"),
            )

    warnings = list(result.warnings)
    if top_recommendation:
        warnings.extend(top_recommendation.warnings)
    if warnings:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _ascii("Warnings"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        for item in warnings:
            pdf.multi_cell(text_width, 6, _ascii(_warning_line(item)))

    if operator_notes.strip():
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _ascii("Operator notes"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(text_width, 6, _ascii(operator_notes))

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(
        text_width,
        6,
        _ascii("DISCLAIMER: Educational planning aid only. Final device selection must be confirmed on a dedicated workstation and in the official manufacturer IFU."),
    )

    return bytes(pdf.output())
