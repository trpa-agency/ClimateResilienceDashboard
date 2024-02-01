from utils import barchart, get_fs_data


def get_data_forest_fuel():
    df = get_fs_data(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/9"
    )
    return df


def plot_forest_fuel(df):
    barchart(
        df,
        path_html="html/2.1(a)_ForestFuel.html",
        div_id="2.1.a_ForestFuel",
        x="Name",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
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
        y_title="Acres",
        x_title="Zone",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
    )
