import datetime
import glob
import json
import time

import pandas as pd
import requests as rq
from tqdm import tqdm

# Insert API key here
api_key = "INSERT API KEY HERE"


def check_api_key(api_key=api_key):
    """Function to check if the API Key being used is valid"""
    key_check = rq.get("https://api.purpleair.com/v1/keys", params={"api_key": api_key}).json()
    try:
        if key_check["error"]:
            print("Invalid key")
    except KeyError:
        return None


## All censors in Bounding box
# Bounding box used: {"xmax" : -119.91367, "ymax" : 39.27833, "xmin" : -120.18534, "ymin" : 38.92124}

tahoe_bbox = {"xmax": -119.91367, "ymax": 39.27833, "xmin": -120.18534, "ymin": 38.92124}


def get_sensor_list(bbox):
    """Function to create list of all sensors in a bounding box"""
    sensor_list = rq.get(
        "https://api.purpleair.com/v1/sensors",
        headers={"X-API-Key": api_key},
        params={
            "nwlng": str(bbox["xmin"]),
            "nwlat": str(bbox["ymax"]),
            "selng": str(bbox["xmax"]),
            "selat": str(bbox["ymin"]),
            "fields": "latitude,longitude,date_created,last_seen",
            "max_age": 0,
        },
    )
    try:
        if sensor_list.json()["error"]:
            print("API Call failed. Error message: " + str(sensor_list.json()["error"]))
    except KeyError:
        writeout_time = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
        with open("./data/PurpleAir/bbox_sensor_list_" + writeout_time + ".json", "w") as outfile:
            json.dump(sensor_list.json(), outfile)
        sensor_table = pd.DataFrame(
            data=sensor_list.json()["data"], columns=sensor_list.json()["fields"]
        )
        sensor_table["date_created"] = pd.to_datetime(sensor_table["date_created"], unit="s")
        sensor_table["last_seen"] = pd.to_datetime(sensor_table["last_seen"], unit="s")

        sensor_table.to_csv(
            "./data/PurpleAir/bbox_sensor_table" + writeout_time + ".csv", index=False
        )
        print("API call successful. Data saved as " + writeout_time + ".json")
    return sensor_table


# sensor_list = get_sensor_list(tahoe_bbox)
sensor_list = pd.read_csv("data/PurpleAir/bbox_sensor_table2024-02-01_13:19.csv")


def get_sensor_year_data(api_fields, sensor_index, start_timetuple, end_timetuple, api_key=api_key):
    """Function to make single API call. Start and end (year, month) as tuple"""
    sensor_year = rq.get(
        f"https://api.purpleair.com/v1/sensors/{sensor_index}/history",
        headers={"X-API-Key": api_key},
        params={
            "start_timestamp": str(time.mktime(start_timetuple)),
            "end_timestamp": str(time.mktime(end_timetuple)),
            "average": "1440",
            "fields": api_fields,
        },
    ).json()
    return sensor_year


def test_api_error(api_output):
    """Function to test if API call returned any errors"""
    try:
        if api_output["error"]:
            return api_output["error"]
    except KeyError:
        return None


