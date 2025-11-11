# This dataset was scraped from nextspaceflight.com and includes all the space missions since the beginning of Space Race between the USA and the Soviet Union in 1957!
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

from iso3166 import countries

pd.options.display.float_format = '{:,.2f}'.format

# TODO Load the Data
df_data = pd.read_csv('mission_launches.csv')

# TODO Preliminary Data Exploration
print(f"Shape of the data:\n{df_data.shape}\n")
print(f"Columns name of the data:\n{df_data.columns}\n")

print(f"Are there any NaN values:\n{df_data.isna().values.any()}\n")
for column in df_data:
    print(f'Missing values for {column}\n{df_data[column].isna().values.any()}\n')

print(f"Are there any duplicate values:\n{df_data.duplicated().values.any()}\n")

# TODO Data Cleaning
df_data.drop(["Unnamed: 0.1", "Unnamed: 0"], axis=1, inplace=True)
df_organization = df_data["Organisation"].value_counts()

# Create column Year and Date
df_data["Date"] = pd.to_datetime(df_data["Date"], utc=True, errors='coerce')
df_data["Year"] = pd.DatetimeIndex(df_data["Date"]).year.astype("Int64")

plt.figure(figsize=(16, 8))
plt.bar(x=df_organization.index,
        height=df_organization.values)
plt.xticks(rotation=45)
plt.xlabel("Organisation")
plt.ylabel("Count")
plt.title("Space mission launches by organisation")
plt.tight_layout()
plt.show()

df_rocket_status = df_data["Rocket_Status"].value_counts()
plt.figure(figsize=(16, 8))
plt.bar(x=df_rocket_status.index,
        height=df_rocket_status.values)
plt.xlabel("Rocket Status")
plt.ylabel("Count")
plt.title("Active vs. retired Rockets")
plt.tight_layout()
plt.show()

df_mission_status = df_data["Mission_Status"].value_counts()
plt.figure(figsize=(16, 8))
plt.bar(x=df_mission_status.index,
        height=df_mission_status.values)
plt.xlabel("Mission Status")
plt.ylabel("Count")
plt.title("Distribution of mission status")
plt.tight_layout()
plt.show()

df_launches = df_data.dropna().copy()  # to avoid warning message .copy()
df_launches["Price"] = df_launches["Price"].astype(str).str.replace(",","")  # Price column is str. Need to transfer into float.
df_launches["Price"] = pd.to_numeric(df_launches["Price"])
print(df_launches["Price"].sort_values(ascending=False))
plt.figure(figsize=(16, 8))
plt.hist(df_launches["Price"],
         bins=10,
         ec="black",
         color="red",
         rwidth=0.2)
plt.xlabel("Price [Mil. USD]")
plt.ylabel("Count")
plt.title("Launches")
plt.xlim(left=0)
plt.show()

# TODO Choropleth Map to Show the Number of Launches by Country
country_list = []
for country in df_data["Location"]:
    country_temp = country.split(",")[-1].strip()

    if country_temp == "Russia" or country_temp == "Barents Sea":
        country_temp = "Russian Federation"
    if country_temp == "New Mexico" or country_temp == "Pacific Missile Range Facility" or country_temp == "Gran Canaria":
        country_temp = "USA"
    if country_temp == "Yellow Sea":
        country_temp = "China"
    if country_temp == "Shahrud Missile Test Site" or country_temp == "Iran":
        country_temp = "Iran, Islamic Republic of"
    if country_temp == "South Korea":
        country_temp = "Korea, Republic of"
    if country_temp == "North Korea":
        country_temp = "Korea, Democratic People's Republic of"
    if country_temp == "Pacific Ocean":
        country_temp = "Kiribati"

    country_list.append(country_temp)

df_data["Country"] = country_list

country_iso_list = []

for country in country_list:
    if country in countries:
        country_iso_list.append(countries.get(country).alpha3)
    else:
        print(f"{country} is not in the list.")

df_data["ISO"] = country_iso_list
df_countries = df_data.groupby(["ISO"], as_index=False).agg({"Country": pd.Series.count})

world_map = px.choropleth(df_countries,
                          locations="ISO",
                          color="Country",
                          labels={"Country": "Total count"},
                          color_continuous_scale=px.colors.sequential.matter)
