from utils import get_fs_data, stackedbar


def get_data_forest_fuel():
    df = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/9"
    )
    df["Year"] = ""
    return df


def plot_forest_fuel(df):
    stackedbar(
        df,
        path_html="html/2.1(a)_ForestFuel.html",
        div_id="2.1.a_ForestFuel",
        x="Acres",
        y="Year",
        facet=None,
        color="Name",
        color_sequence=["#208385", "#FC9A62", "#F9C63E", "#632E5A", "#A48352", "#BCEDB8"],
        orders={
            "Name": [
                "WUI Defense Zone",
                "WUI Threat Zone",
                "Desolation Wilderness",
                "Granite Chief Wilderness",
                "Mt. Rose Wilderness",
                "General Forest",
            ],
        },
        y_title="",
        x_title="Acres",
        hovertemplate="%{x:.2f}",
        hovermode="y unified",
        orientation="h",
        format=",.0f",
    )
