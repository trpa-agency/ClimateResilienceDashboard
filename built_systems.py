import numpy as np
import pandas as pd
import plotly.graph_objects as go

from utils import (
    get_fs_data,
    get_fs_data_spatial,
    get_fs_data_spatial_query,
    read_file,
    stacked_area,
    stackedbar,
    trendline,
)


# get data for affordable units
def get_data_affordable_units():
    # parcel development history layer
    parcelURL = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/17"
    # deed restricted housing layer
    deedURL = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/20"

    parcelUnits = get_fs_data_spatial_query(parcelURL, "Year = 2022")
    deedUnits = get_fs_data_spatial_query(deedURL, "DeedRestrictionType = 'Affordable Housing'")

    # merge the two dataframes on the parcel id
    df = pd.merge(parcelUnits, deedUnits, on="APN", how="left")

    # group by LOCATION_TO_TOWNCENTER and sum of OBJECTID_y and Residential_Units
    df = (
        df.groupby("LOCATION_TO_TOWNCENTER")
        .agg({"OBJECTID_y": "count", "Residential_Units": "sum"})
        .reset_index()
    )

    # add the values in the first row to the second row
    df.iloc[1] = df.iloc[0] + df.iloc[1]

    # drop index row 0
    df = df.drop(df.index[0])

    # rename column OBJECTID_y to Total Deed Restricted Housing
    df = df.rename(
        columns={
            "LOCATION_TO_TOWNCENTER": "Location to Town Center",
            "OBJECTID_y": "Total Deed Restricted Housing",
            "Residential_Units": "Total Residential Units",
        }
    )

    # cast Total Deed Restricted Housing to int and Residential Units to int
    df["Total Deed Restricted Housing"] = df["Total Deed Restricted Housing"].astype(int)
    df["Total Residential Units"] = df["Total Residential Units"].astype(int)
    return df


# html\3.1.a_Affordable_Units.html
def plot_affordable_units(df):
    stackedbar(
        df,
        path_html="html/3.1.a_Affordable_Units.html",
        div_id="3.1.a_Affordable_Units",
        x="Location to Town Center",
        y=["Total Deed Restricted Housing", "Total Residential Units"],
        facet=None,
        color=None,
        color_sequence=["#023f64", "#7ebfb5", "#a48352"],
        orders=None,
        y_title="Total Units",
        x_title="Location to Town Center",
        format=".0f",
        custom_data=None,
        hovertemplate="%{y:.0f}",
        hovermode="x unified",
        orientation=None,
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


# get data for home heating
def get_data_home_heating():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/135"
    )
    data["Geography"] = data["Geography"].replace({"Basin": "Lake Tahoe Region"})
    mask = (data["Category"] == "Home Heating Method") & (
        data["variable_name"] != "Total Heating Methods"
    )
    val = (
        data[mask]
        .loc[:, ["variable_name", "value", "Geography", "year_sample"]]
        .rename(columns={"year_sample": "Year", "variable_name": "Energy Source"})
    )
    total = data[data["variable_name"] == "Total Heating Methods"].loc[
        :, ["value", "Geography", "year_sample"]
    ]
    df = val.merge(
        total,
        left_on=["Geography", "Year"],
        right_on=["Geography", "year_sample"],
        suffixes=("", "_total"),
    )
    df["Year"] = df["Year"].astype("str")
    df["share"] = df["value"] / df["value_total"]
    return df


# html\3.1.b_HomeHeatingFuels.html
def plot_home_heating(df):
    stackedbar(
        df,
        path_html="html/3.1.b_HomeHeatingFuels.html",
        div_id="3.1.b_HomeHeatingFuels",
        x="Year",
        y="share",
        facet="Geography",
        color="Energy Source",
        color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
            "#BCEDB8",
            "#023F64",
            "#62C0CC",
            "#B83F5D",
        ],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="% of Home Energy Sources by Share of Total",
        x_title="Year",
        hovertemplate="%{y:.0%}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
        custom_data=None,
        facet_row=None,
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=150,
                yanchor="bottom",
                y=1.2,
                xanchor="right",
                x=0.95,
            )
        ),
    )


