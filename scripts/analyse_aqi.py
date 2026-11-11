"""
Analyse the cleaned daily Delhi AQI data and print the findings.

Answers, in plain terms:
  1. Which station is worst on average, and by how much?
  2. Which were the worst days overall?
  3. How does AQI change by month / season?
  4. Which pollutant drives the AQI most often?
  5. How many days were in each AQI category, and how many days
     would have needed a health advisory (AQI over 200, i.e. Poor
     or worse)?

Run:  python scripts/analyse_aqi.py
Input: data/aqi_daily_clean.csv (from scripts/clean_aqi.py)
Output: printed summary + analysis/aqi_summary.csv (monthly averages)
"""
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def analyse(clean_path):
    """Load the daily data and return a dict of summary tables."""
    df = pd.read_csv(clean_path, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    station_avg = (df.groupby("station")["aqi"].agg(["mean", "max", "median"])
                     .round(1).sort_values("mean", ascending=False))
    worst_days = (df.sort_values("aqi", ascending=False)
                    .head(10)[["date", "station", "aqi", "aqi_category",
                               "dominant_pollutant", "pm2_5", "pm10"]])
    monthly = (df.groupby("month")["aqi"].mean().round(1)
                 .rename("avg_aqi").reset_index())
    dominant = df["dominant_pollutant"].value_counts()
    categories = df["aqi_category"].value_counts()
    advisory_days = df[df["aqi"] > 200].groupby("station").size()
    return {"df": df, "station_avg": station_avg, "worst_days": worst_days,
            "monthly": monthly, "dominant": dominant,
            "categories": categories, "advisory_days": advisory_days}


def main():
    clean_path = os.path.join(DATA_DIR, "aqi_daily_clean.csv")
    results = analyse(clean_path)
    df = results["df"]

    print(f"Station-days analysed: {len(df)} "
          f"({df['date'].min().date()} to {df['date'].max().date()})\n")

    print("1) Average AQI by station (higher = worse air)")
    print(results["station_avg"].to_string())
    print("\n2) Worst 10 station-days")
    print(results["worst_days"].to_string(index=False))
    print("\n3) Average AQI by month")
    print(results["monthly"].to_string(index=False))
    print("\n4) Pollutant driving the AQI most often")
    print(results["dominant"].to_string())
    print("\n5) Days in each AQI category (all stations combined)")
    print(results["categories"].to_string())
    print("\n6) Health-advisory days (AQI over 200) by station")
    print(results["advisory_days"].to_string())

    out_path = os.path.join(DATA_DIR, "aqi_monthly_summary.csv")
    results["monthly"].to_csv(out_path, index=False)
    print(f"\nMonthly summary saved to {out_path}")


if __name__ == "__main__":
    main()
