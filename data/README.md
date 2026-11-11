# Data

## Source — real data, not synthetic

- **Source:** Open-Meteo Air Quality API (`https://air-quality-api.open-meteo.com`),
  which serves CAMS (Copernicus Atmosphere Monitoring Service) data.
  Free, no API key. Fetched 11 Nov 2026 with `scripts/fetch_data.py`.
- **Why not CPCB directly?** CPCB's portal (`cpcb.nic.in`,
  `airquality.cpcb.gov.in`) is a JavaScript dashboard with no public
  CSV download, `data.gov.in` needs an API key, and OpenAQ's v2 API
  returned HTTP 410 (retired). So CPCB station readings could not be
  downloaded. WAQI's demo token also returned a wrong-city reading.
- **What this data is:** CAMS is a gridded atmospheric model, not a
  network of ground monitors. Its values run higher than CPCB ground
  readings, especially for PM10 in June (dust) and for ozone. Treat
  the AQI here as a **CPCB-formula index computed on modelled data** —
  good for comparing areas, months and pollutants, not as an official
  CPCB AQI for a given day.
- **Stations:** only three Delhi locations give distinct CAMS grid
  values, so those three are used: Anand Vihar (28.65, 77.31),
  RK Puram (28.56, 77.17), Najafgarh (28.60, 76.98).

## Files

| File | Contents |
|---|---|
| `aqi_hourly_raw.csv` | 11,736 hourly rows (3 stations × 163 days × 24 h), PM2.5, PM10, NO2, SO2, O3 in µg/m³, 1 Jun – 10 Nov 2026. No missing values. |
| `aqi_daily_clean.csv` | 489 station-days (163 days × 3 stations) from `scripts/clean_aqi.py`: daily pollutant averages, AQI, dominant pollutant, AQI category. |
| `aqi_monthly_summary.csv` | Average AQI by month, from `scripts/analyse_aqi.py`. |

## How the AQI is computed

CPCB sub-index formula, applied to daily averages (ozone: highest
8-hour rolling mean). AQI = the highest sub-index. **Ozone is stored
but not used in the AQI**: CAMS modelled ozone runs systematically
high and would drive the AQI on almost every day, hiding the
PM2.5/PM10 signal. CPCB's AQI needs at least three pollutants
including PM2.5 or PM10, so PM2.5 + PM10 + NO2 + SO2 is a valid
CPCB-style index. See `scripts/clean_aqi.py` for the breakpoints.