# get data for deed restricted units
def get_data_deed_restricted():
    # deed restriction service
    deedRestrictionService = "https://www.laketahoeinfo.org/WebServices/GetDeedRestrictedParcels/JSON/e17aeb86-85e3-4260-83fd-a2b32501c476"
    # read in deed restricted parcels
    dfDeed = pd.read_json(deedRestrictionService)
    # filter out deed restrictions that are not affordable housing
    dfDeed = dfDeed.loc[
        dfDeed["DeedRestrictionType"].isin(
            ["Affordable Housing", "Achievable Housing", "Moderate Income Housing"]
        )
    ]
    # create year column
    dfDeed["Year"] = dfDeed["RecordingDate"].str[-4:]
    # group by type and year
    df = dfDeed.groupby(["DeedRestrictionType", "Year"]).size().reset_index(name="Total")
    # sort by year
    df.sort_values("Year", inplace=True)
    # rename columns
    df = df.rename(columns={"DeedRestrictionType": "Type", "Year": "Year", "Total": "Count"})
    # Create a DataFrame with all possible combinations of 'Type' and 'Year'
    df_all = pd.DataFrame(
        {
            "Type": np.repeat(df["Type"].unique(), df["Year"].nunique()),
            "Year": df["Year"].unique().tolist() * df["Type"].nunique(),
        }
    )
    # Merge the new DataFrame with the original one to fill in the gaps of years for each type with NaN values
    df = pd.merge(df_all, df, on=["Type", "Year"], how="left")
    # Replace NaN values in 'Count' with 0
    df["Count"] = df["Count"].fillna(0)
    # Ensure 'Count' is of integer type
    df["Count"] = df["Count"].astype(int)
    # Recalculate 'Cumulative Count' as the cumulative sum of 'Count' within each 'Type' and 'Year'
    df["Cumulative Count"] = df.sort_values("Year").groupby("Type")["Count"].cumsum()
    return df