def pull_all_sensor_data(sensor_table, fields="pm2.5_alt_a, pm2.5_alt_b"):
    """Function to pull data for all sensors from table created using `get_sensor_list` function upto Jan 31, 2024"""
    for sensor_number in tqdm(range(len(sensor_table))):
        sensor_info = sensor_table.iloc[sensor_number]
        sensor_created = pd.Timestamp(sensor_info["date_created"]).floor("d")
        sensor_last_seen = pd.Timestamp(sensor_info["last_seen"]).ceil("d")
        tqdm.write(
            f"Pulling data for sensor {sensor_info['sensor_index']} \nSensor active from {sensor_created.date()} to {sensor_last_seen.date()} = {(sensor_last_seen-sensor_created).days} days"
        )
        expected_output_rows = (sensor_last_seen - sensor_created).days
        sensor_data = []
        start_timetuple = sensor_created
        end_timetuple = sensor_created + pd.Timedelta(365, "d")
        pbar = tqdm(total=((expected_output_rows / 365) // 1) + 1)
        while start_timetuple < sensor_last_seen:
            if end_timetuple > sensor_last_seen:
                end_timetuple = sensor_last_seen

            tqdm.write(f"From {start_timetuple.date()} to {end_timetuple.date()}")

            sensor_year_data = get_sensor_year_data(
                api_key=api_key,
                api_fields=fields,
                sensor_index=sensor_info["sensor_index"],
                start_timetuple=start_timetuple.timetuple(),
                end_timetuple=end_timetuple.timetuple(),
            )

            test_result = test_api_error(sensor_year_data)
            if not test_result:
                pass
            elif test_result == "RateLimitExceededError":
                time.sleep(5)
                sensor_year_data = get_sensor_year_data(
                    api_key=api_key,
                    api_fields=fields,
                    sensor_index=sensor_info["sensor_index"],
                    start_timetuple=start_timetuple,
                    end_timetuple=end_timetuple,
                )
                test_result = test_api_error(sensor_year_data)
                if test_result:
                    import pdb

                    pdb.set_trace()
            elif test_result != "RateLimitExceededError":
                tqdm.write(
                    f"API for sensor {sensor_info['sensor_index']} failed. Error message:{test_result}"
                )
                import pdb

                pdb.set_trace()

            sensor_data.append(
                pd.DataFrame(data=sensor_year_data["data"], columns=sensor_year_data["fields"])
            )
            time.sleep(1.5)
            pbar.update(1)
            start_timetuple = end_timetuple
            end_timetuple = end_timetuple + pd.Timedelta(365, "d")
            pass

        pbar.close()
        sensor_data = pd.concat(sensor_data)
        import pdb

        pdb.set_trace()
        sensor_data["time_stamp"] = pd.to_datetime(sensor_data["time_stamp"], unit="s")
        sensor_data["sensor_index"] = sensor_info["sensor_index"]
        # assert abs(1 - (expected_output_rows / len(sensor_data))) < 0.1
        sensor_data.to_csv(
            f"./data/PurpleAir/all_sensors/sensor_{sensor_info['sensor_index']}.csv", index=False
        )
    return sensor_data


def make_unified_time_series():
    """Function will pool all files in data/PurpleAir/all_sensors and convert it to an average value timeseries"""
    all_sensor_data = []
    for file in tqdm(glob.glob("data/PurpleAir/all_sensors/*.csv")):
        all_sensor_data.append(pd.read_csv(file))
    all_sensor_data = pd.concat(all_sensor_data)
    all_sensor_data = all_sensor_data.rename(
        columns={"pm2.5_alt_a": "pm25_a", "pm2.5_alt_b": "pm25_b"}
    )
    # order both index and columns
    all_sensor_data.sort_values(["time_stamp", "sensor_index"], inplace=True)
    all_sensor_data = all_sensor_data[["time_stamp", "sensor_index", "pm25_a", "pm25_b"]]

    # Reliablity metrics removes observations where channel A and B differ by:
    # ± 5 ug/m^3
    # ± 56% measured value
    all_sensor_data = all_sensor_data.assign(
        one_channel_offline=lambda x: (x["pm25_a"].isnull() | x["pm25_b"].isnull()),
        both_channel_offline=lambda x: (x["pm25_a"].isnull() & x["pm25_b"].isnull()),
        abs_test_pass=lambda x: abs(all_sensor_data["pm25_a"] - all_sensor_data["pm25_b"]) <= 5,
        sd_test_pass=lambda x: abs(1 - (x["pm25_a"] / x["pm25_b"])) <= 0.56,
        reliable=lambda x: (x.abs_test_pass & x.sd_test_pass),
    )
    all_sensor_data["mean_pm25"] = all_sensor_data[["pm25_a", "pm25_b"]].apply(
        lambda x: x.mean(), axis=1
    )
    # Write out CSV
    all_sensor_data.to_csv("data/PurpleAir/all_sensors.csv", index=False)

    # Filtering to reliable data only
    reliable_sensor_data = all_sensor_data[all_sensor_data["reliable"]].copy()

    # Daily averages for Tahoe region
    daily_average_pm25 = (
        reliable_sensor_data.groupby("time_stamp")
        .mean()["mean_pm25"]
        .round(2)
        .rename("daily_mean_25pm")
    )
    daily_obs_count = (
        reliable_sensor_data.groupby("time_stamp").count()["mean_pm25"].rename("daily_sensor_count")
    )
    daily_sensor_data = pd.concat([daily_average_pm25, daily_obs_count], axis=1).reset_index()
    daily_sensor_data.to_csv("data/PurpleAir/daily_averaged_values.csv", index=False)

    return daily_sensor_data
