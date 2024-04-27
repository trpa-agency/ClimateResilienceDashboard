import numpy as np
import pandas as pd
import plotly.express as px

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
    # change value Community Defense Zone to Defense Zone for consistency
    df["Treatment Zone"] = df["Treatment Zone"].replace("Community Defense Zone", "Defense Zone")
    df["Year"] = df["Year"].astype(str)
    df = df.groupby(["Year", "Treatment Zone"]).agg({"Acres": "sum"}).reset_index()
    return df


def plot_forest_fuel(df):
    stackedbar(
        df,
        path_html="html/2.1.a_ForestFuel.html",
        div_id="2.1.a_ForestFuel",
        x="Year",
        y="Acres",
        facet=None,
        color="Treatment Zone",
        # color_sequence=["#208385", "#FC9A62", "#F9C63E", "#632E5A", "#A48352", "#BCEDB8"],
        color_sequence=["#ABCD66", "#E69800", "#A87000", "#F5CA7A"],
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
        y_title="Acres Treated",
        x_title="Year",
        custom_data=["Treatment Zone"],
        hovertemplate="<br>".join(
            ["<b>%{y:,.0f} acres</b> of forest health treatment", "in the <i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
        additional_formatting=dict(
            # title = "Forest Health Treatment",
            legend=dict(
                title= "Forest Health Treatment Zone",
                orientation="h",
                entrywidth=85,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
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
        path_html="html/2.1.b_OldGrowthForest_SeralStage.html",
        div_id="2.1.b_OldGrowthForest_SeralStage",
        x="SeralStage",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Seral Stage",
        custom_data=["SeralStage"],
        hovertemplate="<br>".join(["<b>%{y:,.0f}</b> acres of", "<i>%{customdata[0]}</i> forest"])
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
    structure = df.groupby("SpatialVar").agg({"Acres": "sum"}).reset_index()
    stackedbar(
        structure,
        path_html="html/2.1.b_OldGrowthForest_Structure.html",
        div_id="2.1.b_OldGrowthForest_Structure",
        x="SpatialVar",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Structure",
        custom_data=["SpatialVar"],
        hovertemplate="<br>".join(
            ["<b>%{y:,.0f}</b> acres of", "<i>%{customdata[0]}</i> old growth forest"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )
    species = df.groupby("TRPA_VegType").agg({"Acres": "sum"}).reset_index()
    stackedbar(
        species,
        path_html="html/2.1.b_OldGrowthForest_Species.html",
        div_id="2.1.b_OldGrowthForest_Species",
        x="TRPA_VegType",
        y="Acres",
        facet=None,
        color=None,
        color_sequence=["#208385"],
        orders=None,
        y_title="Acres",
        x_title="Vegetation Type",
        custom_data=["TRPA_VegType"],
        hovertemplate="<br>".join(
            ["<b>%{y:,.0f}</b> acres of", "<i>%{customdata[0]}</i> old growth forest"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
    )


def get_probability_of_high_severity_fire():
    highseverity = get_fs_data_spatial(
        "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/129"
    )
    df = highseverity.groupby(["Name", "gridcode"])["Acres"].sum().reset_index()
    df["Probability"] = np.where(
        df["gridcode"] == 1, "High Severity Fire", "Low to Moderate Severity Fire"
    )

    # standardize values to "Wilderness"
    df.loc[
        df["Name"].isin(
            ["Desolation Wilderness", "Mt. Rose Wilderness", "Granite Chief Wilderness"]
        )
    ] = "Wilderness"

    total = df.groupby("Name")["Acres"].sum().reset_index()

    df = df.merge(total, on="Name")
    df["Share"] = df["Acres_x"] / df["Acres_y"]
    df = df.rename(
        columns={"Name": "Forest Management Zone", "Acres_x": "Acres", "Acres_y": "Total"}
    )
    return df


# def get_probability_of_low_severity_fire():
#     lowseverity = get_fs_data_spatial(
#         "https://maps.trpa.org/server/rest/services/LTinfo_Climate_Resilience_Dashboard/MapServer/130"
#     )
#     df = lowseverity.groupby(["Name", "gridcode"])["Acres"].sum().reset_index()
#     df["Probability"] = np.where(df["gridcode"] == 1, "High Risk of Fire", "Low Risk of Fire")

#     # change Desolation Wilderness, Mt. Rose Wilderness, and Granite Chief Wilderness to "Wilderness"
#     df.loc[df["Name"].isin(
#         ["Desolation Wilderness", "Mt. Rose Wilderness", "Granite Chief Wilderness"])] = "Wilderness"

#     total = df.groupby("Name")["Acres"].sum().reset_index()

#     df = df.merge(total, on="Name")
#     df["Share"] = df["Acres_x"] / df["Acres_y"]
#     df = df.rename(
#         columns={"Name": "Forest Management Zone", "Acres_x": "Acres", "Acres_y": "Total"}
#     )
#     return df


def plot_probability_of_high_severity_fire(df):
    stackedbar(
        df,
        path_html="html/2.1.c_Probability_of_High_Severity_Fire.html",
        div_id="2.1.c_Probability_of_High_Severity_Fire",
        x="Forest Management Zone",
        y="Share",
        facet=None,
        color="Probability",
        color_sequence=["#208385", "#FCB42C"],
        orders=None,
        y_title="",
        x_title="Forest Management Zone",
        custom_data=["Probability"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0%}</b> of the forested area is", "likely to burn as <i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=".0%",
    )


# def plot_probability_of_low_severity_fire(df):
#     stackedbar(
#         df,
#         path_html="html/2.1.c_Probability_of_Low_Severity_Fire.html",
#         div_id="2.1.c_Probability_of_Low_Severity_Fire",
#         x="Forest Management Zone",
#         y="Share",
#         facet=None,
#         color="Probability",
#         color_sequence=["#208385", "#FCB42C"],
#         orders=None,
#         y_title="",
#         x_title="Forest Management Zone",
#         hovertemplate="%{y}",
#         hovermode="x unified",
#         orientation=None,
#         format=".0%",
#     )


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
    # filter out Terrestrial from Invasive Species Type
    data = data.loc[data["Invasive Species Type"] != "Terrestrial"]
    df = data.groupby(["Year", "Invasive Species Type"])["Acres"].sum().reset_index()
    return df


def plot_aquatic_species(df):
    trendline(
        df,
        path_html="html/2.2.a_Aquatic_Species.html",
        div_id="2.2.a_Aquatic_Species",
        x="Year",
        y="Acres",
        color="Invasive Species Type",
        # color_sequence=["#023f64", "#7ebfb5"],
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
        hovermode="x unified",
        custom_data=None,
        additional_formatting=dict(
            title="Aquatic Invasive Species Treatment",
            margin=dict(t=20),
            # turn off legend
            showlegend=False,
        ),
    )

def plot_aquatic_species_bar(df):
    stackedbar(
        df,
        path_html="html/2.2.a_Aquatic_Species.html",
        div_id="2.2.a_Aquatic_Species",
        x="Year",
        y="Acres",
        color="Invasive Species Type",
        color_sequence=["#023f64", "#7ebfb5"],
        facet=None,
        orders=None,
        x_title="Year",
        y_title="Acres",
        custom_data=["Invasive Species Type"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0f} acres</b> of", "<i>%{customdata[0]}</i> invasive species treated"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
        additional_formatting=dict(
            title=dict(text="Aquatic Invasive Species Treatment",
                    x=0.05,
                    y=0.95,
                    xanchor="left",
                    yanchor="top",
                    font=dict(size=16),
                    automargin=True),
            margin=dict(t=20),
            # turn off legend
            showlegend=False,
        ),
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
    # # add SEZ Restored to the Action Performed column
    # df["Action Performed"] = df["Action Performed"].replace("Restored", "SEZ Restored")

    return df


def plot_restored_wetlands_meadows(df):
    trendline(
        df,
        path_html="html/2.3.a_Restored_Wetlands_Meadows.html",
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
        custom_data=["Action Performed"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0f}</b> acres of", "wetlands and meadows <i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        markers=True,
        hover_data=None,
        tickvals=None,
        ticktext=None,
        tickangle=None,
        hovermode="x unified",
    )


def plot_restored_wetlands_meadows_bar(df):
    stackedbar(
        df,
        path_html="html/2.3.a_Restored_Wetlands_Meadows.html",
        div_id="2.3.a_Restored_Wetlands_Meadows",
        x="Year",
        y="Acres",
        color="Action Performed",
        color_sequence=["#023f64", "#7ebfb5"],
        orders=None,
        x_title="Year",
        y_title="Acres",
        facet=None,
        custom_data=["Action Performed"],
        hovertemplate="<br>".join(
            ["<b>%{y:.0f} acres</b> of wetlands and meadows", "<i>%{customdata[0]}</i>"]
        )
        + "<extra></extra>",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=120,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
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
    bmpsCertByYear["Developed Parcels with BMPs"] = bmpsCertByYear["OBJECTID"].cumsum()
    # BMPs installed per year compared to total developed parcels per year
    bmpsCertByYear["BMPs per Developed Parcel"] = (
        bmpsCertByYear["Developed Parcels with BMPs"] / bmpsCertByYear["Developed Parcels"]
    ).round(2)
    # BMPs installed per year compared to total developed parcels per year but subtracting the BMPs installed from the total developed parcels
    bmpsCertByYear["Developed Parcels without BMPs"] = (
        bmpsCertByYear["Developed Parcels"] - bmpsCertByYear["Developed Parcels with BMPs"]
    )
    # drop objectid
    df = bmpsCertByYear.drop(columns=["OBJECTID"])
    return df


def plot_bmp(df):
    stackedbar(
        df,
        path_html="html/2.3.b_BMP.html",
        div_id="2.3.b_BMP",
        x="Year",
        y=["Developed Parcels with BMPs", "Developed Parcels without BMPs"],
        facet=None,
        color=None,
        color_sequence=["#208385", "#808080"],
        orders=None,
        y_title="Developed Parcels",
        x_title="Year",
        hovertemplate="%{y:,.0f}",
        hovermode="x unified",
        orientation=None,
        custom_data=None,
        format=",.0f",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=190,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
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
    sdf_impervious_hard_summary["Total Acres Treated"] = sdf_impervious_hard_summary[
        "Acres"
    ].cumsum()
    # subtract area covereed by cumulatve sum from total acres
    sdf_impervious_hard_summary["Total Acres Untreated"] = (
        total_acres - sdf_impervious_hard_summary["Total Acres Treated"]
    )
    df = sdf_impervious_hard_summary
    return df


def plot_areawide(df):
    stackedbar(
        df,
        path_html="html/2.4.c_Areawide_Covering_Impervious.html",
        div_id="2.4.c_Areawide",
        x="Year_Completed",
        y=["Total Acres Treated", "Total Acres Untreated"],
        facet=None,
        color=None,
        color_sequence=["#208385", "#808080"],
        orders=None,
        y_title="Acres",
        x_title="Year",
        hovermode="x unified",
        orientation=None,
        format=",.0f",
        # custom_data = list(df.columns[3:],
        # hovertemplate="<br>".join([
        #     "b>%{y:,.0f}</b> of <b>%{customdata}</b>",
        #     "by areawide stormwater infrastructure"
        #         ]) +"<extra></extra>",
        custom_data=None,
        hovertemplate="%{y:,.0f}",
        additional_formatting=dict(
            legend=dict(
                orientation="h",
                entrywidth=130,
                yanchor="bottom",
                y=1.05,
                xanchor="right",
                x=0.95,
            )
        ),
    )


def get_veg():
    dfVeg = get_fs_data("https://maps.trpa.org/server/rest/services/LTInfo_Monitoring/MapServer/91")
    # selecvegetation
    df = dfVeg.loc[(dfVeg["Development"] == "Undeveloped")]

    # change name SUM_Acres to Acres
    df = df.rename(columns={"SUM_Acres": "Acres"})
    # create pivot table
    table = pd.pivot_table(df, values=["Acres"], index=["TRPA_VegType"], aggfunc=np.sum)
    # flatten the pivot table
    flattened = pd.DataFrame(table.to_records())
    flattened.columns = [
        hdr.replace("('Acres', '", "").replace("')", "") for hdr in flattened.columns
    ]
    df = flattened
    df["TRPA_VegType"].replace("", np.nan, inplace=True)
    df = df.dropna(subset=["TRPA_VegType"])
    df["TotalAcres"] = 171438.19  # total acres of undisturbed vegetation
    df["VegPercent"] = (df["Acres"] / df["TotalAcres"]) * 100
    return df


def plot_veg(df):
    df,
    path_html = "html/2.1.b_VegetationType.html"
    div_id = "2.1.b_VegetationType"
    x = "TRPA_VegType"
    y = "VegPercent"
    facet = None
    color = "TRPA_VegType"
    color_sequence = [
        "#9ed7c2",
        "#cdf57a",
        "#b4d79e",
        "#ff0000",
        "#a5f57a",
        "#00a820",
        "#df73ff",
        "#3e72b0",
        "#2f3f56",
        "#a8a800",
    ]
    orders = None
    y_title = ("Acres",)
    x_title = ("Vegetatoin Type",)
    hovertemplate = ("%{y:,.0f}",)
    hovermode = "x unified"
    orientation = None
    format = ",.0f"
    custom_data = ["Acres", "TotalAcres"]

    additional_formatting = dict(
        # title="Vegetation Type % Abundance",
        hovermode="x unified",
        barmode="overlay",
        xaxis=dict(tickmode="linear", title_text="Vegetation Type"),
        yaxis=dict(
            tickmode="linear",
            tick0=0,
            dtick=10,
            ticksuffix="%",
            range=[0, 60],
            title_text="% of undisturbed vegetation",
        ),
        # turn off legend
        showlegend=False,
    )

    config = {"displayModeBar": False}
    # create the plot
    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode="stack",
        facet_col=facet,
        # facet_row=facet_row,
        color_discrete_sequence=color_sequence,
        category_orders=orders,
        orientation=orientation,
        custom_data=custom_data,
    )

    fig.update_traces(
        name="",
        hovertemplate="<br>".join(
            [
                "<b>%{y:.1f}%</b> or <i>%{customdata[0]:,.0f}</i> acres",
                "of the total undisturbed vegetation",
                "(%{customdata[1]:,.0f} acres)",
            ]
        ),
    )

    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    fig.update_layout(
        # yaxis=dict(tickformat=format, hoverformat=format, title=y_title),
        # xaxis=dict(title=x_title),
        hovermode=hovermode,
        template="plotly_white",
        dragmode=False,
        legend_title=None,
        legend=dict(
            orientation="h",
            entrywidth=80,
            # entrywidthmode="fraction",
            yanchor="bottom",
            y=1,
            xanchor="right",
            x=1,
        ),
    )
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True, tickformat=format))
    fig.update_xaxes(tickformat=".0f")
    fig.update_layout(additional_formatting)

    fig.write_html(
        config=config,
        file=path_html,
        include_plotlyjs="directory",
        div_id=div_id,
    )
