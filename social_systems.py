import numpy as np

from utils import get_fs_data, stackbar_percent


def get_data_4_1_b():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
    mask = data["Category"] == "Race and Ethnicity"
    val = (
        data[mask]
        .loc[:, ["variable_name", "value", "Geography", "year_sample"]]
        .rename(columns={"year_sample": "Year", "variable_name": "Race"})
    )
    total = val.groupby(["Geography", "Year"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Year"],
        right_on=["Geography", "Year"],
        suffixes=("", "_total"),
    )
    df["Year"] = df["Year"].astype(str)
    df["share"] = df["value"] / df["value_total"]
    df["Race"] = np.where(
        df["Race"] == "Total population:  Hispanic or Latino",
        "Hispanic",
        np.where(
            df["Race"] == "Total population:  Not Hispanic or Latino; White alone",
            "White",
            np.where(
                df["Race"]
                == "Total population:  Not Hispanic or Latino; Not Hispanic or Latino; American Indian and Alaska Native alone",
                "AIAN",
                np.where(
                    df["Race"]
                    == "Total population:  Not Hispanic or Latino; Black or African American alone",
                    "Black",
                    np.where(
                        df["Race"] == "Total population:  Not Hispanic or Latino; Asian",
                        "Asian",
                        np.where(
                            df["Race"]
                            == "Total population:  Not Hispanic or Latino; Native Hawaiian and Other Pacific Islander alone",
                            "NHPI",
                            np.where(
                                df["Race"]
                                == "Total population:  Not Hispanic or Latino; Some other race alone",
                                "Some Other",
                                "Multi",
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    df = df.sort_values("Year")
    return df


def plot_4_1_b(df):
    stackbar_percent(
        df,
        path_html="html/4.1(b)_RaceEthnicity.html",
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
        y_title="% of Home Energy Sources by Share of Total",
        x_title="Year",
    )


def get_data_4_1_d_age():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
    mask = data["Category"] == "Tenure by Age"
    val = (
        data[mask]
        .loc[:, ["variable_name", "value", "Geography"]]
        .rename(columns={"variable_name": "Age"})
    )
    val["Tenure"] = np.where(
        val["Age"].str.startswith("Owner"), "Owner Occupied", "Renter Occupied"
    )
    total = val.groupby(["Geography", "Tenure"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Tenure"],
        right_on=["Geography", "Tenure"],
        suffixes=("", "_total"),
    )
    df["share"] = df["value"] / df["value_total"]
    df["Age"] = np.where(
        df["Age"].str.contains("15"),
        "15 to 24 Years",
        np.where(
            df["Age"].str.contains("25"),
            "25 to 34 Years",
            np.where(
                df["Age"].str.contains("35"),
                "35 to 44 Years",
                np.where(
                    df["Age"].str.contains("45"),
                    "45 to 54 Years",
                    np.where(
                        df["Age"].str.contains("55"),
                        "55 to 59 Years",
                        np.where(
                            df["Age"].str.contains("60"),
                            "60 to 64 Years",
                            np.where(
                                df["Age"].str.contains("65"),
                                "65 to 74 Years",
                                np.where(
                                    df["Age"].str.contains("75"), "75 to 84 Years", "85+ Years"
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
    return df


def plot_4_1_d_age(df):
    stackbar_percent(
        df,
        path_html="html/4.1(d)_TenureByAge.html",
        x="Tenure",
        y="share",
        facet="Geography",
        color="Age",
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
        y_title="% of Tenure by Age",
        x_title="Tenure",
    )


def get_data_4_1_d_race():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
    mask = data["Category"] == "Tenure by Race"
    val = (
        data[mask]
        .loc[:, ["variable_name", "value", "Geography"]]
        .rename(columns={"variable_name": "Race"})
    )
    val["Tenure"] = np.where(
        val["Race"].str.startswith("Owner"), "Owner Occupied", "Renter Occupied"
    )
    val = val[(~val["Race"].str.contains("Total"))]
    total = val.groupby(["Geography", "Tenure"]).sum()
    df = val.merge(
        total,
        left_on=["Geography", "Tenure"],
        right_on=["Geography", "Tenure"],
        suffixes=("", "_total"),
    )
    df["share"] = df["value"] / df["value_total"]
    df["Race"] = np.where(
        df["Race"].str.contains("Asian"),
        "Asian",
        np.where(
            df["Race"].str.contains("Black"),
            "Black",
            np.where(
                df["Race"].str.contains("Native Hawaiian"),
                "NHPI",
                np.where(
                    df["Race"].str.contains("Some"),
                    "Some Other",
                    np.where(df["Race"].str.contains("White"), "White", "AIAN"),
                ),
            ),
        ),
    )
    return df


def plot_4_1_d_race(df):
    stackbar_percent(
        df,
        path_html="html/4.1(d)_TenureByRace.html",
        x="Tenure",
        y="share",
        facet="Geography",
        color="Race",
        color_sequence=["#208385", "#FC9A62", "#F9C63E", "#632E5A", "#A48352", "#BCEDB8"],
        y_title="% of Tenure by Race",
        x_title="Tenure",
    )
