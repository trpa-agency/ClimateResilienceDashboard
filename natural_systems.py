import pandas as pd

from utils import get_fs_data, stackedbar


def get_data_forest_fuel():
    eipForestTreatments = "https://www.laketahoeinfo.org/WebServices/GetReportedEIPIndicatorProjectAccomplishments/JSON/e17aeb86-85e3-4260-83fd-a2b32501c476/19"
    data = pd.read_json(eipForestTreatments)
    df = data[data["PMSubcategoryName1"] == "Treatment Zone"]
    df = df.rename(
        columns={
            "IndicatorProjectYear": "Year",
            "PMSubcategoryOption1": "Treatment Zone",
            "IndicatorProjectValue": "Acres",
        }
    )
    df["Year"] = df["Year"].astype(str)
    df = df.groupby(["Year", "Treatment Zone"]).agg({"Acres": "sum"}).reset_index()
    return df


def plot_forest_fuel(df):
    stackedbar(
        df,
        path_html="html/2.1(a)_ForestFuel.html",
        div_id="2.1.a_ForestFuel",
        x="Year",
        y="Acres",
        facet=None,
        color="Treatment Zone",
        color_sequence=["#208385", "#FC9A62", "#F9C63E", "#632E5A", "#A48352", "#BCEDB8"],
        orders={
            "Year": [
                "2007",
                "2008",
                "2009",
                "2010",
                "2011",
                "2012",
                "2013",
                "2014",
                "2015",
                "2016",
                "2017",
                "2018",
                "2019",
                "2020",
                "2021",
                "2022",
                "2023",
            ]
        },
        y_title="Acres",
        x_title="Year",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        orientation=None,
        format=".0f",
    )


def get_old_growth_forest():
    data = get_fs_data(
        "https://maps.trpa.org/server/rest/services/Vegetation_Late_Seral/FeatureServer/0"
    )
    # df = data.groupby(["SeralStage","SpatialVar"]).agg({"Acres": "sum"}).reset_index()
    df = data[["SeralStage", "SpatialVar", "TRPA_VegType", "Acres"]]
    return df


def plot_old_growth_forest(df):
    seral = df.groupby("SeralStage").agg({"Acres": "sum"}).reset_index()
    stackedbar(
        seral,
        path_html="html/2.1(b)_OldGrowthForest_SeralStage.html",
        div_id="2.1.b_OldGrowthForest_SeralStage",
        x="SeralStage",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Seral Stage",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
    structure = df.groupby("SpatialVar").agg({"Acres": "sum"}).reset_index()
    stackedbar(
        structure,
        path_html="html/2.1(b)_OldGrowthForest_Structure.html",
        div_id="2.1.b_OldGrowthForest_Structure",
        x="SpatialVar",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Structure",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
    species = df.groupby("TRPA_VegType").agg({"Acres": "sum"}).reset_index()
    stackedbar(
        species,
        path_html="html/2.1(b)_OldGrowthForest_Species.html",
        div_id="2.1.b_OldGrowthForest_Species",
        x="TRPA_VegType",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Vegetation Type",
        hovertemplate="%{y:.2f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
