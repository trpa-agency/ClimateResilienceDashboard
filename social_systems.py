from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import pydeck

from utils import get_fs_data, groupedbar_percent, read_file, stackedbar, trendline, create_stacked_bar_plot_with_dropdown


# get data for household income
def get_data_household_income():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    # get only household income data
    df = data.loc[(data["Category"] == "Household Income")].copy()
    df["Geography"] = df["Geography"].replace({"Basin": "Lake Tahoe Region"})
    df = df.rename(columns={"year_sample": "Year"})
    return df


# html\4.1.a_Household_Income_v1.html
def plot_household_income(df):
    groupedbar_percent(
        df,
        path_html="html/4.1.a_Household_Income_v1.html",
        div_id="4.1.a_Household_Income_v1",
        x="Year",
        y="value",
        facet="Geography",
        color="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A"],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="Median Household Income ($)",
        x_title="Year",
        custom_data=["Geography"],
        hovertemplate="<br>".join(
            ["<b>$%{y:,.0f}</b> is the median income of", "<i>%{customdata[0]}</i> residents"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        format="$,.0f",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )
    trendline(
        df,
        path_html="html/4.1.a_Household_Income_v2.html",
        div_id="4.1.a_Household_Income_v2",
        x="Year",
        y="value",
        color="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A"],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        sort="Year",
        x_title="Year",
        y_title="Median Household Income ($)",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
        custom_data=["Geography"],
        format="$,.0f",
        hovertemplate="<br>".join(
            ["<b>$%{y:,.0f}</b> is the median income of", "<i>%{customdata[0]}</i> residents"]
        )
        + "<extra></extra>",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=120,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )


def calculate_data_median_home_price(start_date, end_date):
    property_files = (
        Path("~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/")
        .expanduser()
        .glob("Tahoe_PropertyRadar_*.csv")
    )
    data = pd.concat(
        [read_file(file) for file in property_files], ignore_index=True
    ).drop_duplicates()

    data = data[
        (data["City"] != "TRUCKEE")  # NOTE: Should probably be inclusion by tract ID
        & (data["Purchase Type"] == "Market")
        & (data["Lot Acres"] > 0)
        & (
            data["Purchase Date"]
            != "The information contained in this report is subject to the license restrictions and all other terms contained in PropertyRadar.com's User Agreement."
        )
    ]
    data["Purchase Date"] = pd.to_datetime(data["Purchase Date"])
    data = data[
        (data["Purchase Date"] >= pd.to_datetime(start_date))
        & (data["Purchase Date"] <= pd.to_datetime(end_date))
    ]
    data["year"] = data["Purchase Date"].dt.year
    data["month"] = data["Purchase Date"].dt.month
    data.to_csv("data/property_radar_all.csv", index=False)
    df = data.groupby(["year", "month"])["Purchase Amt"].median().reset_index()
    df["month_year"] = (
        df["year"].astype(int).astype(str) + "-" + df["month"].astype(int).astype(str)
    )
    df = df.dropna()
    df.to_csv("data/property_radar.csv", index=False)
    return df



# get data for median home price
def get_data_median_home_price():
    url = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/147"
    data = get_fs_data(url)
    # convert month and year to datetime
    data["month_year"] = pd.to_datetime(data["month_year"])
    data["year"] = data["month_year"].dt.year
    data["month"] = data["month_year"].dt.month
    # rename columns
    df = data.rename(
        columns={"Purchase_Amt": "Purchase Amount", "month_year": "Month", "year": "Year"}
    )
    return df


# html\4.1.b_Median_Sale_Prices.html
def plot_median_home_price(df):
    trendline(
        df,
        path_html="html/4.1.b_Median_Sale_Prices.html",
        div_id="4.1.b_Median_Sale_Prices",
        x="Month",
        y="Purchase Amount",
        color=None,
        color_sequence=["#208385"],
        orders=None,
        sort=["Year", "month"],
        x_title="Sale Date",
        y_title="Median Sale Price ($)",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
        custom_data=None,
        format="$,.0f",
        hovertemplate="<br>".join(["<b>$%{y:,.0f}</b> was the", "<i>median sales price</i>"])
        + "<extra></extra>",
        additional_formatting=None,
    )


