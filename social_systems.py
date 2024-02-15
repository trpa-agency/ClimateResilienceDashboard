import numpy as np
import pandas as pd

from utils import get_fs_data, groupedbar_percent, read_file, stackedbar, trendline


def get_data_tenure_by_age():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/134"
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


def plot_tenure_by_age(df):
    stackedbar(
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
            "Geography": ["Lake Tahoe Region", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Age",
        x_title="Age",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


def get_data_tenure_by_race():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/134"
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


def plot_tenure_by_race(df):
    stackedbar(
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
            "Geography": ["Lake Tahoe Region", "South Lake", "North Lake"],
        },
        y_title="% of Tenure by Race",
        x_title="Race",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


def get_data_race_ethnicity():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/134"
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
            "Total population:  Not Hispanic or Latino; Some other race alone": "Some Other",
            "Total population:  Not Hispanic or Latino; Two or more races": "Multi",
        }
    )
    df = df.sort_values("Year")
    return df


def plot_race_ethnicity(df):
    stackedbar(
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
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="% of Race and Ethnicity of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
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
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="% of Race and Ethnicity of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
        format=".0%",
    )


def get_data_household_income():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/134"
    )
    df = data[data["Category"] == "Household Income"]
    df["Geography"] = df["Geography"].replace({"Basin": "Lake Tahoe Region"})
    df = df.rename(columns={"year_sample": "Year"})
    return df


def plot_household_income(df):
    groupedbar_percent(
        df,
        path_html="html/4.1(a)_Household_Income_v1.html",
        div_id="4.1.a_Household_Income_v1",
        x="Year",
        y="value",
        facet="Geography",
        color="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A"],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        y_title="Median Household Income ($)",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
        format=",.0f",
    )
    trendline(
        df,
        path_html="html/4.1(a)_Household_Income_v2.html",
        div_id="4.1.a_Household_Income_v2",
        x="Year",
        y="value",
        color="Geography",
        color_sequence=["#208385", "#FC9A62", "#632E5A"],
        orders={"Geography": ["Lake Tahoe Region", "South Lake", "North Lake"]},
        sort="Year",
        x_title="Year",
        y_title="Median Household Income ($)",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
    )


def get_data_rent_prices():
    return read_file("data/CoStar/LakeTahoe_MF_AllBeds.csv")


def plot_rent_prices(df):
    trendline(
        df,
        path_html="html/4.1(b)_Rent_Prices.html",
        div_id="4.1.b_Rent_Prices",
        x="Period",
        y="Effective Rent Per Unit",
        color=None,
        color_sequence=["#208385"],
        sort="Period",
        orders=None,
        x_title="Year",
        y_title="Rent Prices ($)",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
    )


def get_data_median_home_price():
    price19 = read_file(
        "~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/Tahoe_PropertyRadar_2019.csv"
    )
    price20 = read_file(
        "~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/Tahoe_PropertyRadar_2020.csv"
    )
    price21 = read_file(
        "~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/Tahoe_PropertyRadar_2021.csv"
    )
    price22 = read_file(
        "~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/Tahoe_PropertyRadar_2022.csv"
    )
    price23_24 = read_file(
        "~/Dropbox (ECONW)/25594 TRPA Climate Dashboard/Data/PropertyRadar/Tahoe_PropertyRadar_2023to2024.csv"
    )
    data = pd.concat([price19, price20, price21, price22, price23_24], ignore_index=True)
    data = data[
        (data["City"] != "Truckee")
        & (
            data["Purchase Date"]
            != "The information contained in this report is subject to the license restrictions and all other terms contained in PropertyRadar.com's User Agreement."
        )
    ]
    data["Purchase Date"] = pd.to_datetime(data["Purchase Date"])
    data.drop_duplicates(inplace=True)
    data = data[data["Purchase Date"].dt.year >= 2019]
    data["year"] = data["Purchase Date"].dt.year
    data["month"] = data["Purchase Date"].dt.month
    df = data.groupby(["year", "month"])["Purchase Amt"].median().reset_index()
    df["Month"] = df["year"].astype(int).astype(str) + "-" + df["month"].astype(int).astype(str)
    df = df.dropna()
    df.to_csv("data/property_radar.csv")
    return df


def plot_median_home_price(df):
    trendline(
        df,
        path_html="html/4.1(b)_Median_Sale_Prices.html",
        div_id="4.1.b_Median_Sale_Prices",
        x="Month",
        y="Purchase Amt",
        color=None,
        color_sequence=["#208385"],
        orders=None,
        sort=["year", "month"],
        x_title="Sale Date",
        y_title="Median Sale Price ($)",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
    )
