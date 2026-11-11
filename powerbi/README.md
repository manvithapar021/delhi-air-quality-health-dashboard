# Power BI dashboard — build guide (about 15 minutes)

A real `.pbix` file cannot be created by a script — it is a binary file
that only Power BI Desktop can save. So this folder does **not** pretend
a `.pbix` exists. It gives you the exact steps to build the same
dashboard in Power BI Desktop (free from Microsoft), plus screenshots
of the charts the dashboard should show, generated from the same data
in `screenshots/`.

## 1. Get the data in

1. Open Power BI Desktop → **Home → Get data → Text/CSV**.
2. Pick `data/aqi_daily_clean.csv` from this project.
3. In the preview, check the types: `date` = Date, `aqi`, `pm2_5`,
   `pm10`, `nitrogen_dioxide`, `sulphur_dioxide`, `ozone` = Decimal
   number, `station`, `aqi_category`, `dominant_pollutant` = Text.
4. Click **Load**.

## 2. Add a month column and three measures

In **Data view**, add a calculated column:

```dax
Month = FORMAT('aqi_daily_clean'[date], "yyyy-MM")
```

Then in **Home → New measure**, add these three DAX measures:

```dax
Avg AQI =
AVERAGE('aqi_daily_clean'[aqi])

% Severe days =
DIVIDE(
    COUNTROWS(FILTER('aqi_daily_clean', 'aqi_daily_clean'[aqi_category] = "Severe")),
    COUNTROWS('aqi_daily_clean')
)

Advisory days (AQI > 200) =
COUNTROWS(FILTER('aqi_daily_clean', 'aqi_daily_clean'[aqi] > 200))
```

## 3. Build these visuals (one per idea)

| Visual | Fields | What it answers |
|---|---|---|
| Cards (top row) | `Avg AQI`, `% Severe days`, `Advisory days (AQI > 200)` | How bad is Delhi's air, at a glance? |
| Line chart | Axis: `Month`, Values: `Avg AQI`, Legend: `station` | When is the air worst — June dust or November smog? |
| Bar chart | Y-axis: `station`, X-axis: `Avg AQI` | Which area needs advisories first? (RK Puram) |
| Stacked column | Axis: `Month`, Values: count of `date`, Legend: `aqi_category` | How many days each month were Poor or worse? |
| Slicer | `station` and `Month` | Let the reader filter the whole page. |

## 4. Finish it

- Set the line chart's Y-axis to start at 0, and add a constant line
  at 200 labelled "Advisory threshold".
- Rename the page "Delhi AQI — Jun–Nov 2026" and save as
  `Delhi_AQI_Dashboard.pbix` in this folder.
- Publish to the Power BI service only if you want a shareable link;
  the screenshots in `screenshots/` are enough for a resume or
  LinkedIn post.

## Screenshots

These were generated from the cleaned data with Matplotlib
(`scripts/make_charts.py`), so they show exactly what the Power BI
visuals should look like:

- `screenshots/monthly_trend.png` — average AQI by month, per station
- `screenshots/station_comparison.png` — average AQI by station
- `screenshots/category_distribution.png` — days in each AQI category
- `screenshots/pollutant_drivers.png` — PM10 vs PM2.5 as the AQI driver
