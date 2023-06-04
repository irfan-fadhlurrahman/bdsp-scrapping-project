import time

from utils import Config

from typing import List, Dict

from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


class WebPageLoader:
    def __init__(self):
        self.driver = None
        self.sleep_range = Config().get_time_range(3.0, 5.0)

    def load_page(self, url: str) -> None:
        self.set_driver()
        self.driver.get(url)
        time.sleep(self.sleep_range)

    def set_driver(self, service: Service = None, options: ChromeOptions = None) -> None:
        if service is None:
            service = self.set_service()

        if options is None:
            options = self.set_options()

        self.driver = Chrome(service=service, options=options)

    def set_service(self) -> Service:
        return Service(executable_path=ChromeDriverManager().install())

    def set_options(self, options_args: List = ["--headless"]) -> ChromeOptions:
        """
        example of the argument:
        options_args = ["--headless", "--no-sandbox"]
        """
        options = ChromeOptions()
        if options_args:
            for option in options_args:
                options.add_argument(option)

        return options


class IndicatorExtractor:
    def __init__(self, driver: Chrome, indicator_id_list: List):
        self.driver = driver
        self.indicator_id_list = indicator_id_list
        self.sleep_range = Config().get_time_range(3.0, 5.0)

    def find(self, indicator_id: str, indicator_idx: int) -> WebElement:
        try:
            return self.driver.find_element(
                By.XPATH, f'//*[@id="{indicator_id}"]/option[{indicator_idx}]'
            )
        except Exception as e:
            print(e)
            print(f"{indicator_id}: Wrong element. Please reconfigure.")

    def trigger(self):
        for indicator_id in self.indicator_id_list:
            if indicator_id not in ["komoditas", "kab"]:
                self.find(indicator_id, 3).click()
                time.sleep(self.sleep_range)
                
    def get_values(self, indicator_id: str) -> List:
        select_elements = self.driver.find_elements(By.ID, indicator_id)
        time.sleep(self.sleep_range)

        indicator_value_list = []
        for select in select_elements:
            option_elements = select.find_elements(By.TAG_NAME, "option")

            for idx, option in enumerate(option_elements[1:]):
                indicator_value_list.append(option.text)

        return indicator_value_list