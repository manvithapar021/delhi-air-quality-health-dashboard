# Delhi Air Quality & Health Dashboard

## Why this project exists

Delhi's air changes fast — a June dust storm, a clear September, then
November smog. A resident, a school, or a public-health team needs a
simple answer to one question: **should we issue a health advisory
today, and for which part of the city?** This project answers that
from daily AQI by area, pollutant and season. It is not charts for
their own sake: every visual maps to an advisory decision.

## Findings (computed from the data in this repo)

Dataset: 489 station-days — 3 Delhi areas, 1 June – 10 November 2026
(163 days each). AQI computed with the CPCB formula on Open-Meteo /
CAMS data; see `data/README.md` for the honesty note on that source.

1. **RK Puram is the worst area, Anand Vihar the least bad.**
   Average AQI: RK Puram 232, Najafgarh 210, Anand Vihar 187. RK Puram
   had 85 health-advisory days (AQI over 200) out of 163, against 59
   for Anand Vihar. On borderline days, the advisory decision depends
   on which part of the city you are in.
2. **June was the worst month, September the best — and November is
   climbing again.** Average AQI by month: June 349, July 193,
   August 154, September 115, October 220, November 273. June's spike
   was PM10 dust (daily PM10 averaged 566 µg/m³ in June, against 108
   in September); November's rise is the familiar winter smog pattern.
3. **Particulates drive Delhi's AQI, not gases.** PM10 was the
   dominant pollutant on 273 of 489 station-days and PM2.5 on 216;
   NO2 and SO2 never drove a single day. Cutting particulate matter
   matters far more than any gas.
4. **Advisories would be needed almost half the time.** 215 of 489
   station-days (44%) were over AQI 200 — Poor 76, Very Poor 49,
   Severe 90 days. Only 27 station-days were Good. The worst single
   day was 12 June at RK Puram: AQI 479, PM10 daily mean 1,673 µg/m³.

## How each tool is used

| Tool | Where | What it does |
|---|---|---|
| Python / Pandas | `scripts/clean_aqi.py`, `scripts/analyse_aqi.py` | Fetch, clean and analyse: daily averages, CPCB AQI, station ranking, monthly trends, advisory-day counts |
| Excel | `Delhi_AQI_Dashboard.xlsx` (built by `scripts/build_excel.py`) | Cleaned-data sheet, Summary sheet (average AQI by station × month + category counts), Charts sheet (monthly trend line, station bar) |
| Power BI | `powerbi/README.md` + `powerbi/screenshots/` | No `.pbix` is faked — a 15-minute build guide (import, DAX measures for Avg AQI / % Severe days / advisory days, exact visuals) plus screenshots of what the dashboard should look like |
| Tableau | `tableau/delhi_aqi.twb` | Workbook on the cleaned CSV with 2 worksheets (Monthly AQI Trend, Station Comparison) and a dashboard combining them |
| Flask | `app.py`, `templates/`, `static/` | Web dashboard: home page with worst station and trend charts, station table, and a health-advisory page mapping each AQI category to concrete advice |

## Data — read this before quoting any number

Real public data, fetched 11 Nov 2026 from the Open-Meteo Air Quality
API (CAMS / Copernicus model). CPCB's own portal has no public CSV
download, `data.gov.in` needs an API key, and OpenAQ's v2 API is
retired — all tried first. CAMS is a gridded model, not ground
monitors, and its values run higher than CPCB station readings,
especially June PM10 dust and ozone. Ozone is stored in the dataset
but excluded from the AQI (it would otherwise dominate almost every
day); the AQI uses PM2.5 + PM10 + NO2 + SO2, which meets CPCB's
minimum-pollutant rule. Full detail: `data/README.md`.

## Files generated locally (not in this repo)

The Excel workbook (`Delhi_AQI_Dashboard.xlsx`) and the PNG charts (`powerbi/screenshots/`, `static/images/`) are generated from the data in this repo — run `python scripts/build_excel.py` and `python scripts/make_charts.py` to recreate them. They are binary files, so they are not stored here.

## How to run locally

```bash
pip install -r requirements.txt

# Re-fetch the raw data (optional — the CSVs are already in data/)
python scripts/fetch_data.py

# Clean it and analyse it
python scripts/clean_aqi.py
python scripts/analyse_aqi.py

# Build the charts and the Excel workbook
python scripts/make_charts.py
python scripts/build_excel.py

# Run the tests
python -m pytest tests/ -v

# Start the web dashboard
python app.py
# open http://127.0.0.1:5000
```

## How to explain this in an interview

"I built a dashboard that tells Delhi residents when a health advisory
is needed. I fetched real hourly air-quality data for three Delhi
areas from Open-Meteo, cleaned it with Pandas, and computed AQI using
the CPCB formula — daily averages for PM2.5, PM10, NO2 and SO2 (ozone is stored in the data but excluded from the AQI, as explained in the README). I
found RK Puram was the worst area, June was the worst month because
of PM10 dust, and particulates, not gases, drive the AQI. I put the
same cleaned data into Excel with pivot-style summaries and charts,
wrote a step-by-step Power BI build with DAX measures, made a Tableau
workbook with a trend and a comparison view, and built a Flask app
that shows the worst station and maps each AQI category to what
people should actually do. The honest limitation is that the source
is CAMS modelled data, not CPCB ground monitors, so I say that in the
README rather than presenting the numbers as official AQI."