# html\3.1.c_Deed_Restricted_Units_v1.html
# html\3.1.c_Deed_Restricted_Units_v2.html
def plot_data_deed_restricted(df):
    trendline(
        df,
        path_html="html/3.1.c_Deed_Restricted_Units_v1.html",
        div_id="3.1.c_Deed_Restricted_Units_v1",
        x="Year",
        y="Cumulative Count",
        color="Type",
        color_sequence=["#023f64", "#7ebfb5", "#a48352"],
        sort="Year",
        orders=None,
        x_title="Year",
        y_title="Cumuluative Total of Deed Restricted Parcels",
        format=",.0f",
        hovertemplate="%{y:.0f}",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
        custom_data=None,
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
    stacked_area(
        df,
        path_html="html/3.1.c_Deed_Restricted_Units_v2.html",
        div_id="3.1.c_Deed_Restricted_Units_v2",
        x="Year",
        y="Cumulative Count",
        color="Type",
        line_group=None,
        color_sequence=["#023f64", "#7ebfb5", "#a48352"],
        x_title="Year",
        y_title="Cumuluative Count of Deed Restricted Parcels",
        hovermode="x unified",
        format=",.0f",
        custom_data=["Type"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0f}</b> parcels with a", "<b>%{customdata[0]}</b> deed restriction"]
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


# get data for energy mix
def get_data_energy_mix():
    return read_file("data/EnergyMix_long.csv")


# html/3.2.a_EnergyMix.html
def plot_energy_mix(df):
    # change name of Renewables to Renewable in Type column
    df["Type"] = df["Type"].replace("Renewables", "Renewable")
    stackedbar(
        df,
        path_html="html/3.2.a_EnergyMix.html",
        div_id="3.2.a_EnergyMix",
        x="Year",
        y="Share",
        facet="Source",
        color="Type",
        color_sequence=["#208385", "#FC9A62"],
        orders={"Year": []},
        y_title="Share of Total Energy Produced",
        x_title="Year",
        custom_data=["Type", "Source"],
        hovertemplate="<br>".join(
            [
                "<b>%{y:.0%}</b> of energy produced by",
                "<i>%{customdata[1]}</i> was from",
                "<i>%{customdata[0]}</i> sources",
            ]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=".0%",
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

# get data for transit ridership
def get_data_transit():
    url = "https://www.laketahoeinfo.org/WebServices/GetTransitMonitoringData/CSV/e17aeb86-85e3-4260-83fd-a2b32501c476"

    dfTransit = pd.read_csv(url)
    dfTransit['Month'] = pd.to_datetime(dfTransit['Month'])
    dfTransit['Month'] = dfTransit['Month'].dt.strftime('%Y-%m')
    # filter out rows where RouteType is not Paratransit, Commuter, or Seasonal Fixed
    df = dfTransit.loc[~dfTransit['RouteType'].isin(['Paratransit', 'Commuter', 'Seasonal Fixed Route'])]
    # df = dfTransit.loc[dfTransit['RouteType'] != 'Paratransit']

    # replace transit operator values with abreviations
    df['TransitOperator'] = df['TransitOperator'].replace(
        ['Tahoe Transportation District',
       'Tahoe Truckee Area Regional Transit',
       'South Shore Transportation Management Association'],
       ["TTD", "TART", "SSTMA"])
    # route name = route type + transit operator
    df['RouteName'] = df['RouteType'] + ' - ' + df['TransitOperator']
    # group by RouteType, TransitOperator, and Month with sum of MonthlyRidership
    df = df.groupby(['RouteName', 'Month'])['MonthlyRidership'].sum().reset_index()
    # rename columns to Date, Name, Ridership
    df.rename(columns={'Month':'Date', 'RouteName':'Name', 'MonthlyRidership':'Ridership'}, inplace=True)
    # sort by Date
    df = df.sort_values('Date')
    return df

# html/3.3.a_Transit_Ridership.html
def plot_transit(df):
    trendline(
        df,
        path_html="html/3.3.a_Transit_Ridership.html",
        div_id="3.3.a_Transit_Ridership",
        x="Date",
        y="Ridership",
        color="Name",
        color_sequence=["#023f64", "#7ebfb5", "#a48352", "#FC9A62"],
        sort="Date",
        orders=None,
        x_title="Date",
        y_title="Ridership",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
        format=",.0f",
        custom_data=["Name"],
        hovertemplate="<br>".join([
            "<b>%{y:,.0f}</b> riders on",
            "<i>%{customdata[0]}</i> lines"
                ])+"<extra></extra>",
        additional_formatting = dict(legend=dict(
                                        title="Transit Ridership",
                                        orientation="h",
                                        entrywidth=120,
                                        yanchor="bottom",
                                        y=1.05,
                                        xanchor="right",
                                        x=0.95,
                                    ))
    )

# get data for vehicle miles traveled
def get_data_vehicle_miles_traveled():
    vmt_data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/133"
    )
    vmt_data[["CA", "NV", "Total"]] = vmt_data[["CA", "NV", "Total"]].apply(
        lambda x: x.str.replace(",", "").dropna().astype(int)
    )
    vmt_data_graph = vmt_data.melt(
        id_vars="year", value_vars=["CA", "NV", "Total"], var_name="State", value_name="VMT"
    )
    vmt_data_graph = vmt_data_graph.query("year > 2015 & State=='Total'")
    return vmt_data_graph


# html/3.3.b_Vehicle_Miles_Traveled.html
def plot_vehicle_miles_traveled(df):
    trendline(
        df,
        path_html="html/3.3.b_Vehicle_Miles_Traveled.html",
        div_id="3.3.b_Vehicle_Miles_Traveled",
        x="year",
        y="VMT",
        color=None,
        color_sequence=["#208385"],
        orders=None,
        sort="year",
        y_title="Miles Traveled",
        x_title="Year",
        format=",.0f",
        hovertemplate="<b>%{y:,.0f}</b> vehicle miles traveled",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
        custom_data=None,
        additional_formatting=dict(
            title="Total Vehicle Miles Traveled",
            )
    )
# get data for mode share
def get_data_mode_share():
    modeshare_data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/136"
    )
    modeshare_data_grouped = (
        modeshare_data.groupby(["Year", "Season", "Mode", "Source"])
        .agg({"Number": "mean"})
        .reset_index()
    )
    modeshare_data_grouped["Year_Season"] = (
        modeshare_data_grouped["Year"].astype(str) + " " + modeshare_data_grouped["Season"]
    )

    modeshare_data_grouped["Total"] = modeshare_data_grouped.groupby(["Year", "Season", "Source"])[
        "Number"
    ].transform("sum")
    # Calculate percentage
    modeshare_data_grouped["Percentage"] = (
        modeshare_data_grouped["Number"] / modeshare_data_grouped["Total"]
    ) * 100

    modeshare_data_grouped["Season"] = pd.Categorical(
        modeshare_data_grouped["Season"], ["Winter", "Q1", "Spring", "Q3", "Summer", "Fall"]
    )
    modeshare_data_grouped = modeshare_data_grouped.sort_values(by=["Year", "Season"])
    # Order year season so that it graphs correctly
    modeshare_data_grouped["Year_Season"] = pd.Categorical(
        modeshare_data_grouped["Year_Season"], modeshare_data_grouped["Year_Season"].unique()
    )

    return modeshare_data_grouped


# html\3.3.d_Mode_Share_1.html
# html\3.3.d_Mode_Share_2.html
def plot_mode_share(df):
    # Make a list of seasons for custom sorting
    x_order = df.sort_values("Year_Season")["Year_Season"].unique()
    x_sort = dict(xaxis=dict(categoryorder="array", categoryarray=x_order))
    # Facet option
    stackedbar(
        df=df,
        path_html="html/3.3.d_Mode_Share_1.html",
        div_id="3.3.d_Mode_Share_1",
        x="Year_Season",
        y="Percentage",
        facet=None,
        color="Mode",
        color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
        ],
        orders={"Mode": ["Car_Truck_Van", "Bicycle", "Others", "Public Transit", "Walk"]},
        y_title="Modeshare Percentage",
        x_title="Year",
        hovertemplate="%{y:.0f}%",
        hovermode="x unified",
        orientation="v",
        format=",.0f",
        additional_formatting=x_sort,
        facet_row="Source",
    )
    # Drop down by modeshare
    path_html = "html/3.3.d_Mode_Share_2.html"
    div_id = "3.3.d_Mode_Share_2"
    config = {"displayModeBar": False}
    x_order = df.sort_values("Year_Season")["Year_Season"].unique()
    Source_Colors = {"LOCUS": "#208385", "Replica": "#FC9A62", "Survey": "#F9C63E"}
    df["Source Color"] = df["Source"].map(Source_Colors)
    modeshare_data_car = df.query('Mode=="Car_Truck_Van"')
    modeshare_data_bike = df.query('Mode=="Bicycle"')
    modeshare_data_walk = df.query('Mode=="Walk"')
    modeshare_data_transit = df.query('Mode=="Public Transit"')
    modeshare_data_other = df.query('Mode=="Others"')
    modeshare_data_non_car_list = ["Bicycle", "Walk", "Public Transit"]
    df["Mode"] = df["Mode"].replace(modeshare_data_non_car_list, "Non-Auto")
    modeshare_data_non_car = df.query('Mode=="Non-Auto"')
    # Group by year_season, source, source color and mode and sum percentage
    modeshare_data_non_car = (
        modeshare_data_non_car.groupby(["Year_Season", "Source", "Source Color", "Mode"])
        .agg({"Percentage": "sum"})
        .reset_index()
    )

    hovertemplate_text = "%{customdata[0]} was %{customdata[1]:.1%} of Modeshare <extra></extra>"

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=modeshare_data_car["Year_Season"],
            y=modeshare_data_car["Percentage"],
            name="Automobile",
            showlegend=False,
            customdata=np.stack(
                (modeshare_data_car["Mode"], modeshare_data_car["Percentage"] / 100), axis=-1
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_car["Source Color"],
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=modeshare_data_bike["Year_Season"],
            y=modeshare_data_bike["Percentage"],
            name="Bicycle",
            showlegend=False,
            visible=False,
            customdata=np.stack(
                (modeshare_data_bike["Mode"], modeshare_data_bike["Percentage"] / 100), axis=-1
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_bike["Source Color"],
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=modeshare_data_walk["Year_Season"],
            y=modeshare_data_walk["Percentage"],
            name="Walk",
            showlegend=False,
            visible=False,
            customdata=np.stack(
                (modeshare_data_walk["Mode"], modeshare_data_walk["Percentage"] / 100), axis=-1
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_walk["Source Color"],
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=modeshare_data_transit["Year_Season"],
            y=modeshare_data_transit["Percentage"],
            name="Public Transit",
            showlegend=False,
            visible=False,
            customdata=np.stack(
                (modeshare_data_transit["Mode"], modeshare_data_transit["Percentage"] / 100),
                axis=-1,
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_transit["Source Color"],
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=modeshare_data_other["Year_Season"],
            y=modeshare_data_other["Percentage"],
            name="Other",
            showlegend=False,
            visible=False,
            customdata=np.stack(
                (modeshare_data_other["Mode"], modeshare_data_other["Percentage"] / 100), axis=-1
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_other["Source Color"],
            ),
        )
    )
    fig.add_trace(
        go.Bar(
            x=modeshare_data_non_car["Year_Season"],
            y=modeshare_data_non_car["Percentage"],
            name="Non-Auto",
            showlegend=False,
            visible=False,
            customdata=np.stack(
                (modeshare_data_non_car["Mode"], modeshare_data_non_car["Percentage"] / 100),
                axis=-1,
            ),
            hovertemplate=hovertemplate_text,
            marker=dict(
                color=modeshare_data_non_car["Source Color"],
            ),
        )
    )
    fig.update_layout(title_text="Modeshare by Source")
    source_sort = ["LOCUS", "Replica", "Survey"]

    def custom_sort(tuple_item):
        return source_sort.index(tuple_item[0])

    unique_source = list(set(zip(df["Source"], df["Source Color"])))
    sorted_source = sorted(unique_source, key=custom_sort)

    for source, color in sorted_source:
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode="markers",
                name=source,
                marker=dict(size=7, color=color, symbol="square"),
            )
        )
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list(
                    [
                        dict(
                            label="Mode: Automobile",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        True,
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Mode: Bicycle",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        True,
                                        False,
                                        False,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Mode: Walk",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        False,
                                        True,
                                        False,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Mode: Public Transit",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        False,
                                        False,
                                        True,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Mode: Other",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        False,
                                        False,
                                        False,
                                        True,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Mode: Non-Auto",
                            method="update",
                            args=[
                                {
                                    "visible": [
                                        False,
                                        False,
                                        False,
                                        False,
                                        False,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                        True,
                                    ]
                                }
                            ],
                        ),
                    ]
                ),
            ),
        ]
    )

    fig.update_layout(title_text="Modeshare by Source")
    fig.update_xaxes(categoryorder="array", categoryarray=x_order)
    fig.update_yaxes(title_text="Percentage of Modeshare", ticksuffix="%")
    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )


