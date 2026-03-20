"""Sizing data extracted from the provided Gore, Medtronic and Cook PDFs.

This module stores the planning tables as editable Python data so the user can
maintain them in VS Code without touching the recommendation logic.
"""

from __future__ import annotations

DATA_SOURCES = {
    "cook": "zenithalpha.pdf (Cook Zenith Alpha worksheet, page 1-2)",
    "gore": "goreex.pdf (GORE EXCLUDER product family, pages 2-4)",
    "medtronic": "endurantII.pdf (Endurant II/IIs sizing sheet, page 2)",
}


COOK_MAIN_BODY_DIAMETERS = [
    {"neck_range_mm": (18, 19), "graft_diameter_mm": 22},
    {"neck_range_mm": (20, 21), "graft_diameter_mm": 24},
    {"neck_range_mm": (22, 22), "graft_diameter_mm": 26},
    {"neck_range_mm": (23, 24), "graft_diameter_mm": 28},
    {"neck_range_mm": (25, 26), "graft_diameter_mm": 30},
    {"neck_range_mm": (27, 28), "graft_diameter_mm": 32},
    {"neck_range_mm": (29, 32), "graft_diameter_mm": 36},
]

COOK_MAIN_BODY_LENGTHS = [
    {
        "neck_length_range_mm": (75, 88),
        "contralateral_length_mm": 70,
        "ipsilateral_length_mm": 94,
    },
    {
        "neck_length_range_mm": (89, 102),
        "contralateral_length_mm": 84,
        "ipsilateral_length_mm": 108,
    },
    {
        "neck_length_range_mm": (103, 112),
        "contralateral_length_mm": 98,
        "ipsilateral_length_mm": 122,
    },
    {
        "neck_length_range_mm": (113, 122),
        "contralateral_length_mm": 108,
        "ipsilateral_length_mm": 132,
    },
    {
        "neck_length_range_mm": (123, 132),
        "contralateral_length_mm": 118,
        "ipsilateral_length_mm": 142,
    },
    {
        "neck_length_range_mm": (133, 142),
        "contralateral_length_mm": 128,
        "ipsilateral_length_mm": 152,
    },
]

COOK_LEG_DIAMETERS = [
    {"iliac_range_mm": (8, 8), "graft_diameter_mm": 9},
    {"iliac_range_mm": (9, 9), "graft_diameter_mm": 11},
    {"iliac_range_mm": (10, 12), "graft_diameter_mm": 13},
    {"iliac_range_mm": (13, 15), "graft_diameter_mm": 16},
    {"iliac_range_mm": (16, 18), "graft_diameter_mm": 20},
    {"iliac_range_mm": (19, 20), "graft_diameter_mm": 24},
]

COOK_CONTRALATERAL_LENGTHS = [
    {"vessel_length_mm": (38, 54), "diameter_range_mm": (9, 24), "label_length_mm": 42, "total_length_mm": 70},
    {"vessel_length_mm": (55, 71), "diameter_range_mm": (9, 24), "label_length_mm": 59, "total_length_mm": 87},
    {"vessel_length_mm": (72, 89), "diameter_range_mm": (9, 24), "label_length_mm": 77, "total_length_mm": 105},
    {"vessel_length_mm": (90, 105), "diameter_range_mm": (9, 24), "label_length_mm": 93, "total_length_mm": 121},
    {"vessel_length_mm": (106, 122), "diameter_range_mm": (9, 13), "label_length_mm": 110, "total_length_mm": 138},
    {"vessel_length_mm": (123, 137), "diameter_range_mm": (9, 13), "label_length_mm": 125, "total_length_mm": 153},
]

