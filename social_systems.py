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