world_map.show()

# TODO Choropleth Map to Show the Number of Failures by Country
df_failures = df_data.where(df_data["Mission_Status"] == "Failure").groupby(["ISO"], as_index=False).agg(
    {"Country": pd.Series.count})

world_failures_map = px.choropleth(df_failures,
                                   locations="ISO",
                                   color="Country",
                                   labels={"Country": "Total failures"},
                                   color_continuous_scale=px.colors.sequential.matter)
world_failures_map.show()

# TODO Plotly Sunburst Chart of the countries, organisations, and mission status
df_countries_org_miss_status = df_data.groupby(["Country", "Organisation", "Mission_Status"], as_index=False).agg(
    {"ISO": pd.Series.count})

countries_org_miss_status = px.sunburst(df_countries_org_miss_status,
                                        path=["Country", "Organisation", "Mission_Status"],
                                        values="ISO",
                                        # color="Mission_Status", #if the user wants to have different color for Mission_Status
                                        # color_discrete_map={"Success":"green", "Failure":"red", "Partial Failure":"orange", "Prelaunch Failure":"blue"},
                                        )
countries_org_miss_status.show()

# TODO Analyse the Total Amount of Money Spent by Organisation on Space Missions
df_total_amount_space_mission = df_launches.groupby(["Organisation"], as_index=False).agg({"Price": pd.Series.sum})
print(df_total_amount_space_mission.sort_values(by="Price", ascending=False))

df_total_amount_launch = df_launches.groupby(["Organisation", "Detail"], as_index=False).agg({"Price": pd.Series.sum})
print(df_total_amount_launch.sort_values(by="Price", ascending=False))

# TODO Chart the Number of Launches per Year
df_launches_year = df_data.groupby(["Year"], as_index=False).size()

plt.figure(figsize=(16, 8))
sns.barplot(x="Year", y="size", data=df_launches_year)
plt.xticks(rotation=45)
plt.xlabel("Year")
plt.ylabel("Launches")
plt.title("Number of launches per Year")
plt.tight_layout()
plt.show()

# TODO Number of Launches Month-on-Month until the Present
df_data["Month"] = pd.DatetimeIndex(df_data["Date"]).month.astype("Int64")
df_data["MonthYear"] = df_data["Date"].dt.to_period("M").dt.to_timestamp()

monthly_counts = df_data.groupby("MonthYear").size()
rolling_avg = monthly_counts.rolling(window=6).mean()

plt.figure(figsize=(16, 8))
plt.plot(monthly_counts, label="Launches", color="steelblue")
plt.plot(rolling_avg, label="Mean (6 months)", color="orange")
plt.axvline(monthly_counts.idxmax(), color="red", linestyle="--", label="Peak")
plt.title("Number of launches over Years(with rolling 6 months)")
plt.xlabel("Year")
plt.ylabel("Number of launches")
plt.legend()
plt.tight_layout()
plt.show()

# TODO Launches per Month: Which months are most popular and least popular for launches?
popular_months = df_data["Month"].value_counts().reset_index()
popular_months.columns = ["Month", "Count"]
print(f"Popular month for launches\n{popular_months.sort_values(by='Count', ascending=False)}\n")

# TODO Launch Price varied Over Time?
avg_price = df_launches.groupby(["Year"], as_index=False).agg({"Price": pd.Series.mean})
# Between 1957-1964 and 1973-1981 there are no Price Data
plt.figure(figsize=(16, 8))
sns.lineplot(x="Year", y="Price", data=avg_price)
plt.xticks(ticks=avg_price["Year"], rotation=45)
plt.xlabel("Year")
plt.ylabel("Average Price")
plt.title("Price variation")
plt.tight_layout()
plt.grid(color="grey", linestyle="--")
plt.show()

# TODO Number of Launches over Time by Organisations.
df_launches_org = df_launches.groupby(["Year", "Organisation"], as_index=False).agg({"Detail": pd.Series.count})

