import numpy as np
import pandas as pd

from utils import get_fs_data, get_fs_data_spatial, stackedbar, trendline


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


def get_probability_of_high_severity_fire():
    highseverity = get_fs_data_spatial(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/129"
    )
    df = highseverity.groupby(["Name", "gridcode"])["Acres"].sum().reset_index()
    df["Probability"] = np.where(df["gridcode"] == 1, "High Risk of Fire", "Low Risk of Fire")
    total = df.groupby("Name")["Acres"].sum().reset_index()
    df = df.merge(total, on="Name")
    df["Share"] = df["Acres_x"] / df["Acres_y"]
    df = df.rename(
        columns={"Name": "Forest Management Zone", "Acres_x": "Acres", "Acres_y": "Total"}
    )
    return df


def get_probability_of_low_severity_fire():
    lowseverity = get_fs_data_spatial(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/130"
    )
    df = lowseverity.groupby(["Name", "gridcode"])["Acres"].sum().reset_index()
    df["Probability"] = np.where(df["gridcode"] == 1, "High Risk of Fire", "Low Risk of Fire")
    total = df.groupby("Name")["Acres"].sum().reset_index()
    df = df.merge(total, on="Name")
    df["Share"] = df["Acres_x"] / df["Acres_y"]
    df = df.rename(
        columns={"Name": "Forest Management Zone", "Acres_x": "Acres", "Acres_y": "Total"}
    )
    return df