COOK_IPSILATERAL_LENGTHS = [
    {"vessel_length_mm": (38, 54), "diameter_range_mm": (9, 13), "label_length_mm": 42, "total_length_mm": 70},
    {"vessel_length_mm": (51, 54), "diameter_range_mm": (16, 24), "label_length_mm": 42, "total_length_mm": 70},
    {"vessel_length_mm": (55, 71), "diameter_range_mm": (9, 13), "label_length_mm": 59, "total_length_mm": 87},
    {"vessel_length_mm": (68, 71), "diameter_range_mm": (16, 24), "label_length_mm": 59, "total_length_mm": 87},
    {"vessel_length_mm": (72, 89), "diameter_range_mm": (9, 24), "label_length_mm": 77, "total_length_mm": 105},
    {"vessel_length_mm": (90, 105), "diameter_range_mm": (9, 24), "label_length_mm": 93, "total_length_mm": 121},
    {"vessel_length_mm": (106, 122), "diameter_range_mm": (9, 13), "label_length_mm": 110, "total_length_mm": 138},
    {"vessel_length_mm": (123, 137), "diameter_range_mm": (9, 13), "label_length_mm": 125, "total_length_mm": 153},
]


GORE_ACTIVE_CONTROL_MAIN_BODIES = [
    {"catalogue": "CXT201212", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (16, 18), "aortic_diameter_mm": 20, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 120, "introducer_fr": 15},
    {"catalogue": "CXT201412", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (16, 18), "aortic_diameter_mm": 20, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 15},
    {"catalogue": "CXT231412", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 15},
    {"catalogue": "CXT261412", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 16},
    {"catalogue": "CXT281412", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 16},
    {"catalogue": "CXT321414", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (27, 29), "aortic_diameter_mm": 32, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 18},
    {"catalogue": "CXT361414", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (30, 32), "aortic_diameter_mm": 36, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 18},
]

GORE_C3_MAIN_BODIES = [
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 120, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 140, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 160, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 180, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 160, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (19, 21), "aortic_diameter_mm": 23, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 180, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 120, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 140, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 160, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 180, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 160, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (22, 23), "aortic_diameter_mm": 26, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 180, "introducer_fr": 16},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 120, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 140, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 160, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (10, 11), "iliac_diameter_mm": 12, "overall_length_mm": 180, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 120, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 160, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (24, 26), "aortic_diameter_mm": 28.5, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 180, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (27, 29), "aortic_diameter_mm": 31, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 130, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (27, 29), "aortic_diameter_mm": 31, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 150, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (27, 29), "aortic_diameter_mm": 31, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 170, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (30, 32), "aortic_diameter_mm": 35, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 140, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (30, 32), "aortic_diameter_mm": 35, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 160, "introducer_fr": 18},
    {"family": "EXCLUDER AAA with C3", "aortic_range_mm": (30, 32), "aortic_diameter_mm": 35, "iliac_range_mm": (12, 13.5), "iliac_diameter_mm": 14.5, "overall_length_mm": 180, "introducer_fr": 18},
]

