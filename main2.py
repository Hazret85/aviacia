from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd



INPUT_CSV =  "Airline_Delay_Cause.csv"
OUTPUT_XLSX = "delay_metrics.xlsx"

# Грубая карта регионов США по двухбуквенным штатам
STATE2REGION = {
    # Northeast
    "CT": "Northeast", "ME": "Northeast", "MA": "Northeast", "NH": "Northeast",
    "RI": "Northeast", "VT": "Northeast", "NJ": "Northeast", "NY": "Northeast",
    "PA": "Northeast",
    # Midwest
    "IL": "Midwest", "IN": "Midwest", "MI": "Midwest", "OH": "Midwest",
    "WI": "Midwest", "IA": "Midwest", "KS": "Midwest", "MN": "Midwest",
    "MO": "Midwest", "NE": "Midwest", "ND": "Midwest", "SD": "Midwest",
    # South
    "DE": "South", "FL": "South", "GA": "South", "MD": "South",
    "NC": "South", "SC": "South", "VA": "South", "DC": "South",
    "WV": "South", "AL": "South", "KY": "South", "MS": "South",
    "TN": "South", "AR": "South", "LA": "South", "OK": "South",
    "TX": "South",
    # West
    "AZ": "West", "CO": "West", "ID": "West", "MT": "West",
    "NV": "West", "NM": "West", "UT": "West", "WY": "West",
    "AK": "West", "CA": "West", "HI": "West", "OR": "West",
    "WA": "West",
}



def parse_state(airport_name: str) -> str | None:

    m = re.search(r",\s*([A-Z]{2}):", str(airport_name))
    return m.group(1) if m else None


def minutes_total(df: pd.DataFrame) -> pd.Series:
    cols = [
        "carrier_ct",
        "weather_ct",
        "nas_ct",
        "security_ct",
        "late_aircraft_ct",
    ]
    return df[cols].sum(axis=1)


df = pd.read_csv(INPUT_CSV)


delay_cols = [
    "carrier_ct",
    "weather_ct",
    "nas_ct",
    "security_ct",
    "late_aircraft_ct",
]
df["total_delay_ct"] = df[delay_cols].sum(axis=1)


carriers_overview = (
    df.groupby(["carrier", "carrier_name"], as_index=False)
      .agg(total_flights=("arr_flights", "sum"),
           delayed_flights=("arr_del15", "sum"))
)
carriers_overview["delay_rate"] = (
    carriers_overview["delayed_flights"] / carriers_overview["total_flights"]
)
carriers_overview["minutes_per_flight"] = (
    df.groupby(["carrier"])["total_delay_ct"].sum().values
    / carriers_overview["total_flights"]
)

airports_overview = (
    df.groupby(["airport", "airport_name"], as_index=False)
      .agg(total_flights=("arr_flights", "sum"),
           delayed_flights=("arr_del15", "sum"))
)
airports_overview["delay_rate"] = (
    airports_overview["delayed_flights"] / airports_overview["total_flights"]
)
airports_overview["minutes_per_flight"] = (
    df.groupby(["airport"])["total_delay_ct"].sum().values
    / airports_overview["total_flights"]
)


cause_mix_carrier = (
    df.groupby("carrier")[delay_cols + ["total_delay_ct"]].sum()
      .assign(**{
          f"share_{c.replace('_ct', '')}": lambda d, c=c:
              d[c] / d["total_delay_ct"]
          for c in delay_cols
      })
      .reset_index()
)

cause_mix_airport = (
    df.groupby("airport")[delay_cols + ["total_delay_ct"]].sum()
      .assign(**{
          f"share_{c.replace('_ct', '')}": lambda d, c=c:
              d[c] / d["total_delay_ct"]
          for c in delay_cols
      })
      .reset_index()
)


monthly = (
    df.groupby(["year", "month"], as_index=False)
      .agg(flights=("arr_flights", "sum"),
           delayed=("arr_del15", "sum"))
)
monthly["delay_rate"] = monthly["delayed"] / monthly["flights"]

# Стандартное отклонение delay_rate по месяцам
carrier_monthly = (
    df.groupby(["carrier", "year", "month"])
      .agg(flights=("arr_flights", "sum"), delayed=("arr_del15", "sum"))
      .reset_index()
)
carrier_monthly["delay_rate"] = carrier_monthly["delayed"] / carrier_monthly["flights"]
carrier_stability = (
    carrier_monthly.groupby("carrier")["delay_rate"]
      .agg(std_delay_rate="std")
      .reset_index()
)

airport_monthly = (
    df.groupby(["airport", "year", "month"])
      .agg(flights=("arr_flights", "sum"), delayed=("arr_del15", "sum"))
      .reset_index()
)
airport_monthly["delay_rate"] = airport_monthly["delayed"] / airport_monthly["flights"]
airport_stability = (
    airport_monthly.groupby("airport")["delay_rate"]
      .agg(std_delay_rate="std")
      .reset_index()
)


df["state"] = df["airport_name"].apply(parse_state)
df["region"] = df["state"].map(STATE2REGION).fillna("Other")

regional = (
    df.groupby("region")[delay_cols + ["total_delay_ct"]].sum()
      .reset_index()
)
regional["weather_share"] = regional["weather_ct"] / regional["total_delay_ct"]
regional["operational_share"] = (
    (regional["carrier_ct"] + regional["late_aircraft_ct"])
    / regional["total_delay_ct"]
)
regional["nas_share"] = regional["nas_ct"] / regional["total_delay_ct"]

regional_shares = regional[
    [
        "region",
        "weather_share",
        "operational_share",
        "nas_share",
    ]
]


with pd.ExcelWriter(OUTPUT_XLSX, engine="xlsxwriter") as writer:
    carriers_overview.to_excel(writer, sheet_name="carriers_overview", index=False)
    airports_overview.to_excel(writer, sheet_name="airports_overview", index=False)
    cause_mix_carrier.to_excel(writer, sheet_name="cause_mix_carrier", index=False)
    cause_mix_airport.to_excel(writer, sheet_name="cause_mix_airport", index=False)
    monthly.to_excel(writer, sheet_name="monthly_delay_rate", index=False)
    carrier_stability.to_excel(writer, sheet_name="carrier_stability", index=False)
    airport_stability.to_excel(writer, sheet_name="airport_stability", index=False)
    regional_shares.to_excel(writer, sheet_name="regional_shares", index=False)

print(f"✅ Метрики успешно рассчитаны и сохранены в {OUTPUT_XLSX.resolve()}")
