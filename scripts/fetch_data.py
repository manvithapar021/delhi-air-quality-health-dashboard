"""
Fetch real Delhi air-quality data and save it as raw hourly CSV.

Source: Open-Meteo Air Quality API (https://air-quality-api.open-meteo.com),
which serves CAMS (Copernicus Atmosphere Monitoring Service) data.
Free, no API key needed. CPCB's own portal and OpenAQ were tried first:
- cpcb.nic.in / airquality.cpcb.gov.in is a JavaScript dashboard with no
  public CSV download, and data.gov.in needs an API key.
- api.openaq.org/v2 returned HTTP 410 (the v2 API has been retired).

Because CAMS is a gridded model (about 0.4-degree cells), only three
Delhi locations give distinct values. Those three are used as the
"stations" and their coordinates are recorded in the CSV and README,
so nobody mistakes this for CPCB monitoring-station readings.

Stations (latitude, longitude):
  - Anand Vihar  (east Delhi)   28.65, 77.31
  - RK Puram     (south Delhi)  28.56, 77.17
  - Najafgarh    (west Delhi)   28.60, 76.98

Date range: 1 June 2026 - 10 November 2026 (monsoon through the
post-Diwali / early-winter smog period).

Run:  python scripts/fetch_data.py
Output: data/aqi_hourly_raw.csv  (hourly PM2.5, PM10, NO2, SO2, O3 in ug/m3)
"""
import csv
import os
import sys

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

STATIONS = {
    "Anand Vihar": (28.65, 77.31),
    "RK Puram": (28.56, 77.17),
    "Najafgarh": (28.60, 76.98),
}
START_DATE = "2026-06-01"
END_DATE = "2026-11-10"
API_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
POLLUTANTS = ["pm2_5", "pm10", "nitrogen_dioxide", "sulphur_dioxide", "ozone"]


def fetch_station(station, lat, lon):
    """Fetch hourly pollutant data for one location. Returns a list of rows."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(POLLUTANTS),
        "start_date": START_DATE,
        "end_date": END_DATE,
        "timezone": "Asia/Kolkata",
    }
    response = requests.get(API_URL, params=params, timeout=120)
    response.raise_for_status()
    hourly = response.json()["hourly"]
    rows = []
    for i, timestamp in enumerate(hourly["time"]):
        row = {"station": station, "latitude": lat, "longitude": lon,
               "datetime": timestamp}
        for pollutant in POLLUTANTS:
            row[pollutant] = hourly[pollutant][i]
        rows.append(row)
    return rows


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "aqi_hourly_raw.csv")
    all_rows = []
    for station, (lat, lon) in STATIONS.items():
        print(f"Fetching {station} ({lat}, {lon}) ...")
        rows = fetch_station(station, lat, lon)
        print(f"  {len(rows)} hourly records")
        all_rows.extend(rows)

    fieldnames = ["station", "latitude", "longitude", "datetime"] + POLLUTANTS
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Saved {len(all_rows)} rows to {out_path}")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        print("Check your internet connection and try again.", file=sys.stderr)
        sys.exit(1)
