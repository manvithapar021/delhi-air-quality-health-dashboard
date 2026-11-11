"""Tests for the Delhi AQI dashboard.

Run from the project root:  python -m pytest tests/ -v
(or: python -m unittest discover -s tests -v)
"""
import os
import sys
import xml.etree.ElementTree as ET

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from clean_aqi import aqi_category, sub_index, BREAKPOINTS  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_sub_index_known_points():
    """CPCB PM2.5 breakpoints: 30 -> 50, 60 -> 100, 90 -> 200, 120 -> 300."""
    cases = [(0, 0), (30, 50), (60, 100), (90, 200), (120, 300), (250, 400)]
    for concentration, expected in cases:
        assert sub_index(concentration, BREAKPOINTS["pm2_5"]) == expected


def test_sub_index_no_gaps():
    """Every concentration in 0-500 must land in a band, never default to 500."""
    for pollutant, breakpoints in BREAKPOINTS.items():
        for concentration in [30.7, 60.5, 90.2, 120.9, 250.1, 431.5]:
            assert sub_index(concentration, breakpoints) < 500


def test_aqi_category():
    assert aqi_category(25) == "Good"
    assert aqi_category(75) == "Satisfactory"
    assert aqi_category(150) == "Moderate"
    assert aqi_category(250) == "Poor"
    assert aqi_category(350) == "Very Poor"
    assert aqi_category(450) == "Severe"


def test_cleaned_data_shape():
    df = pd.read_csv(os.path.join(BASE_DIR, "data", "aqi_daily_clean.csv"),
                     parse_dates=["date"])
    assert len(df) == 489
    assert set(df["station"]) == {"Anand Vihar", "RK Puram", "Najafgarh"}
    assert df["aqi"].between(0, 500).all()
    assert df["aqi_category"].isin(
        ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]).all()
    assert df["date"].min().date().isoformat() == "2026-06-01"
    assert df["date"].max().date().isoformat() == "2026-11-10"


def test_tableau_workbook_parses():
    tree = ET.parse(os.path.join(BASE_DIR, "tableau", "delhi_aqi.twb"))
    root = tree.getroot()
    assert root.tag == "workbook"
    worksheets = [w.get("name") for w in root.iter("worksheet")]
    assert "Monthly AQI Trend" in worksheets
    assert "Station Comparison" in worksheets
    dashboards = [d.get("name") for d in root.iter("dashboard")]
    assert "Delhi AQI Dashboard" in dashboards


def test_excel_workbook():
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(BASE_DIR, "Delhi_AQI_Dashboard.xlsx"))
    assert wb.sheetnames == ["Cleaned Data", "Summary", "Charts"]
    assert wb["Cleaned Data"].max_row == 490  # header + 489 rows
    assert len(wb["Charts"]._charts) == 2
