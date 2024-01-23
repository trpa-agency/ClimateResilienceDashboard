import numpy as np
import pandas as pd

from utils import get_fs_data, groupedbar_percent, stackbar_percent


def get_data_4_1_c_age():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
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
    total = val.groupby(["Geography", "Age"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Age"],
        right_on=["Geography", "Age"],
        suffixes=("", "_total"),
    )
    df["share"] = df["value"] / df["value_total"]
    return df


def plot_4_1_c_age(df):
    stackbar_percent(
        df,
        path_html="html/4.1(c)_TenureByAge.html",
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
            "Geography": ["Basin", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Age",
        x_title="Age",
        hovertemplate="%{y}",
        hovermode="x unified",
    )


def get_data_4_1_c_race():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
    mask = data["Category"] == "Tenure by Race"
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


def plot_4_1_c_race(df):
    stackbar_percent(
        df,
        path_html="html/4.1(c)_TenureByRace.html",
        div_id="4.1.c_TenureByRace",
        x="Race",
        y="share",
        facet="Geography",
        color="Tenure",
        color_sequence=["#208385", "#FC9A62"],
        orders={
            "Race": ["White", "Black", "Asian", "NHPI", "Some Other"],
            "Geography": ["Basin", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Race",
        x_title="Race",
        hovertemplate="%{y}",
        hovermode="x unified",
    )


def get_data_4_4_a():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
    mask1 = (data["Category"] == "Race and Ethnicity") & (data["year_sample"] != 2020)
    mask2 = (
        (data["Category"] == "Race and Ethnicity")
        & (data["year_sample"] == 2020)
        & (data["sample_level"] == "block group")
    )
    df1 = data[mask1]
    df2 = data[mask2]
    val = pd.concat([df1, df2], ignore_index=True)
    val = val.loc[:, ["variable_name", "value", "Geography", "year_sample"]].rename(
        columns={"year_sample": "Year", "variable_name": "Race"}
    )
    # val = bind data1 and data2
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
            "Total population:  Not Hispanic or Latino; Some other race alone": "Some Other",
            "Total population:  Not Hispanic or Latino; Two or more races": "Multi",
        }
    )
    df = df.sort_values("Year")
    return df


def plot_4_4_a(df):
    stackbar_percent(
        df,
        path_html="html/4.4(a)_RaceEthnicity_v1.html",
        div_id="4.4.a_RaceEthnicity_v1",
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
        orders={"Geography": ["Basin", "South Lake", "North Lake"]},
        y_title="% of Race and Ethnicity of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
    )
    groupedbar_percent(
        df,
        path_html="html/4.4(a)_RaceEthnicity_v2.html",
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
        orders={"Geography": ["Basin", "South Lake", "North Lake"]},
        y_title="% of Race and Ethnicity of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
    )
