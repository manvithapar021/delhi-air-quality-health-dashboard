"""
Generate the charts used by the Flask app and the Power BI screenshots.

Run:  python scripts/make_charts.py
Input: data/aqi_daily_clean.csv
Output: static/images/*.png and powerbi/screenshots/*.png
"""
import os

import matplotlib
matplotlib.use("Agg")  # no screen needed, just save image files
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "aqi_daily_clean.csv")

CATEGORY_COLOURS = {"Good": "#2ca02c", "Satisfactory": "#7fbf7f",
                    "Moderate": "#ffbf00", "Poor": "#ff7f0e",
                    "Very Poor": "#d62728", "Severe": "#8b0000"}


def save(fig, path):
    """Save a figure and close it so memory stays clean."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def monthly_trend(df, path):
    """Average AQI by month, one line per station."""
    monthly = (df.assign(month=df["date"].dt.to_period("M").astype(str))
                 .groupby(["month", "station"])["aqi"].mean().unstack())
    fig, ax = plt.subplots(figsize=(9, 4.5))
    monthly.plot(ax=ax, marker="o")
    ax.axhspan(201, 500, color="red", alpha=0.07)
    ax.text(0.01, 0.95, "Shaded = health-advisory zone (AQI over 200)",
            transform=ax.transAxes, fontsize=8)
    ax.set_title("Average AQI by month — Delhi, Jun–Nov 2026")
    ax.set_ylabel("Average AQI")
    ax.set_xlabel("Month")
    ax.legend(title="Station")
    save(fig, path)


def station_comparison(df, path):
    """Average AQI by station, as a bar chart."""
    avg = df.groupby("station")["aqi"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(avg.index, avg.values, color="#1f77b4")
    for i, value in enumerate(avg.values):
        ax.text(value + 5, i, f"{value:.0f}", va="center")
    ax.set_xlim(0, max(avg.values) * 1.2)
    ax.set_title("Average AQI by station — Jun–Nov 2026 (higher = worse air)")
    ax.set_xlabel("Average AQI")
    save(fig, path)


def category_distribution(df, path):
    """How many station-days fell in each AQI category."""
    order = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]
    counts = df["aqi_category"].value_counts().reindex(order).fillna(0)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(counts.index, counts.values,
           color=[CATEGORY_COLOURS[c] for c in counts.index])
    ax.set_title("Station-days in each AQI category (489 station-days)")
    ax.set_ylabel("Days")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    save(fig, path)


def pollutant_drivers(df, path):
    """Which pollutant drove the AQI most often."""
    counts = df["dominant_pollutant"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(counts.index, counts.values, color="#2ca02c")
    ax.set_title("Pollutant driving the AQI (days out of 489)")
    ax.set_ylabel("Days")
    save(fig, path)


def main():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    static_dir = os.path.join(BASE_DIR, "static", "images")
    shots_dir = os.path.join(BASE_DIR, "powerbi", "screenshots")
    monthly_trend(df, os.path.join(static_dir, "monthly_trend.png"))
    monthly_trend(df, os.path.join(shots_dir, "monthly_trend.png"))
    station_comparison(df, os.path.join(static_dir, "station_comparison.png"))
    station_comparison(df, os.path.join(shots_dir, "station_comparison.png"))
    category_distribution(df, os.path.join(shots_dir, "category_distribution.png"))
    pollutant_drivers(df, os.path.join(shots_dir, "pollutant_drivers.png"))


if __name__ == "__main__":
    main()
