"""
Delhi Air Quality & Health Dashboard — Flask app.

Reads the cleaned daily AQI data (data/aqi_daily_clean.csv) and shows:
  /           dashboard: latest day, worst station, monthly trend chart,
              station table with average AQI and advisory days
  /advisory  health advice mapped to each AQI category, plus the
              current category for every station
  /stations  full station table, sorted worst first

Run:  python app.py
Then open http://127.0.0.1:5000 in a browser.
"""
import os

import pandas as pd
from flask import Flask, render_template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "aqi_daily_clean.csv")

app = Flask(__name__)

# Health advice per CPCB AQI category — what a resident should actually do.
ADVICE = {
    "Good": ("Minimal impact.", "Enjoy outdoor activities as normal."),
    "Satisfactory": ("Minor breathing discomfort for sensitive people.",
                     "Sensitive people should reduce prolonged outdoor exertion."),
    "Moderate": ("Breathing discomfort for people with lung or heart disease.",
                 "People with asthma or heart disease should reduce outdoor exertion."),
    "Poor": ("Breathing discomfort for most people on prolonged exposure.",
             "Reduce outdoor activity; sensitive groups should stay indoors."),
    "Very Poor": ("Respiratory illness on prolonged exposure.",
                  "Avoid outdoor activity; wear a mask (N95) if you must go out."),
    "Severe": ("Serious respiratory effects, even for healthy people.",
               "Stay indoors; avoid all outdoor exercise; wear an N95 mask outside."),
}


def load_data():
    """Load the cleaned daily data, newest first."""
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df.sort_values("date", ascending=False)


def station_summary(df):
    """One row per station: average AQI, worst day, advisory days."""
    rows = []
    for station, group in df.groupby("station"):
        latest = group.iloc[0]
        rows.append({
            "station": station,
            "avg_aqi": round(group["aqi"].mean(), 1),
            "max_aqi": int(group["aqi"].max()),
            "latest_aqi": int(latest["aqi"]),
            "latest_category": latest["aqi_category"],
            "latest_date": latest["date"].strftime("%d %b %Y"),
            "advisory_days": int((group["aqi"] > 200).sum()),
            "total_days": len(group),
        })
    return sorted(rows, key=lambda r: r["avg_aqi"], reverse=True)


@app.route("/")
def index():
    df = load_data()
    latest_date = df["date"].max().strftime("%d %B %Y")
    stations = station_summary(df)
    worst = stations[0]
    return render_template("index.html", latest_date=latest_date,
                           stations=stations, worst=worst)


@app.route("/advisory")
def advisory():
    df = load_data()
    stations = station_summary(df)
    return render_template("advisory.html", stations=stations, advice=ADVICE)


@app.route("/stations")
def stations():
    df = load_data()
    stations = station_summary(df)
    return render_template("stations.html", stations=stations)


if __name__ == "__main__":
    app.run(debug=True)