GORE_CONTRALATERAL_LEGS = [
    {"catalogue": "PLC121000", "iliac_range_mm": (10, 11), "graft_diameter_mm": 12, "length_mm": 100, "sheath_fr": 12},
    {"catalogue": "PLC121200", "iliac_range_mm": (10, 11), "graft_diameter_mm": 12, "length_mm": 120, "sheath_fr": 12},
    {"catalogue": "PLC121400", "iliac_range_mm": (10, 11), "graft_diameter_mm": 12, "length_mm": 140, "sheath_fr": 12},
    {"catalogue": "PLC141000", "iliac_range_mm": (12, 13.5), "graft_diameter_mm": 14.5, "length_mm": 100, "sheath_fr": 12},
    {"catalogue": "PLC141200", "iliac_range_mm": (12, 13.5), "graft_diameter_mm": 14.5, "length_mm": 120, "sheath_fr": 12},
    {"catalogue": "PLC141400", "iliac_range_mm": (12, 13.5), "graft_diameter_mm": 14.5, "length_mm": 140, "sheath_fr": 12},
    {"catalogue": "PLC161000", "iliac_range_mm": (13.5, 14.5), "graft_diameter_mm": 16, "length_mm": 95, "sheath_fr": 12},
    {"catalogue": "PLC161200", "iliac_range_mm": (13.5, 14.5), "graft_diameter_mm": 16, "length_mm": 115, "sheath_fr": 12},
    {"catalogue": "PLC161400", "iliac_range_mm": (13.5, 14.5), "graft_diameter_mm": 16, "length_mm": 135, "sheath_fr": 12},
    {"catalogue": "PLC181000", "iliac_range_mm": (14.5, 16.5), "graft_diameter_mm": 18, "length_mm": 95, "sheath_fr": 12},
    {"catalogue": "PLC181200", "iliac_range_mm": (14.5, 16.5), "graft_diameter_mm": 18, "length_mm": 115, "sheath_fr": 12},
    {"catalogue": "PLC181400", "iliac_range_mm": (14.5, 16.5), "graft_diameter_mm": 18, "length_mm": 135, "sheath_fr": 12},
    {"catalogue": "PLC201000", "iliac_range_mm": (16.5, 18.5), "graft_diameter_mm": 20, "length_mm": 95, "sheath_fr": 12},
    {"catalogue": "PLC201200", "iliac_range_mm": (16.5, 18.5), "graft_diameter_mm": 20, "length_mm": 115, "sheath_fr": 12},
    {"catalogue": "PLC201400", "iliac_range_mm": (16.5, 18.5), "graft_diameter_mm": 20, "length_mm": 135, "sheath_fr": 12},
    {"catalogue": "PLC231000", "iliac_range_mm": (18.5, 21.5), "graft_diameter_mm": 23, "length_mm": 100, "sheath_fr": 14},
    {"catalogue": "PLC231200", "iliac_range_mm": (18.5, 21.5), "graft_diameter_mm": 23, "length_mm": 120, "sheath_fr": 14},
    {"catalogue": "PLC231400", "iliac_range_mm": (18.5, 21.5), "graft_diameter_mm": 23, "length_mm": 140, "sheath_fr": 14},
    {"catalogue": "PLC271000", "iliac_range_mm": (21.5, 25.0), "graft_diameter_mm": 27, "length_mm": 100, "sheath_fr": 15},
    {"catalogue": "PLC271200", "iliac_range_mm": (21.5, 25.0), "graft_diameter_mm": 27, "length_mm": 120, "sheath_fr": 15},
    {"catalogue": "PLC271400", "iliac_range_mm": (21.5, 25.0), "graft_diameter_mm": 27, "length_mm": 140, "sheath_fr": 15},
]