# get data for rent prices
def get_data_rent_prices():
    df_tahoe = read_file("data/CoStar/LakeTahoe_MF_AllBeds.csv")
    df_tahoe["Geography"] = "Lake Tahoe"
    df_CA = read_file("data/CoStar/California_MF_AllBeds.csv")
    df_CA["Geography"] = "California"
    df_NV = read_file("data/CoStar/Nevada_MF_AllBeds.csv")
    df_NV["Geography"] = "Nevada"
    df = pd.concat([df_tahoe, df_CA, df_NV], ignore_index=True)
    df["Year"] = df["Period"].str[:4].astype(int)
    df["Quarter"] = df["Period"].str[6:7]

    # df["Year"] = df["Period"].apply(lambda x: x.split()[0])
    # df['Period'] = df['Period'].str.replace(' ', '')
    # df = df[df["Period"]!="2024Q1QTD"]
    # df['date'] = pd.PeriodIndex(df['Period'], freq='Q').strftime('%Y%Q')
    return df


# html\4.1.b_Rent_Prices.html
def plot_rent_prices(df):
    trendline(
        df,
        path_html="html/4.1.b_Rent_Prices.html",
        div_id="4.1.b_Rent_Prices",
        x="Period",
        y="Effective Rent Per Unit",
        color="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A"],
        sort="Period",
        orders=None,
        x_title="Year",
        y_title="Rent Prices ($)",
        markers=True,
        tickvals=df[df["Geography"] == "Lake Tahoe"]["Period"][::4],
        ticktext=df[df["Geography"] == "Lake Tahoe"]["Year"][::4],
        tickangle=-45,
        format="$,.0f",
        hovermode="x unified",
        # hover_data={"Year": True, "Quarter": True},
        hover_data=None,
        custom_data=["Geography", "Quarter", "Year"],
        # hovertemplate="<b>%{customdata[0]} Q%{customdata[1]}</b>: %{y}",
        hovertemplate="<br>".join(
            [
                "<b>$%{y:,.0f}</b> was the <i>median rent price</i> in ",
                "<i>%{customdata[0]}</i> during <i>Q%{customdata[1]}</i> of <i>%{customdata[2]}</i>",
            ]
        )
        + "<extra></extra>",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=70,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )


