from utils import get_fs_data, read_file, stackbar_percent


def get_data_3_1_b():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/128"
    )
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


def plot_3_1_b(df):
    stackbar_percent(
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
        orders={"Geography": ["Basin", "South Lake", "North Lake"]},
        y_title="% of Home Energy Sources by Share of Total",
        x_title="Year",
        hovertemplate="%{y}",
        hovermode="x unified",
    )


def get_data_3_2_a():
    return read_file("data/EnergyMix_long.csv")


def plot_3_2_a(df):
    stackbar_percent(
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
    )
