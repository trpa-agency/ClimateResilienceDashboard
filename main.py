import subprocess

import climate_conditions

daily_visualizations = [
    climate_conditions.GreenHouseGas,
]

weekly_visualizations = []

monthly_visualizations = []

yearly_visualizations = []


def call_prettier(filepath):
    """Calls prettier to format the HTML file.

    This may only work on Unix-like systems.
    """
    result = subprocess.run(["npx", "--yes", "prettier", "--write", filepath], capture_output=True)
    if result.stdout:
        print(result.stdout.decode())
    if result.stderr:
        print(result.stderr.decode())


def update_html(viz_class):
    df = viz_class.get_data()
    viz_class.plot(df)
    # potentially wrap in try/except here
    call_prettier(viz_class.filepath)
    # Alternative would be to use something like pre-commit.ci to run prettier on all PRs


for viz in daily_visualizations:
    update_html(viz)
