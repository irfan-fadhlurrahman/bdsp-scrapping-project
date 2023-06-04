import os
import time
import dill

import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# See src/indicator.py
from indicator import *

INDICATOR_VALUES_FILEPATH = "data/indicator_input_dict.bin"


def read_binary_file(path):
    with open(path, "rb") as f:
        return dill.load(f)


def get_indicator_input_values(path):
    if os.path.exists(path):
        print("Read from existing local file")
        return read_binary_file(path)
    else:
        print("Scrapping begins.......")
        return extract_all_indicator_values()


def convert_input_as_index(indicator_dict, input_dict):
    """
    NOTE: Remember that XPATH index for this case start from 2
    """
    input_with_index = {}

    # Independent input: subsektor, level, provinsi, tahunAwal, tahunAkhir
    for indicator_id in ["subsektor", "level", "tahunAwal", "tahunAkhir"]:
        if isinstance(indicator_dict.get(indicator_id), list):
            for idx, indicator in enumerate(indicator_dict.get(indicator_id)):
                if input_dict[indicator_id] == indicator:
                    input_with_index.update({indicator_id: {indicator: idx + 2}})

    # Dependent input: provinsi
    if input_dict["level"] == "Provinsi":
        for idx, indicator in enumerate(indicator_dict.get("prov")):
            if input_dict["prov"] == indicator:
                input_with_index.update({"prov": {indicator: idx + 2}})

    # Dependent input: kabupaten
    if input_dict["level"] == "Kabupaten":
        for idx, indicator in enumerate(indicator_dict.get("prov")):
            if input_dict["prov"] == indicator:
                input_with_index.update({"prov": {indicator: idx + 2}})

        for idx, indicator in enumerate(indicator_dict["kab"].get(input_dict["prov"])):
            if input_dict["kab"] == indicator:
                input_with_index.update({"kab": {indicator: idx + 2}})

    # Dependent input: komoditas
    for idx, indicator in enumerate(
        indicator_dict["komoditas"].get(input_dict["subsektor"])
    ):
        if input_dict["komoditas"] == indicator:
            input_with_index.update({"komoditas": {indicator: idx + 2}})

    return input_with_index


def extract(indicator_dict, input_with_idx):
    # Scrap a table from input starts here
    driver = get_driver(driver_path=CHROMEDRIVER_PATH, url=URL)

    # Fill all inputs
    for indicator_id in list(input_with_idx.keys()):
        for indicator_name, indicator_idx in input_with_idx[indicator_id].items():
            print(indicator_name, indicator_idx)
            indicator = find_indicator_name(
                driver, indicator_id=indicator_id, indicator_idx=indicator_idx
            )
            indicator.click()
            time.sleep(5)

    # Click 'search' button
    search_button = driver.find_element(By.XPATH, '//*[@id="search"]')
    search_button.click()

    # wait for the table to load
    table_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
    )
    print(table_element.text)
    time.sleep(10)

    # Get table headers
    header_elements = table_element.find_elements(By.TAG_NAME, "thead")
    headers = [header.text.split(" ") for header in header_elements][0]
    print(headers)

    # Get table contents
    data = []
    row_elements = table_element.find_elements(By.TAG_NAME, "tr")
    for row in row_elements[1:]:
        cell_elements = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text.strip() for cell in cell_elements]
        data.append(row_data)

    for row in data:
        print(row)

    # Do not forget to quit the driver
    driver.quit()

    return {"headers": headers, "content": data}


if __name__ == "__main__":
    extract()
