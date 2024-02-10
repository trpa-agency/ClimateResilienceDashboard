import numpy as np
import pandas as pd

from utils import get_fs_data, read_file, stackedbar, trendline


def get_data_home_heating():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/132"
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
        path_html="html/3.1(b)_HomeHeatingFuels.html",
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
        path_html="html/3.2(a)_EnergyMix.html",
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
        path_html="html/3.1(c)_Deed_Restricted_Units.html",
        div_id="3.1.c_Deed_Restricted_Units",
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
    )
