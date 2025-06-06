import pandas as pd
import matplotlib.pyplot as plt
import re

df = pd.read_csv("Airline_Delay_Cause.csv")

delay_cols = ["carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]
df["total_delay_ct"] = df[delay_cols].sum(axis=1)

def parse_state(n):
    m = re.search(r",\s*([A-Z]{2}):", str(n))
    return m.group(1) if m else "Other"

STATE2REGION = {
    "CT":"Northeast","ME":"Northeast","MA":"Northeast","NH":"Northeast",
    "RI":"Northeast","VT":"Northeast","NJ":"Northeast","NY":"Northeast",
    "PA":"Northeast","IL":"Midwest","IN":"Midwest","MI":"Midwest","OH":"Midwest",
    "WI":"Midwest","IA":"Midwest","KS":"Midwest","MN":"Midwest","MO":"Midwest",
    "NE":"Midwest","ND":"Midwest","SD":"Midwest","DE":"South","FL":"South",
    "GA":"South","MD":"South","NC":"South","SC":"South","VA":"South","DC":"South",
    "WV":"South","AL":"South","KY":"South","MS":"South","TN":"South","AR":"South",
    "LA":"South","OK":"South","TX":"South","AZ":"West","CO":"West","ID":"West",
    "MT":"West","NV":"West","NM":"West","UT":"West","WY":"West","AK":"West",
    "CA":"West","HI":"West","OR":"West","WA":"West"
}

df["state"] = df["airport_name"].apply(parse_state)
df["region"] = df["state"].map(STATE2REGION).fillna("Other")

carriers = df.groupby("carrier").agg(
    total_flights=("arr_flights","sum"),
    delayed_flights=("arr_del15","sum")
).reset_index()
carriers["delay_rate"] = carriers["delayed_flights"]/carriers["total_flights"]
top10_carriers = carriers.nsmallest(10,"delay_rate")
worst10_carriers = carriers.nlargest(10,"delay_rate")

airports = df.groupby("airport").agg(
    total_flights=("arr_flights","sum"),
    delayed_flights=("arr_del15","sum")
).reset_index()
airports["delay_rate"] = airports["delayed_flights"]/airports["total_flights"]
top10_airports = airports.nsmallest(10,"delay_rate")
worst10_airports = airports.nlargest(10,"delay_rate")

monthly = df.groupby(["year","month"]).agg(
    flights=("arr_flights","sum"),
    delayed=("arr_del15","sum")
).reset_index()
monthly["delay_rate"] = monthly["delayed"]/monthly["flights"]
monthly["date"] = pd.to_datetime(monthly["year"].astype(str)+"-"+monthly["month"].astype(str)+"-01")

regional = df.groupby("region")[delay_cols+["total_delay_ct"]].sum().reset_index()
regional = regional.assign(
    weather_share=lambda x: x["weather_ct"]/x["total_delay_ct"],
    operational_share=lambda x: (x["carrier_ct"]+x["late_aircraft_ct"])/x["total_delay_ct"],
    nas_share=lambda x: x["nas_ct"]/x["total_delay_ct"]
).set_index("region")

fig, axs = plt.subplots(3,2,figsize=(16,18))
plt.subplots_adjust(hspace=0.5,bottom=0.05)

# Top 10 Most Punctual Carriers
bars = axs[0,0].barh(top10_carriers["carrier"],top10_carriers["delay_rate"],color="green")
axs[0,0].invert_yaxis()
axs[0,0].set_title("Top 10 Most Punctual Carriers")
axs[0,0].set_xlabel("Delay Rate")
for bar in bars:
    w = bar.get_width()
    axs[0,0].text(w+0.005,bar.get_y()+bar.get_height()/2,f"{w:.2%}",va="center")

# Top 10 Least Punctual Carriers
bars = axs[0,1].barh(worst10_carriers["carrier"],worst10_carriers["delay_rate"],color="red")
axs[0,1].invert_yaxis()
axs[0,1].set_title("Top 10 Least Punctual Carriers")
axs[0,1].set_xlabel("Delay Rate")
for bar in bars:
    w = bar.get_width()
    axs[0,1].text(w+0.005,bar.get_y()+bar.get_height()/2,f"{w:.2%}",va="center")

# Top 10 Most Punctual Airports
bars = axs[1,0].barh(top10_airports["airport"],top10_airports["delay_rate"],color="blue")
axs[1,0].invert_yaxis()
axs[1,0].set_title("Top 10 Most Punctual Airports")
axs[1,0].set_xlabel("Delay Rate")
for bar in bars:
    w = bar.get_width()
    axs[1,0].text(w+0.005,bar.get_y()+bar.get_height()/2,f"{w:.2%}",va="center")

# Top 10 Least Punctual Airports
bars = axs[1,1].barh(worst10_airports["airport"],worst10_airports["delay_rate"],color="orange")
axs[1,1].invert_yaxis()
axs[1,1].set_title("Top 10 Least Punctual Airports")
axs[1,1].set_xlabel("Delay Rate")
for bar in bars:
    w = bar.get_width()
    axs[1,1].text(w+0.005,bar.get_y()+bar.get_height()/2,f"{w:.2%}",va="center")

# Monthly Delay Rate Over Time
axs[2,0].plot(monthly["date"],monthly["delay_rate"],marker="o",linewidth=2)
axs[2,0].set_title("Monthly Delay Rate Over Time")
axs[2,0].set_xlabel("Date")
axs[2,0].set_ylabel("Delay Rate")
axs[2,0].tick_params(axis='x',rotation=45)
axs[2,0].grid(True)
for i,x in enumerate(monthly["date"]):
    y = monthly.loc[i,"delay_rate"]
    axs[2,0].text(x,y+0.005,f"{y:.2%}",ha="center")

# Regional Delay Shares
ax = axs[2,1]
regional[['weather_share','operational_share','nas_share']].plot(
    kind="bar",stacked=True,ax=ax,figsize=(8,6)
)
ax.set_title("Regional Delay Shares")
ax.set_xlabel("Region")
ax.set_ylabel("Share of Total Delay")
ax.legend(loc="upper right")
for p in ax.patches:
    if p.get_width() > 0:
        width = p.get_width()
        ax.text(p.get_x()+p.get_width()/2,p.get_y()+p.get_height()/2,f"{width:.2%}",ha="center",va="center",fontsize=8,color="white")

plt.tight_layout()
plt.show()