GORE_AORTIC_EXTENDERS = [
    {"catalogue": "CXA200005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (16, 18), "diameter_mm": 20, "length_mm": 45, "sheath_fr": 15},
    {"catalogue": "CXA230005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (19, 21), "diameter_mm": 23, "length_mm": 45, "sheath_fr": 15},
    {"catalogue": "CXA260005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (22, 23), "diameter_mm": 26, "length_mm": 45, "sheath_fr": 16},
    {"catalogue": "CXA285005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (24, 26), "diameter_mm": 28.5, "length_mm": 45, "sheath_fr": 16},
    {"catalogue": "CXA320005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (27, 29), "diameter_mm": 32, "length_mm": 45, "sheath_fr": 18},
    {"catalogue": "CXA360005", "family": "Conformable AAA (Active Control)", "aortic_range_mm": (30, 32), "diameter_mm": 36, "length_mm": 45, "sheath_fr": 18},
]

GORE_ILIAC_EXTENDERS = [
    {"catalogue": "PLL161007", "iliac_range_mm": (8, 9), "diameter_mm": 10, "length_mm": 70, "sheath_fr": 12},
    {"catalogue": "PLL161207", "iliac_range_mm": (10, 11), "diameter_mm": 12, "length_mm": 70, "sheath_fr": 12},
    {"catalogue": "PLL161407", "iliac_range_mm": (12, 13.5), "diameter_mm": 14.5, "length_mm": 70, "sheath_fr": 12},
]


MEDTRONIC_BIFURCATIONS = [
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 13, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 13, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 13, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 16, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 16, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 23, "distal_diameter_mm": 16, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 13, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 13, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 13, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 16, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 16, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 25, "distal_diameter_mm": 16, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 13, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 13, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 13, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 16, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 16, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 16, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 20, "covered_length_mm": 124, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 20, "covered_length_mm": 145, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 28, "distal_diameter_mm": 20, "covered_length_mm": 166, "catheter_fr": 18},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 16, "covered_length_mm": 124, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 16, "covered_length_mm": 145, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 16, "covered_length_mm": 166, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 20, "covered_length_mm": 124, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 20, "covered_length_mm": 145, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 32, "distal_diameter_mm": 20, "covered_length_mm": 166, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 36, "distal_diameter_mm": 16, "covered_length_mm": 145, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 36, "distal_diameter_mm": 16, "covered_length_mm": 166, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 36, "distal_diameter_mm": 20, "covered_length_mm": 145, "catheter_fr": 20},
    {"family": "Endurant II", "proximal_diameter_mm": 36, "distal_diameter_mm": 20, "covered_length_mm": 166, "catheter_fr": 20},
]

MEDTRONIC_SHORT_BODIES = [
    {"family": "Endurant IIs", "proximal_diameter_mm": 23, "distal_diameter_mm": 14, "covered_length_mm": 103, "catheter_fr": 18},
    {"family": "Endurant IIs", "proximal_diameter_mm": 25, "distal_diameter_mm": 14, "covered_length_mm": 103, "catheter_fr": 18},
    {"family": "Endurant IIs", "proximal_diameter_mm": 28, "distal_diameter_mm": 14, "covered_length_mm": 103, "catheter_fr": 18},
    {"family": "Endurant IIs", "proximal_diameter_mm": 32, "distal_diameter_mm": 14, "covered_length_mm": 103, "catheter_fr": 20},
    {"family": "Endurant IIs", "proximal_diameter_mm": 36, "distal_diameter_mm": 14, "covered_length_mm": 103, "catheter_fr": 20},
]

MEDTRONIC_LIMBS = [
    {"family": "Endurant limb", "distal_diameter_mm": 10, "covered_length_mm": 82, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 10, "covered_length_mm": 93, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 10, "covered_length_mm": 124, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 10, "covered_length_mm": 156, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 10, "covered_length_mm": 199, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 13, "covered_length_mm": 82, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 13, "covered_length_mm": 93, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 13, "covered_length_mm": 124, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 13, "covered_length_mm": 156, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 13, "covered_length_mm": 199, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 16, "covered_length_mm": 82, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 16, "covered_length_mm": 93, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 16, "covered_length_mm": 124, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 16, "covered_length_mm": 156, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 16, "covered_length_mm": 199, "catheter_fr": 14},
    {"family": "Endurant limb", "distal_diameter_mm": 20, "covered_length_mm": 82, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 20, "covered_length_mm": 93, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 20, "covered_length_mm": 124, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 20, "covered_length_mm": 156, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 20, "covered_length_mm": 199, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 24, "covered_length_mm": 82, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 24, "covered_length_mm": 124, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 24, "covered_length_mm": 156, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 24, "covered_length_mm": 199, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 28, "covered_length_mm": 82, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 28, "covered_length_mm": 93, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 28, "covered_length_mm": 124, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 28, "covered_length_mm": 156, "catheter_fr": 16},
    {"family": "Endurant limb", "distal_diameter_mm": 28, "covered_length_mm": 199, "catheter_fr": 16},
]

MEDTRONIC_AORTIC_EXTENDERS = [
    {"diameter_mm": 23, "covered_length_mm": 49, "catheter_fr": 18},
    {"diameter_mm": 25, "covered_length_mm": 49, "catheter_fr": 18},
    {"diameter_mm": 28, "covered_length_mm": 49, "catheter_fr": 18},
    {"diameter_mm": 32, "covered_length_mm": 49, "catheter_fr": 20},
    {"diameter_mm": 36, "covered_length_mm": 49, "catheter_fr": 20},
]

MEDTRONIC_ILIAC_EXTENDERS = [
    {"diameter_mm": 10, "covered_length_mm": 82, "catheter_fr": 14},
    {"diameter_mm": 13, "covered_length_mm": 82, "catheter_fr": 14},
    {"diameter_mm": 20, "covered_length_mm": 82, "catheter_fr": 16},
    {"diameter_mm": 24, "covered_length_mm": 82, "catheter_fr": 16},
    {"diameter_mm": 28, "covered_length_mm": 82, "catheter_fr": 18},
]
