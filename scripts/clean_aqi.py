"""
Clean hourly Delhi air-quality data into a daily dataset with CPCB AQI.

Steps:
  1. Read data/aqi_hourly_raw.csv (from scripts/fetch_data.py).
  2. Drop rows with a missing pollutant value; drop exact duplicates.
  3. Keep only station-days with at least 18 hourly records, so a daily
     average is not based on a couple of hours.
  4. Daily average for PM2.5, PM10, NO2 and SO2. For ozone, use the
     highest 8-hour rolling mean of the day, as CPCB does.
  5. Compute the CPCB sub-index for PM2.5, PM10, NO2 and SO2 and take
     the maximum as the day's AQI. The pollutant with the maximum is
     recorded as the "dominant pollutant". Ozone is stored in the
     dataset but NOT used in the AQI: CAMS modelled ozone runs
     systematically high against CPCB ground readings and, if included,
     would drive the AQI on almost every day (247 of 489 station-days),
     hiding the PM2.5/PM10 signal that actually decides Delhi's AQI.
     CPCB's AQI needs at least three pollutants including PM2.5 or
     PM10, so PM2.5 + PM10 + NO2 + SO2 is a valid CPCB-style index.
  6. Add the CPCB AQI category for the day.

CPCB sub-index breakpoints (concentration in ug/m3 -> AQI):
  PM2.5: 0-30, 31-60, 61-90, 91-120, 121-250, >250
  PM10:  0-50, 51-100, 101-250, 251-350, 351-430, >430
  NO2:   0-40, 41-80, 81-180, 181-280, 281-400, >400
  SO2:   0-40, 41-80, 81-380, 381-800, 801-1600, >1600
  O3:    0-50, 51-100, 101-168, 169-208, 209-748, >748
  AQI bands: 0-50, 51-100, 101-200, 201-300, 301-400, 401-500.

Run:  python scripts/clean_aqi.py
Output: data/aqi_daily_clean.csv
"""
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# (low concentration, high concentration, low AQI, high AQI) per pollutant.
# Bands are continuous (each band starts where the last ended) so every
# concentration falls in exactly one band.
BREAKPOINTS = {
    "pm2_5": [(0, 30, 0, 50), (30, 60, 51, 100), (60, 90, 101, 200),
              (90, 120, 201, 300), (120, 250, 301, 400), (250, 1000, 401, 500)],
    "pm10": [(0, 50, 0, 50), (50, 100, 51, 100), (100, 250, 101, 200),
             (250, 350, 201, 300), (350, 430, 301, 400), (430, 2000, 401, 500)],
    "nitrogen_dioxide": [(0, 40, 0, 50), (40, 80, 51, 100), (80, 180, 101, 200),
                         (180, 280, 201, 300), (280, 400, 301, 400),
                         (400, 1000, 401, 500)],
    "sulphur_dioxide": [(0, 40, 0, 50), (40, 80, 51, 100), (80, 380, 101, 200),
                        (380, 800, 201, 300), (800, 1600, 301, 400),
                        (1600, 5000, 401, 500)],
    "ozone": [(0, 50, 0, 50), (50, 100, 51, 100), (100, 168, 101, 200),
              (168, 208, 201, 300), (208, 748, 301, 400), (748, 2000, 401, 500)],
}

CATEGORIES = [(0, 50, "Good"), (51, 100, "Satisfactory"), (101, 200, "Moderate"),
              (201, 300, "Poor"), (301, 400, "Very Poor"), (401, 500, "Severe")]


def sub_index(concentration, breakpoints):
    """Convert one pollutant concentration to its CPCB sub-index (0-500)."""
    for low_c, high_c, low_i, high_i in breakpoints:
        if low_c <= concentration <= high_c:
            return round((high_i - low_i) / (high_c - low_c)
                         * (concentration - low_c) + low_i)
    return 500  # above the top breakpoint


def aqi_category(aqi):
    """Return the CPCB category name for an AQI value."""
    for low, high, name in CATEGORIES:
        if low <= aqi <= high:
            return name
    return "Severe"


def clean(raw_path, clean_path):
    """Read hourly data, return and save the daily cleaned DataFrame."""
    df = pd.read_csv(raw_path, parse_dates=["datetime"])
    df = df.drop_duplicates().dropna(subset=["pm2_5", "pm10",
                                             "nitrogen_dioxide",
                                             "sulphur_dioxide", "ozone"])
    df["date"] = df["datetime"].dt.date

    # Ozone: highest 8-hour rolling mean within each station-day.
    df = df.sort_values(["station", "datetime"])
    df["ozone_8h"] = (df.groupby("station")["ozone"]
                        .transform(lambda s: s.rolling(8, min_periods=8).mean()))

    daily_rows = []
    for (station, date), group in df.groupby(["station", "date"]):
        if len(group) < 18:
            continue  # not enough hours for a trustworthy daily average
        row = {"station": station, "date": date,
               "latitude": group["latitude"].iloc[0],
               "longitude": group["longitude"].iloc[0],
               "hours_recorded": len(group),
               "pm2_5": round(group["pm2_5"].mean(), 1),
               "pm10": round(group["pm10"].mean(), 1),
               "nitrogen_dioxide": round(group["nitrogen_dioxide"].mean(), 1),
               "sulphur_dioxide": round(group["sulphur_dioxide"].mean(), 1),
               "ozone": round(group["ozone_8h"].max(), 1)}
        # AQI is the highest sub-index; that pollutant "drives" the day.
        # Ozone is excluded (see step 5 in the module docstring).
        aqi_pollutants = ["pm2_5", "pm10", "nitrogen_dioxide",
                          "sulphur_dioxide"]
        sub_indexes = {p: sub_index(row[p], BREAKPOINTS[p])
                       for p in aqi_pollutants}
        dominant = max(sub_indexes, key=sub_indexes.get)
        row["aqi"] = sub_indexes[dominant]
        row["dominant_pollutant"] = dominant
        row["aqi_category"] = aqi_category(row["aqi"])
        daily_rows.append(row)

    daily = pd.DataFrame(daily_rows).sort_values(["date", "station"])
    daily.to_csv(clean_path, index=False)
    return daily


def main():
    raw_path = os.path.join(DATA_DIR, "aqi_hourly_raw.csv")
    clean_path = os.path.join(DATA_DIR, "aqi_daily_clean.csv")
    daily = clean(raw_path, clean_path)
    print(f"Saved {len(daily)} station-days to {clean_path}")
    print(f"Date range: {daily['date'].min()} to {daily['date'].max()}")
    print("Days by category:")
    print(daily["aqi_category"].value_counts().to_string())


if __name__ == "__main__":
    main()
