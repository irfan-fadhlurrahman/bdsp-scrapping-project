import os
import time

import dill

import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HOME_PATH = os.path.expanduser("~")
CHROMEDRIVER_PATH = f"{HOME_PATH}/web-scraping/chromedriver"

URL = "https://bdsp2.pertanian.go.id/bdsp/id/indikator"

INDICATOR_ID_LIST = [
    "subsektor",
    "komoditas",
    "level",
    "prov",
    "kab",
    "tahunAwal",
    "tahunAkhir",
]


def get_driver(driver_path, url):
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    return driver


def find_indicator_name(driver, indicator_id, indicator_idx):
    indicator = driver.find_element(
        By.XPATH, f'//*[@id="{indicator_id}"]/option[{indicator_idx}]'
    )
    return indicator


def get_all_indicator_values(driver, indicator_id):
    indicator_list = []
    select_elements = driver.find_elements(By.ID, indicator_id)

    for select in select_elements:
        option_elements = select.find_elements(By.TAG_NAME, "option")
        for idx, option in enumerate(option_elements[1:]):
            indicator_list.append(option.text)

    return indicator_list


def extract_indicator_values(driver, indicator_id="subsektor", indicator_idx=2):
    indicator = find_indicator_name(
        driver, indicator_id=indicator_id, indicator_idx=indicator_idx
    )
    indicator.click()
    time.sleep(2)

    print(indicator.text)
    return get_all_indicator_values(driver, indicator_id)


def extract_values_that_dependent(
    driver, depends_on_list, indicator_id="komoditas", indicator_idx=1
):
    if depends_on_list:
        return extract_indicator_values(
            driver, indicator_id=indicator_id, indicator_idx=indicator_idx
        )


def extract_all_indicator_values():
    driver = get_driver(driver_path=CHROMEDRIVER_PATH, url=URL)

    # Empty dict to store all values
    indicator_dict = {}

    # Extract all independent indicator values
    for indicator_id in ["subsektor", "level", "tahunAwal", "tahunAkhir"]:
        dict_values = {
            indicator_id: extract_indicator_values(driver, indicator_id=indicator_id)
        }

        indicator_dict.update(dict_values)
        print(dict_values)

    # Extract komoditi
    komoditas_dict = {}
    for idx, subsektor in enumerate(indicator_dict["subsektor"]):
        # Trigger to make the html element of targeted indicator out
        subsektor_list = extract_indicator_values(
            driver, indicator_id="subsektor", indicator_idx=idx + 2
        )
        komoditas_list = extract_indicator_values(driver, indicator_id="komoditas")
        komoditas_dict.update({subsektor: komoditas_list})
        time.sleep(10)

    indicator_dict.update({"komoditas": komoditas_dict})
    print(komoditas_dict)

    # Extract provinsi
    provinsi_dict = {}
    for idx, level in enumerate(indicator_dict["level"]):
        current_level = find_indicator_name(
            driver, indicator_id="level", indicator_idx=idx + 2
        )
        if current_level.text != "Provinsi":
            continue
        else:
            # Trigger to make the html element of targeted indicator out
            level_list = extract_indicator_values(
                driver, indicator_id="level", indicator_idx=idx + 2
            )
            provinsi_list = extract_indicator_values(driver, indicator_id="prov")
            time.sleep(20)

    indicator_dict.update({"prov": provinsi_list})
    print(provinsi_dict)

    # Extract Kabupaten
    kabupaten_dict = {}
    for level in indicator_dict["level"]:
        if level != "Kabupaten":
            continue
        else:
            for idx, provinsi in enumerate(indicator_dict["prov"]):
                # Trigger to make the html element of targeted indicator out
                level_list = extract_indicator_values(
                    driver, indicator_id="level", indicator_idx=4
                )
                provinsi_list = extract_indicator_values(
                    driver, indicator_id="prov", indicator_idx=idx + 2
                )
                kabupaten_list = extract_indicator_values(driver, indicator_id="kab")
                kabupaten_dict.update({provinsi: kabupaten_list})
                time.sleep(20)

                # TEMP: to avoid internal server error
                # break

    indicator_dict.update({"kab": kabupaten_dict})
    print(indicator_dict)

    driver.quit()

    # Save as binary files
    with open("data/indicator_input_dict.bin", "wb") as f:
        dill.dump(indicator_dict, f)

    return indicator_dict


if __name__ == "__main__":
    extract_all_indicator_values()
