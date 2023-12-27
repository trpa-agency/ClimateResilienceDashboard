from utils import read_file, stackbar_percent


def get_data_3_2_a():
    return read_file("data/EnergyMix_long.csv")


def plot_3_2_a(df):
    stackbar_percent(
        df,
        path_html="html/3.2(a)_EnergyMix.html",
        x="Year",
        y="Share",
        facet="Source",
        color="Type",
        y_title="% of Renewable Energy by Share of Total",
        x_title="Year",
    )