# get data for low stress bicycle
def get_data_low_stress_bicycle():
    sdf_bikelane = get_fs_data_spatial(
        "https://maps.trpa.org/server/rest/services/Transportation/MapServer/3"
    )
    # recalc miles field from shape length
    sdf_bikelane.MILES = sdf_bikelane["Shape.STLength()"] / 1609.34
    # filter for CLASS = 1 2 or 3
    filtered_sdf_bikelane = sdf_bikelane[sdf_bikelane["CLASS"].isin(["1", "2", "3"])]
    # fix bad values
    filtered_sdf_bikelane.loc[:, "YR_OF_CONS"] = filtered_sdf_bikelane.loc[:, "YR_OF_CONS"].replace(
        ["before 2010", " before 2010"], "2010"
    )
    filtered_sdf_bikelane.loc[:, "YR_OF_CONS"] = filtered_sdf_bikelane.loc[:, "YR_OF_CONS"].replace(
        ["before 2006", "Before 2006", "BEFORE 2006"], "2006"
    )
    filtered_sdf_bikelane.loc[:, "YR_OF_CONS"] = filtered_sdf_bikelane.loc[:, "YR_OF_CONS"].replace(
        [" 2014"], "2014"
    )
    filtered_sdf_bikelane.loc[:, "YR_OF_CONS"] = filtered_sdf_bikelane.loc[:, "YR_OF_CONS"].replace(
        ["2007 (1A) 2008 (1B)"], "2008"
    )
    # drop rows with <NA> values
    filtered_sdf_bikelane = filtered_sdf_bikelane.dropna(subset=["YR_OF_CONS"])
    # drop rows with 'i dont know' or 'UNKNOWN' values
    filtered_sdf_bikelane = filtered_sdf_bikelane[
        ~filtered_sdf_bikelane["YR_OF_CONS"].isin(["i dont know", "UNKNOWN"])
    ]
    # rename columns
    df = filtered_sdf_bikelane.rename(
        columns={"CLASS": "Class", "YR_OF_CONS": "Year", "MILES": "Miles"}
    )
    # Create a DataFrame with all possible combinations of 'Type' and 'Year'
    df_all = pd.DataFrame(
        {
            "Class": np.repeat(df["Class"].unique(), df["Year"].nunique()),
            "Year": df["Year"].unique().tolist() * df["Class"].nunique(),
        }
    )
    # Merge the new DataFrame with the original one to fill in the gaps of years for each type with NaN values
    df = pd.merge(df_all, df, on=["Class", "Year"], how="left")
    # add 2005 to the Year field for Class 1 2, and 3
    dict = {"Class": ["1", "2", "3"], "Year": ["2005", "2005", "2005"], "Miles": [0, 0, 0]}
    df2 = pd.DataFrame(dict)
    df = pd.concat([df, df2], ignore_index=True)

    # cast Year as integer
    df["Year"] = df["Year"].astype(int)
    # cast Class as text
    df["Class"] = df["Class"].astype(str)
    # add the word "Class" to the beginning of the Class field
    df["Class"] = "Class " + df["Class"]
    # sort by year and miles
    df.sort_values(["Year", "Miles"], inplace=True)
    # Replace NaN values in 'MILES' with 0
    df["Miles"] = df["Miles"].fillna(0)
    # create grouped dataframe
    df = df.groupby(["Year", "Class"])["Miles"].sum().reset_index()
    # Recalculate 'Cumulative Count' as the cumulative sum of 'Count' within each 'Type' and 'Year'
    df["Total Miles"] = df.sort_values("Year").groupby("Class")["Miles"].cumsum()
    df["Year"] = df["Year"].astype(str)
    return df


# html/3.3.f_Low_Stress_Bicycle.html
def plot_low_stress_bicycle(df):
    stacked_area(
        df,
        path_html="html/3.3.f_Low_Stress_Bicycle.html",
        div_id="3.3.f_Low_Stress_Bicycle",
        x="Year",
        y="Total Miles",
        color="Class",
        line_group="Class",
        color_sequence=["#023f64", "#7ebfb5", "#a48352"],
        x_title="Year",
        y_title="Total Miles of Bike Routes Built",
        hovermode="x unified",
        format=".0f",
        custom_data=["Class"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0f}</b> total miles of", "<i>%{customdata[0]}</i> routes completed"]
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
