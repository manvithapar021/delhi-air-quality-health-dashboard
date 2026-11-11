"""
Build the Excel workbook for the Delhi AQI dashboard.

Run:  python scripts/build_excel.py
Input: data/aqi_daily_clean.csv
Output: Delhi_AQI_Dashboard.xlsx with three sheets:
  - Cleaned Data: every station-day (date, station, pollutants, AQI, category)
  - Summary: average AQI by station and month (a pivot-style table),
    plus days in each AQI category
  - Charts: monthly AQI trend (line) and station comparison (bar),
    built from the Summary sheet so they update if the data changes.
"""
import os

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "aqi_daily_clean.csv")
OUT_PATH = os.path.join(BASE_DIR, "Delhi_AQI_Dashboard.xlsx")


def add_sheet_with_rows(wb, title, df):
    """Write a DataFrame to a new sheet with bold headers and sized columns."""
    ws = wb.create_sheet(title)
    ws.append(list(df.columns))
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for row in df.itertuples(index=False):
        ws.append(list(row))
    for i, column in enumerate(df.columns, start=1):
        width = max(len(str(column)) + 2,
                    min(22, df[column].astype(str).str.len().max() + 2))
        ws.column_dimensions[get_column_letter(i)].width = width
    return ws


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    wb = Workbook()
    wb.remove(wb.active)  # start with no default blank sheet

    # 1) Cleaned data, exactly as in the CSV.
    add_sheet_with_rows(wb, "Cleaned Data", df.drop(columns=["month"]))

    # 2) Summary: average AQI by station (rows) and month (columns).
    pivot = (df.pivot_table(index="station", columns="month",
                            values="aqi", aggfunc="mean").round(1))
    pivot_ws = wb.create_sheet("Summary")
    pivot_ws.append(["Station"] + list(pivot.columns) + ["Overall avg"])
    for cell in pivot_ws[1]:
        cell.font = Font(bold=True)
    for station in pivot.index:
        pivot_ws.append([station] + list(pivot.loc[station])
                        + [round(df[df["station"] == station]["aqi"].mean(), 1)])
    pivot_ws.append([])  # blank row, then the category counts
    pivot_ws.append(["AQI category", "Station-days"])
    for cell in pivot_ws[pivot_ws.max_row]:
        cell.font = Font(bold=True)
    order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    for category in order:
        count = int((df["aqi_category"] == category).sum())
        pivot_ws.append([category, count])

    # 3) Charts, reading from the Summary sheet.
    charts_ws = wb.create_sheet("Charts")
    charts_ws["A1"] = "Monthly average AQI (all stations)"
    charts_ws["A1"].font = Font(bold=True, size=13)
    monthly = (df.groupby("month")["aqi"].mean().round(1)
                 .reset_index().rename(columns={"aqi": "Avg AQI"}))
    charts_ws.append([])  # row 2
    charts_ws.append(list(monthly.columns))  # row 3 = header
    for row in monthly.itertuples(index=False):
        charts_ws.append(list(row))
    line = LineChart()
    line.title = "Monthly average AQI — Delhi, Jun–Nov 2026"
    line.y_axis.title = "Average AQI"
    line.x_axis.title = "Month"
    data = Reference(charts_ws, min_col=2, min_row=3,
                     max_row=3 + len(monthly))
    cats = Reference(charts_ws, min_col=1, min_row=4,
                     max_row=3 + len(monthly))
    line.add_data(data, titles_from_data=True)
    line.set_categories(cats)
    charts_ws.add_chart(line, "A10")

    station_avg = (df.groupby("station")["aqi"].mean().round(1)
                     .reset_index().rename(columns={"aqi": "avg_aqi"}))
    start_row = 3 + len(monthly) + 2
    charts_ws.cell(row=start_row, column=1, value="Station").font = Font(bold=True)
    charts_ws.cell(row=start_row, column=2, value="Avg AQI").font = Font(bold=True)
    for i, row in enumerate(station_avg.itertuples(index=False), start=1):
        charts_ws.cell(row=start_row + i, column=1, value=row.station)
        charts_ws.cell(row=start_row + i, column=2, value=row.avg_aqi)
    bar = BarChart()
    bar.type = "col"
    bar.title = "Average AQI by station — Jun–Nov 2026"
    bar.y_axis.title = "Average AQI"
    bar_data = Reference(charts_ws, min_col=2, min_row=start_row,
                         max_row=start_row + len(station_avg))
    bar_cats = Reference(charts_ws, min_col=1, min_row=start_row + 1,
                         max_row=start_row + len(station_avg))
    bar.add_data(bar_data, titles_from_data=True)
    bar.set_categories(bar_cats)
    charts_ws.add_chart(bar, f"A{start_row + len(station_avg) + 2}")

    wb.save(OUT_PATH)
    print(f"Saved {OUT_PATH} "
          f"({len(df)} cleaned rows, {len(monthly)} months, "
          f"{len(station_avg)} stations)")


if __name__ == "__main__":
    main()
