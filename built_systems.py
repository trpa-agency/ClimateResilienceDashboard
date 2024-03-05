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
        hovertemplate="%{y:.0f}",
        hovermode="x unified",
        orientation=None,
    )


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
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


def get_data_energy_mix():
    return read_file("data/EnergyMix_long.csv")


def plot_energy_mix(df):
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
        y_title="% of Renewable Energy by Share of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


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
        format=".0f",
        hovertemplate="%{y:.0f}",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x",
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
        format=".0f",
        hovertemplate="%{y:.0f}",
    )


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
        y_title="Total Miles of Bike Lane",
        hovermode="x unified",
        format=".2f",
        hovertemplate="%{y:.2f}",
    )


def get_data_transit():
    url = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/131"
    # get data from map service
    data = get_fs_data(url)
    # drop ObjectID
    data = data.drop(columns=["OBJECTID"])
    # stack data by month
    data = data.melt(id_vars=["MONTH"], var_name="Name", value_name="Ridership")
    # create Year field from last two characters of month but add 20 prefix
    data["Year"] = "20" + data["MONTH"].str[-2:]
    # change Name column to Transit Provider
    data = data.rename(columns={"Name": "Transit Provider"})
    # strip the last three characters from month
    data["Month"] = data["MONTH"].str[:-3]
    # drop MONTH
    data = data.drop(columns=["MONTH"])
    # make the values in Month the real names of the months
    data["Month"] = data["Month"].replace(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
    )
    # create a Date type field of Month and Year
    data["Date"] = data["Month"] + " " + data["Year"]
    # convert Date to datetime
    data["Date"] = pd.to_datetime(data["Date"], format="%B %Y")
    df = data.sort_values("Date")
    # drop Name = Total
    df = df.loc[df["Transit Provider"] != "Total"]
    # drop Name IN _Paratransit
    df = df.loc[~df["Transit Provider"].str.contains("_Paratransit")]
    # drop _ in Name values
    df["Transit Provider"] = df["Transit Provider"].str.replace("_", " ")
    return df


def plot_transit(df):
    trendline(
        df,
        path_html="html/3.3.a_Transit_Ridership.html",
        div_id="3.3.a_Transit_Ridership",
        x="Date",
        y="Ridership",
        color="Transit Provider",
        color_sequence=["#023f64", "#7ebfb5", "#a48352", "#FC9A62"],
        sort="Date",
        orders=None,
        x_title="Date",
        y_title="Ridership",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
    )


def get_data_mode_share():
    modeshare_data = get_fs_data('https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/136')
    modeshare_data_grouped = modeshare_data.groupby(['Year','Season', 'Mode', 'Source']).agg({'Number': 'mean'}).reset_index()
    modeshare_data_grouped['Year_Season'] = modeshare_data_grouped['Year'].astype(str) + ' ' + modeshare_data_grouped['Season']

    modeshare_data_grouped['Total'] = modeshare_data_grouped.groupby(['Year','Season','Source'])['Number'].transform('sum')
    #Calculate percentage
    modeshare_data_grouped['Percentage'] = (modeshare_data_grouped['Number'] / modeshare_data_grouped['Total']) * 100

    modeshare_data_grouped['Season'] = pd.Categorical(modeshare_data_grouped['Season'], 
                                                      ['Winter', 'Q1', 'Spring', 'Q3', 'Summer', 'Fall'])
    modeshare_data_grouped = modeshare_data_grouped.sort_values(by=['Year', 'Season'])
    #Order year season so that it graphs correctly
    modeshare_data_grouped['Year_Season'] = pd.Categorical(modeshare_data_grouped['Year_Season'], modeshare_data_grouped['Year_Season'].unique())

    return modeshare_data_grouped


def plot_mode_share(df):
    #Make a list of seasons for custom sorting
    x_order = df.sort_values('Year_Season')['Year_Season'].unique()
    x_sort = dict(xaxis=dict(categoryorder='array', categoryarray=x_order))
    #Facet option
    stackedbar(
    df= df,
    path_html="html/3.3.d_Mode_Share_1.html",
    div_id="3.3.d_Mode_Share_1",
    x ="Year_Season",
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
    orders={"Mode":
     ['Car_Truck_Van', 'Bicycle', 'Others', 'Public Transit', 'Walk']},
    y_title="Modeshare Percentage",
    x_title="Year",
    hovertemplate="%{y:.0f}%",
    hovermode="x unified",
    orientation="v",
    format=",.0f",
    additional_formatting=x_sort,
    facet_row="Source"
    )
    #Just automobile mode share
    modeshare_data__auto = df.query('Mode=="Car_Truck_Van"')
    stackedbar(
    df=modeshare_data__auto,
    path_html="html/3.3.d_Mode_Share_2.html",
    div_id='3.3.d_Mode_Share_2',
    x="Year_Season",
    y="Percentage",
    facet=None,
    color="Source",
    color_sequence=[
            "#208385",
            "#FC9A62",
            "#F9C63E",
            "#632E5A",
            "#A48352",
        ],
    orders=None,
    y_title="Percentage of Auto Trips",
    x_title="Year and Season",
    format=",.0f",
    hovermode="x unified",
    orientation="v",
    hovertemplate="%{y:.0f}%",
    additional_formatting=x_sort
    )

def get_data_vehicles_miles_traveled():
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


def plot_vehicles_miles_traveled(df):
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
        y_title="Total VMT",
        x_title="Year",
        hovertemplate="%{y}",
        format=".%",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
    )