fig = px.line(x="Year", y="Detail", color="Organisation", markers=True, data_frame=df_launches_org)
fig.update_layout(xaxis=dict(
    tickmode='array',
    tickvals=list(range(df_launches_org["Year"].min(), df_launches_org["Year"].max() + 5, 2))
),
    xaxis_title="Year",
    yaxis_title="Number of Launches",
    title="Launch over Time by Organization")
plt.grid(color="grey", linestyle="--")
fig.show()

# TODO Plotly Pie Chart comparing the total number of launches of the USSR and the USA
df_temp = df_data.copy()
df_temp = df_temp[df_temp["Year"] <= 1991]

df_temp["Country"] = df_temp["Country"].replace({
    "Kazakhstan": "USSR",
    "Russian Federation": "USSR"
})

df_filtered = df_temp[df_temp["Country"].isin(["USSR", "USA"])]

launch_counts_ussr_usa = df_filtered["Country"].value_counts()

fig = px.pie(
    names=launch_counts_ussr_usa.index,
    values=launch_counts_ussr_usa.values,
    title="Number of launches of the USSR and the USA"
)
fig.show()

# TODO Chart that shows the Total Number of Launches Year-On-Year by the Two Superpowers
df_launches_ussr_usa = df_filtered.groupby(["Year", "Country"], as_index=False).agg({"Detail": pd.Series.count})

fig = px.line(x="Year", y="Detail", color="Country", markers=True, data_frame=df_launches_ussr_usa)
fig.update_layout(xaxis=dict(
    tickmode='array',
    tickvals=list(range(df_launches_ussr_usa["Year"].min(), df_launches_ussr_usa["Year"].max() + 5, 2))
),
    xaxis_title="Year",
    yaxis_title="Number of Launches",
    title="Launch over Cold War by USSR and USA")
plt.grid(color="grey", linestyle="--")
fig.show()

#Or

fig = px.bar(
    df_launches_ussr_usa,
    x="Year",
    y="Detail",
    color="Country",
    barmode="group",
    title="Launch over Cold War by USSR and USA"
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Launches",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(df_launches_ussr_usa["Year"].min(), df_launches_ussr_usa["Year"].max() + 5))
    )
)
fig.show()

#TODO Total Number of Mission Failures Year on Year
df_failures_temp = df_filtered[df_filtered["Mission_Status"] == "Failure"]
df_failures_ussr_usa = df_failures_temp.groupby(["Year","Country"], as_index=False).agg({"Mission_Status": pd.Series.count})

fig = px.bar(
    df_failures_ussr_usa,
    x="Year",
    y="Mission_Status",
    color="Country",
    barmode="group",
    title="Failures over Cold War by USSR and USA"
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Failures",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(df_launches_ussr_usa["Year"].min(), df_launches_ussr_usa["Year"].max() + 5))
    )
)
fig.show()

df_failures = df_data.where(df_data["Mission_Status"] == "Failure").groupby(["Year"], as_index=False).agg(
    {"Mission_Status": pd.Series.count})

fig = px.bar(
    df_failures,
    x="Year",
    y="Mission_Status",
    title="Failures over Years"
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Failures",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(df_failures["Year"].min(), df_failures["Year"].max() + 5, 2))
    )
)
fig.show()

#TODO Chart the Percentage of Failures over Time
total_failures = df_failures["Mission_Status"].sum()
df_failures["Percent_Failures"] = (df_failures["Mission_Status"] / total_failures) * 100

fig = px.bar(
    df_failures,
    x="Year",
    y="Percent_Failures",
    title="Percent of Failures over Years"
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Percent of Failures",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(df_failures["Year"].min(), df_failures["Year"].max() + 5, 2))
    )
)
fig.show()

#TODO Every Year Show which Country was in the Lead in terms of Total Number of Launches
df_launches_country = df_data.groupby(["Year", "Country"], as_index=False).agg({"Detail": pd.Series.count})
df_leading_country = df_launches_country.sort_values("Detail", ascending=False).drop_duplicates("Year")

fig = px.bar(
    df_leading_country,
    x="Year",
    y="Detail",
    color="Country",
    barmode="group",
    title="Leading Country by Launches per Year"
)
fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Number of Launches",
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(df_failures["Year"].min(), df_failures["Year"].max() + 5, 2))
    )
)
fig.show()