# get tenure by age data
def get_data_tenure_by_age():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    mask = (data["Category"] == "Tenure by Age") & (data["year_sample"] == 2021)
    val = (
        data[mask]
        .loc[:, ["variable_name", "value", "Geography"]]
        .rename(columns={"variable_name": "Age"})
    )
    val["Tenure"] = np.where(
        val["Age"].str.startswith("Owner"), "Owner Occupied", "Renter Occupied"
    )
    val["Age"] = val["Age"].replace(
        {
            "Owner Occupied: Householder 15 To 24 Years": "15 to 24 Years",
            "Owner Occupied: Householder 25 To 34 Years": "25 to 34 Years",
            "Owner Occupied: Householder 35 To 44 Years": "35 to 44 Years",
            "Owner Occupied: Householder 45 To 54 Years": "45 to 54 Years",
            "Owner Occupied: Householder 55 To 59 Years": "55 to 59 Years",
            "Owner Occupied: Householder 60 To 64 Years": "60 to 64 Years",
            "Owner Occupied: Householder 65 To 74 Years": "65 to 74 Years",
            "Owner Occupied: Householder 75 To 84 Years": "75 to 84 Years",
            "Owner Occupied: Householder 85 Years And Over": "85+ Years",
            "Renter Occupied: Householder 15 To 24 Years": "15 to 24 Years",
            "Renter Occupied: Householder 25 To 34 Years": "25 to 34 Years",
            "Renter Occupied: Householder 35 To 44 Years": "35 to 44 Years",
            "Renter Occupied: Householder 45 To 54 Years": "45 to 54 Years",
            "Renter Occupied: Householder 55 To 59 Years": "55 to 59 Years",
            "Renter Occupied: Householder 60 To 64 Years": "60 to 64 Years",
            "Renter Occupied: Householder 65 To 74 Years": "65 to 74 Years",
            "Renter Occupied: Householder 75 To 84 Years": "75 to 84 Years",
            "Renter Occupied: Householder 85 Years And Over": "85+ Years",
        }
    )
    val["Geography"] = val["Geography"].replace({"Basin": "Lake Tahoe Region"})
    total = val.groupby(["Geography", "Age"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Age"],
        right_on=["Geography", "Age"],
        suffixes=("", "_total"),
    )
    df["share"] = df["value"] / df["value_total"]
    return df


# html\4.1.c_TenureByAge.html
def plot_tenure_by_age(df):
    stackedbar(
        df,
        path_html="html/4.1.c_TenureByAge.html",
        div_id="4.1.c_TenureByAge",
        x="Age",
        y="share",
        facet="Geography",
        color="Tenure",
        color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
            "#BCEDB8",
            "#023F64",
            "#B83F5D",
            "#FCE3A4",
        ],
        orders={
            "Age": [
                "15 to 24 Years",
                "25 to 34 Years",
                "35 to 44 Years",
                "45 to 54 Years",
                "55 to 59 Years",
                "60 to 64 Years",
                "65 to 74 Years",
                "75 to 84 Years",
                "85+ Years",
            ],
            "Geography": ["Lake Tahoe Region", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Age",
        x_title="Age",
        hovermode="x unified",
        orientation=None,
        format=".0%",
        custom_data=None,
        hovertemplate="%{y:.0%}",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )


# get tenure by race data
def get_data_tenure_by_race():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    mask = (data["Category"] == "Tenure by Race") & (data["year_sample"] == 2022)
    val = data[mask].loc[:, ["variable_name", "value", "Geography"]]
    val["Race"] = val["variable_name"].replace(
        {
            "Owner Occupied: Asian Alone Householder": "Asian",
            "Owner Occupied: Black Or African American Alone Householder": "Black",
            "Owner Occupied: White Alone Householder": "White",
            "Owner Occupied: Native Hawaiian And Other Pacific Islander Alone Householder": "NHPI",
            "Owner Occupied: Some Other Race Alone Householder": "Some Other",
            "Owner Occupied: American Indian And Alaska Native Alone Householder": "AIAN",
            "Renter Occupied: Asian Alone Householder": "Asian",
            "Renter Occupied: Black Or African American Alone Householder": "Black",
            "Renter Occupied: White Alone Householder": "White",
            "Renter Occupied: Native Hawaiian And Other Pacific Islander Alone Householder": "NHPI",
            "Renter Occupied: Some Other Race Alone Householder": "Some Other",
            "Renter Occupied: American Indian And Alaska Native Alone Householder": "AIAN",
            "Total: Asian Alone Householder": "Asian",
            "Total: Black Or African American Alone Householder": "Black",
            "Total: Native Hawaiian And Other Pacific Islander Alone Householder": "NHPI",
            "Total: Some Other Race Alone Householder": "Some Other",
            "Total: American Indian And Alaska Native Alone Householder": "AIAN",
            "Total: White Alone Householder": "White",
            "Total: Two Or More Races Householder": "Multi",
        }
    )
    val["Geography"] = val["Geography"].replace({"Basin": "Lake Tahoe Region"})
    total = val[(val["variable_name"].str.contains("Total:"))]
    val = val[(~val["variable_name"].str.contains("Total"))]
    df = total.merge(
        val,
        left_on=["Geography", "Race"],
        right_on=["Geography", "Race"],
        suffixes=("_total", ""),
    )
    df["Tenure"] = np.where(
        df["variable_name"].str.startswith("Owner"), "Owner Occupied", "Renter Occupied"
    )
    df["share"] = df["value"] / df["value_total"]
    return df


# html\4.1.c_TenureByRace.html
def plot_tenure_by_race(df):
    stackedbar(
        df,
        path_html="html/4.1.c_TenureByRace.html",
        div_id="4.1.c_TenureByRace",
        x="Race",
        y="share",
        facet="Geography",
        color="Tenure",
        color_sequence=["#208385", "#FC9A62"],
        orders={
            "Race": ["White", "Black", "Asian", "NHPI", "Some Other"],
            "Geography": ["Lake Tahoe Region", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Race",
        x_title="Race",
        hovermode="x unified",
        orientation=None,
        format=".0%",
        custom_data=None,
        hovertemplate="%{y:.0%}",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )

def get_data_housing_occupancy():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    mask = (data["Category"] == "Housing Units: Occupancy")
    val = data[mask].loc[:, ["variable_name", "value", "Geography", 'year_sample']]
    val=val.groupby(["variable_name", "Geography", 'year_sample']).sum().reset_index()

    # Need to get vacant other from total housing units: vacant and
    #subtracting vacant housing units seasonal rereational or occasional use grouped by geography, year
    mask_vacant_seasonal = (val["variable_name"] == "Vacant Housing Units: Seasonal, recreational, or occasional use")
    mask_vacant_total = (val["variable_name"] == "Total Housing Units: Vacant")
    data_vacant = val[mask_vacant_total].loc[:, ["variable_name", "value", "Geography", 'year_sample']]

    data_vacant_seasonal = val[mask_vacant_seasonal].loc[:, ["variable_name", "value", "Geography", 'year_sample']]
    data_vacant_total = val[mask_vacant_total].loc[:, ["variable_name", "value", "Geography", 'year_sample']]
    #rename the value column to vacant_season for data vacant seasonal
    data_vacant_seasonal = data_vacant_seasonal.rename(columns={"value": "vacant_season"})
    data_vacant_total = data_vacant_total.rename(columns={"value": "vacant_total"})
    #merge the two dataframes
    data_vacant = data_vacant_total.merge(data_vacant_seasonal,
                                            on=["Geography", 'year_sample'])
    data_vacant["vacant_other"] = data_vacant["vacant_total"] - data_vacant["vacant_season"]
    data_vacant = data_vacant.loc[:, ["Geography", 'year_sample', 'vacant_other']]
    data_vacant["variable_name"] = "Vacant Housing Units: Other"
    data_vacant = data_vacant.rename(columns={"vacant_other": "value"})
    val = pd.concat([val, data_vacant], ignore_index=True)
    value_lookup = {
                "Occupied Housing Units: Owner Occupied": "Owner Occupied",
            "Occupied Housing Units: Renter Occupied": "Renter Occupied",
            "Vacant Housing Units: Other": "Vacant Other",
            "Vacant Housing Units: Seasonal, recreational, or occasional use": "Vacant Seasonal",
        }
    val["Occupancy"] = val["variable_name"].replace(
        value_lookup
    )
    # Drop if variable_name not in value_lookup
    val = val.loc[val["variable_name"].isin(value_lookup.keys())]

    val["Geography"] = val["Geography"].replace({"Basin": "Lake Tahoe Region"})
    val["Total_Housing_Units"] = val.groupby(["Geography", "year_sample"])["value"].transform("sum")
    val["share"] = val["value"] / val["Total_Housing_Units"]
    return val
def plot_housing_occupancy(df):
    create_stacked_bar_plot_with_dropdown(
        df,
        path_html="html/4.1.c_Occupancy.html",
        div_id="4.1.c_Occupancy",
        x="year_sample",
        y="share",
        color_column="Occupancy",
        dropdown_column="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A", "#A48352"],
        sort_order=['Owner Occupied', 'Renter Occupied', 'Vacant Other', 'Vacant Seasonal'],
        title_text='Housing Occupancy',
        y_title="% Housing Occupancy",
        x_title="Year",
        hovermode="x unified",
        format=".0%",
        custom_data=["Occupancy"],
        hovertemplate="<br>".join(
            ["<b>%{y:.1%}</b> of the housing units are", "<i>%{customdata}</i>"]
        )
        + "<extra></extra>",
        additional_formatting=dict(
            xaxis = dict(
                tickmode = 'array',
                tickvals = [1990, 2000, 2010, 2020],
                ticktext = ['1990', '2000', '2010', '2020'],
            )
        ),
    )
# get commute patterns data
def get_data_commute_patterns():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/141"
    )
    grouped_df = data.groupby(["Year", "category"], as_index=False).agg({"S000": "sum"})
    processed_df = grouped_df.pivot(index="Year", columns="category", values="S000").reset_index()
    processed_df["commuter_percentage"] = (
        processed_df["Live elsewhere, work in Tahoe"]
        / (
            processed_df["Live elsewhere, work in Tahoe"]
            + processed_df["Live in Tahoe, work in Tahoe"]
        )
        * 100
    )
    return processed_df


# html\4.1.d_commuter_patterns.html
def plot_commute_patterns(df):
    path_html = "html/4.1.d_commuter_percentage.html"
    div_id = "4.1.d_commuter_percentage"
    x = "Year"
    y = "commuter_percentage"
    color = None
    color_sequence = None
    x_title = "Year"
    y_title = "Commuter Percentage"
    y_min = 0
    y_max = 100
    df = df.sort_values(by=x)
    config = {"displayModeBar": False}
    fig = px.line(
        df,
        x=x,
        y=y,
        color=color,
        color_discrete_sequence=color_sequence,
    )
    fig.update_layout(
        yaxis=dict(title=y_title),
        xaxis=dict(title=x_title),
        hovermode="x",
        template="plotly_white",
        dragmode=False,
        yaxis_range=[y_min, y_max],
    )
    fig.update_traces(hovertemplate="%{y:,.0f}")
    fig.update_yaxes(tickformat=",.0f")
    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# get commute origin data
def get_data_commute_origin():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/141"
    )
    reno_census_tracts = read_file("data/Reno_Census_Tracts.csv")
    reno_census_tracts['FIPS'] = reno_census_tracts['FIPS'].astype(str)
    data['reno_tract'] = data['h_tract_id'].isin(reno_census_tracts['FIPS'])
    data.loc[data['reno_tract'], 'h_tract_lat'] = 39.5226659
    data.loc[data['reno_tract'], 'h_tract_long'] = -119.8121265 
    grouped_df = data.groupby(
        [
            "Year",
            "h_tract_long",
            "h_tract_lat",
            "w_tract_lat",
            "w_tract_long",
            "category",
            "w_tract_TRPAID",
            "h_tract_TRPAID",
        ],
        as_index=False,
    ).agg({"S000": "sum"})
    all_data_work = grouped_df.query('w_tract_TRPAID!="Outside Basin"')
    # top_commutes = all_data_work.query('S000 >= 15')
    top_commutes_outside_basin = all_data_work.query('S000 >= 15 & h_tract_TRPAID=="Outside Basin"')
    top_commutes_outside_basin_2021 = top_commutes_outside_basin.loc[
        top_commutes_outside_basin["Year"] == 2021
    ]
    return top_commutes_outside_basin_2021


# html\4.1.d_commuter_percentage.html
def plot_commute_origin(df):
    # Still needs some formatting work
    GREEN_RGB = [0, 255, 0, 200]
    RED_RGB = [240, 100, 0, 200]

    arc_layer = pydeck.Layer(
        "ArcLayer",
        data=df,
        get_width="S000 / 10",
        get_source_position=["h_tract_long", "h_tract_lat"],
        get_target_position=["w_tract_long", "w_tract_lat"],
        get_tilt=15,
        get_source_color=GREEN_RGB,
        get_target_color=RED_RGB,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pydeck.ViewState(
        latitude=38.8973752961, longitude=-120.007333471, bearing=45, pitch=50, zoom=8
    )

    tooltip = {"html": "{S000} jobs <br /> Home of commuter in green; work location in red"}
    r = pydeck.Deck(arc_layer, initial_view_state=view_state, tooltip=tooltip, map_style="road")

    r.to_html("html/4.1.d_commuter_patterns.html")


# get TOT data
def get_data_tot_collected():
    df = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/137"
    )
    df_grouped = df.groupby(["Fiscal_Year", "Jurisdiction"], as_index=False)["TOT_Collected"].sum()
    df_grouped["FY_Formatted"] = df_grouped["Fiscal_Year"].str.replace("-", "/")
    drop_year = [
        "2006/07",
        "2007/08",
        "2008/09",
        "2009/10",
        "2010/11",
        "2011/12",
        "2012/13",
        "2013/14",
        "2014/15",
        "2015/16",
        "2016/17",
        "2017/18",
        "2018/19",
    ]
    df_grouped = df_grouped[~df_grouped["FY_Formatted"].isin(drop_year)]
    return df_grouped


# html\4.2.a_TOT_Collected.html
def plot_tot_collected(df):
    stackedbar(
        df,
        path_html="html/4.2.a_TOT_Collected.html",
        div_id="4.2.a_TOT_Collected",
        x="FY_Formatted",
        y="TOT_Collected",
        facet=None,
        color="Jurisdiction",
        color_sequence=["#484a47", "#5c6d70", "#a37774", "#e88873", "#e0ac9d"],
        orders=None,
        y_title="Total TOT Collected",
        x_title="Fiscal Year",
        hovermode="x unified",
        orientation="v",
        format="$,.0f",
        custom_data=["Jurisdiction"],
        hovertemplate="<br>".join(
            ["<b>$%{y:,.0f}</b> of TOT collected in", "<i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=100,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )


# get race and ethinicity data
def get_data_race_ethnicity():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    mask1 = (data["Category"] == "Race and Ethnicity") & (data['dataset'] != 'acs/acs5' )
    # mask2 = (
    #     (data["Category"] == "Race and Ethnicity")
    #     & (data["year_sample"] == 2020)
    #     & (data["sample_level"] == "block group")
    #     & (data['dataset'] != 'acs/acs5' )
    # )
    val = data[mask1]
    # df2 = data[mask2]
    # val = pd.concat([df1, df2], ignore_index=True)
    val = val.loc[:, ["variable_name", "value", "Geography", "year_sample"]].rename(
        columns={"year_sample": "Year", "variable_name": "Race"}
    )
    val["Geography"] = val["Geography"].replace({"Basin": "Lake Tahoe Region"})
    total = val.groupby(["Geography", "Year"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Year"],
        right_on=["Geography", "Year"],
        suffixes=("", "_total"),
    )
    df["Year"] = df["Year"].astype(str)
    df["share"] = df["value"] / df["value_total"]
    df["Race"] = df["Race"].map(
        {
            "Total population:  Hispanic or Latino": "Hispanic",
            "Total population:  Not Hispanic or Latino; White alone": "White",
            "Total population:  Not Hispanic or Latino; Not Hispanic or Latino; American Indian and Alaska Native alone": "AIAN",
            "Total population:  Not Hispanic or Latino; Black or African American alone": "Black",
            "Total population:  Not Hispanic or Latino; American Indian and Alaska Native alone": "AIAN",
            "Total population:  Not Hispanic or Latino; Asian alone": "Asian",
            "Total population:  Not Hispanic or Latino; Native Hawaiian and Other Pacific Islander alone": "NHPI",
            "Total population:  Not Hispanic or Latino; Some other race alone": "Other",
            "Total population:  Not Hispanic or Latino; Two or more races": "Multi",
        }
    )
    # Populate missing combinations of Race and Year with 0 values
    all_years = df["Year"].unique()
    all_races = df["Race"].unique()
    all_geographies = df["Geography"].unique()
    all_combinations = [(year, race, geography) for year in all_years for race in all_races for geography in all_geographies]
    existing_combinations = [(row["Year"], row["Race"], row["Geography"]) for _, row in df.iterrows()]
    missing_combinations = list(set(all_combinations) - set(existing_combinations))
    missing_data = pd.DataFrame(missing_combinations, columns=["Year", "Race", "Geography"])
    missing_data["value"] = 0
    missing_data["value_total"] = 0
    missing_data["share"] = 0
    df = pd.concat([df, missing_data], ignore_index=True)
    df = df.sort_values(["Year", "Race", "Geography"])
    return df


# html\4.4.a_RaceEthnicity_v1.html
# html\4.4.a_RaceEthnicity_v2.html
def plot_race_ethnicity(df):
    create_stacked_bar_plot_with_dropdown(
        df,
        path_html="html/4.4.a_RaceEthnicity_v1.html",
        div_id="4.4.a_RaceEthnicity_v1",
        x="Year",
        y="share",
        color_column="Race",
        dropdown_column="Geography",
        color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
            "#BCEDB8",
            "#023F64",
            "#B83F5D",
        ],
        sort_order=['White', 'Hispanic', 'Asian', 'Black', 'AIAN', 'NHPI', 'Other', 'Multi'],
        title_text='Race and Ethnicity of Population',
        y_title="Percent of Race and Ethnicity",
        x_title="Year",
        hovermode="x unified",
        format=".0%",
        custom_data=["Race"],
        hovertemplate="<br>".join(
            ["<b>%{y:.1%}</b> of the population is", "<i>%{customdata}</i>"]
        )
        + "<extra></extra>",
        additional_formatting=None,
    )
    groupedbar_percent(
        df,
        path_html="html/4.4.a_RaceEthnicity_v2.html",
        div_id="4.4.a_RaceEthnicity_v2",
        x="Year",
        y="share",
        facet="Geography",
        color="Race",
        color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
            "#BCEDB8",
            "#023F64",
            "#B83F5D",
        ],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="% of Race and Ethnicity of Total",
        x_title="Year",
        hovermode="x unified",
        format=".0%",
        custom_data=["Race"],
        hovertemplate="<br>".join(
            ["<b>%{y:.1%}</b> of the population is", "<i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        additional_formatting=None,
    )
