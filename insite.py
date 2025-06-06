import pandas as pd

carriers = pd.read_excel("delay_metrics.xlsx", sheet_name="carriers_overview")
airports = pd.read_excel("delay_metrics.xlsx", sheet_name="airports_overview")
ca_mix_car = pd.read_excel("delay_metrics.xlsx", sheet_name="cause_mix_carrier")
monthly = pd.read_excel("delay_metrics.xlsx", sheet_name="monthly_delay_rate")
regions = pd.read_excel("delay_metrics.xlsx", sheet_name="regional_shares")

best_carriers = carriers.nsmallest(5, "delay_rate")
worst_carriers = carriers.nlargest(5, "delay_rate")
print("TOP-5 авиакомпаний по пунктуальности:")
print(best_carriers[["carrier", "delay_rate", "minutes_per_flight"]].to_string(index=False))
print("\nANTI-TOP-5 авиакомпаний:")
print(worst_carriers[["carrier", "delay_rate", "minutes_per_flight"]].to_string(index=False))

best_airports = airports.nsmallest(5, "delay_rate")
worst_airports = airports.nlargest(5, "delay_rate")
print("\nTOP-5 аэропортов по пунктуальности:")
print(best_airports[["airport", "delay_rate", "minutes_per_flight"]].to_string(index=False))
print("\nANTI-TOP-5 аэропортов:")
print(worst_airports[["airport", "delay_rate", "minutes_per_flight"]].to_string(index=False))

print("\nПеревозчики с высоким % Carrier Delay:")
top_carriage = ca_mix_car.nlargest(5, "share_carrier")[["carrier", "share_carrier"]]
top_carriage["share_carrier"] = top_carriage["share_carrier"].map(lambda x: f"{x:.2%}")
print(top_carriage.to_string(index=False))

print("\nПеревозчики с высоким % Late Aircraft Delay:")
top_late = ca_mix_car.nlargest(5, "share_late_aircraft")[["carrier", "share_late_aircraft"]]
top_late["share_late_aircraft"] = top_late["share_late_aircraft"].map(lambda x: f"{x:.2%}")
print(top_late.to_string(index=False))

monthly["date"] = pd.to_datetime(monthly["year"].astype(str) + "-" + monthly["month"].astype(str) + "-01")
peak_row = monthly.loc[monthly["delay_rate"].idxmax()]
trough_row = monthly.loc[monthly["delay_rate"].idxmin()]
print(f"\nПИК задержек: {peak_row['date']:%B %Y} — {peak_row['delay_rate']:.2%}")
print(f"МИНИМУМ задержек: {trough_row['date']:%B %Y} — {trough_row['delay_rate']:.2%}")

monthly = monthly.sort_values("date")
if len(monthly) >= 2:
    last, prev = monthly.iloc[-1], monthly.iloc[-2]
    mom = (last["delay_rate"] - prev["delay_rate"]) / prev["delay_rate"]
    print(f"MoM ({last['date']:%b %Y}): {mom:+.2%} ({prev['delay_rate']:.2%} → {last['delay_rate']:.2%})")

print("\nRegional Shares:")
regions_sorted = regions.sort_values("weather_share", ascending=False)[["region", "weather_share", "operational_share", "nas_share"]]
regions_sorted["weather_share"] = regions_sorted["weather_share"].map(lambda x: f"{x:.2%}")
regions_sorted["operational_share"] = regions_sorted["operational_share"].map(lambda x: f"{x:.2%}")
regions_sorted["nas_share"] = regions_sorted["nas_share"].map(lambda x: f"{x:.2%}")
print(regions_sorted.to_string(index=False))