def plot_probability_of_high_severity_fire(df):
    stackedbar(
        df,
        path_html="html/2.1(c)_Probability_of_High_Severity_Fire.html",
        div_id="2.1.c_Probability_of_High_Severity_Fire",
        x="Forest Management Zone",
        y="Share",
        facet=None,
        color="Probability",
        color_sequence=["#208385", "#FC9A62"],
        orders=None,
        y_title="",
        x_title="Forest Management Zone",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


def plot_probability_of_low_severity_fire(df):
    stackedbar(
        df,
        path_html="html/2.1(c)_Probability_of_Low_Severity_Fire.html",
        div_id="2.1.c_Probability_of_Low_Severity_Fire",
        x="Forest Management Zone",
        y="Share",
        facet=None,
        color="Probability",
        color_sequence=["#208385", "#FC9A62"],
        orders=None,
        y_title="",
        x_title="Forest Management Zone",
        hovertemplate="%{y}",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


def get_data_aquatic_species():
    eipInvasive = "https://www.laketahoeinfo.org/WebServices/GetReportedEIPIndicatorProjectAccomplishments/JSON/e17aeb86-85e3-4260-83fd-a2b32501c476/15"
    data = pd.read_json(eipInvasive)
    data = data.rename(
        columns={
            "IndicatorProjectYear": "Year",
            "PMSubcategoryOption1": "Invasive Species Type",
            "IndicatorProjectValue": "Acres",
        }
    )
    df = data.groupby(["Year", "Invasive Species Type"])["Acres"].sum().reset_index()
    return df


def plot_aquatic_species(df):
    trendline(
        df,
        path_html="html/2.2(a)_Aquatic_Species.html",
        div_id="2.2.a_Aquatic_Species",
        x="Year",
        y="Acres",
        color="Invasive Species Type",
        color_sequence=["#023f64", "#7ebfb5"],
        sort="Year",
        orders=None,
        x_title="Year",
        y_title="Acres",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x",
    )


def get_data_restored_wetlands_meadows():
    eipSEZRestored = "https://www.laketahoeinfo.org/WebServices/GetReportedEIPIndicatorProjectAccomplishments/JSON/e17aeb86-85e3-4260-83fd-a2b32501c476/9"
    data = pd.read_json(eipSEZRestored)
    data = data.rename(
        columns={
            "IndicatorProjectYear": "Year",
            "PMSubcategoryOption1": "Action Performed",
            "IndicatorProjectValue": "Acres",
        }
    )
    df = data.groupby(["Year", "Action Performed"])["Acres"].sum().reset_index()
    return df


def plot_restored_wetlands_meadows(df):
    trendline(
        df,
        path_html="html/2.3(a)_Restored_Wetlands_Meadows.html",
        div_id="2.3.a_Restored_Wetlands_Meadows",
        x="Year",
        y="Acres",
        color="Action Performed",
        color_sequence=["#023f64", "#7ebfb5"],
        orders=None,
        sort="Year",
        x_title="Year",
        y_title="Acres",
        format=",.0f",
        hovertemplate="%{y:,.0f}",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x",
    )


def get_data_bmp():
    # BMP map service from BMP database
    bmpsLayer = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/121"
    # get data from map service
    data = get_fs_data(bmpsLayer)
    # select rows where BMPs CertificateIssued = 1 (True)
    data.loc[data["CertificateIssued"] == 1]
    # create Year column
    data["Year"] = pd.DatetimeIndex(data["CertDate"]).year
    # total bmps certified by year
    bmpsCertByYear = data.groupby("Year")["OBJECTID"].count().reset_index()
    # total developed parcel rows
    parcelsDeveloped = data.loc[~data["EXISTING_LANDUSE"].isin(["Vacant", "Open Space"])]
    # set total developed parcels field
    bmpsCertByYear["Developed Parcels"] = parcelsDeveloped["OBJECTID"].count()
    # cumulative sum of BMPs installed per year
    bmpsCertByYear["Total BMPs Installed"] = bmpsCertByYear["OBJECTID"].cumsum()
    # BMPs installed per year compared to total developed parcels per year
    bmpsCertByYear["BMPs per Developed Parcel"] = (
        bmpsCertByYear["Total BMPs Installed"] / bmpsCertByYear["Developed Parcels"]
    ).round(2)
    # BMPs installed per year compared to total developed parcels per year but subtracting the BMPs installed from the total developed parcels
    bmpsCertByYear["Developed Parcels without a BMP"] = (
        bmpsCertByYear["Developed Parcels"] - bmpsCertByYear["Total BMPs Installed"]
    )
    # drop objectid
    df = bmpsCertByYear.drop(columns=["OBJECTID"])
    return df


def plot_bmp(df):
    stackedbar(
        df,
        path_html="html/2.3(b)_BMP.html",
        div_id="2.3.b_BMP",
        x="Year",
        y=["Total BMPs Installed", "Developed Parcels without a BMP"],
        facet=None,
        color=None,
        color_sequence=["#208385", "#808080"],
        orders=None,
        y_title="Cumulative BMPs Installed",
        x_title="Year",
        hovertemplate="%{y:,.0f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )


def get_areawide_data():
    # areawide overlay URL
    areawideOverlay = "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/140"
    # get data from map service
    data = get_fs_data(areawideOverlay)
    # summarize total area of Surface = Hard Surface
    df = data.loc[data["Surface"] == "Hard"]
    # calculate total acres
    total_acres = df["Acres"].sum()
    # summarize the area of hard surface covered by status = completed or active
    sdf_impervious_hard_summary = (
        df.groupby(["Status", "Year_Completed"])["Acres"].sum().reset_index()
    )
    # sort years
    sdf_impervious_hard_summary = sdf_impervious_hard_summary.sort_values(by="Year_Completed")
    # filter out Status is not ''
    sdf_impervious_hard_summary = sdf_impervious_hard_summary[
        sdf_impervious_hard_summary["Status"] != ""
    ]
    # group status active and constructed to completed
    sdf_impervious_hard_summary["Status"] = sdf_impervious_hard_summary["Status"].replace(
        ["Active", "Constructed"], "Completed"
    )
    # create cumulative sum of acres of status - completed
    sdf_impervious_hard_summary["Acres Covered"] = sdf_impervious_hard_summary["Acres"].cumsum()
    # subtract area covereed by cumulatve sum from total acres
    sdf_impervious_hard_summary["Acres Remaining"] = (
        total_acres - sdf_impervious_hard_summary["Acres Covered"]
    )
    df = sdf_impervious_hard_summary
    return df


def plot_areawide(df):
    stackedbar(
        df,
        path_html="html/2.4.(c)_Areawide_Covering_Impervious.html",
        div_id="2.4.c_Areawide",
        x="Year_Completed",
        y=["Acres Covered", "Acres Remaining"],
        facet=None,
        color=None,
        color_sequence=["#208385", "#808080"],
        orders=None,
        y_title="Impervious Surface Covered by Stormwater Areawide Treatment",
        x_title="Year",
        hovertemplate="%{y:,.0f}",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
