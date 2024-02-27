import climate_conditions

daily_updates = [
    climate_conditions.GreenHouseGas,
]

weekly_updates = []

monthly_updates = []

yearly_updates = []


def run_updates(update_list):
    for viz_class in update_list:
        df = viz_class.get_data()
        viz_class.plot(df)
        # HTML files will be formatted in Github by pre-commit.ci


run_updates(daily_updates)
