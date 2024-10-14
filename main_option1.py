from schedule import every, repeat, run_pending
import time
import os
import subprocess
import datetime
import logging
from climate_conditions import *


# Configure logging
logging.basicConfig(filename='task_scheduler.log', level=logging.INFO)
# .
# Inside execute_task function:
def execute_task(task_name, max_runtime, command):
    try:
        start_time = datetime.datetime.now()
        # Example: Run an external command as the task
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        process.communicate()
        exit_code = process.returncode
        end_time = datetime.datetime.now()
        runtime = (end_time - start_time).total_seconds() / 3600  # Calculate runtime in hours
        if runtime > max_runtime:
            logging.warning(f"Task '{task_name}' exceeded max runtime ({max_runtime} hours) and was terminated.")
            process.terminate()  # Terminate the task
        else:
            logging.info(f"Task '{task_name}' completed in {runtime:.2f} hours.")
            if exit_code != 0:
                logging.error(f"Task '{task_name}' encountered an error. Exit code: {exit_code}")
    except Exception as e:
        logging.error(f"Error executing task '{task_name}': {str(e)}")


# schedule get_data_temp function to run every 15 minutes
every(15).minutes.do(get_data_temp())
# then schedule plot_temp to run when get_data_temp is done
os.wait(get_data_temp())

# Define the schedule of the system
every(15).minutes.do(get_data_temp())

# schedule plot_temp function to wait until return of get_data_temp
every(15).minutes.do(plot_temp())

while True:
    run_pending()
    time.sleep(1)