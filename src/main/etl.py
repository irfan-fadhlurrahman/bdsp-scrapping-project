import os
import re
import glob
import time
import pprint

from utils import FileHandler, BinaryFileHandler, MongoDBDatabase
from scraper import WebPageLoader, IndicatorExtractor

from typing import List, Dict

from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement


INDICATOR_ID_LIST = [
    "subsektor",
    "komoditas",
    "level",
    "prov",
    "kab",
    "tahunAwal",
    "tahunAkhir",
]

class WebPageToLocalHTMLFilesPipeline:
    
    def __init__(self):
        self.indicator_id_list = INDICATOR_ID_LIST
    
    def initialize(self, url: str):
        self.url = url
        self.page_loader = WebPageLoader()
        self.page_loader.load_page(self.url)
        
        self.indicator_input = IndicatorExtractor(
            self.page_loader.driver, 
            self.indicator_id_list
        )
        
    def quit(self):
        self.page_loader.driver.quit()
           
    def extract(self) -> None:
        # Trigger the html page so hidden elements are opened
        self.indicator_input.trigger()
        
        # Save the page source
        file_handler = FileHandler("web-scraping/data/page_source/all")
        file_handler.save(
            self.page_loader.driver.page_source, 
            "page_source_all.html"
        )
        
        # Get Subsector and Province
        subsector_list = self.indicator_input.get_values("subsektor")
        province_list = self.indicator_input.get_values("prov")
        
        # Get Commodities
        for idx, subsector in enumerate(subsector_list):
            self.indicator_input.find("subsektor", idx + 2).click()
            time.sleep(self.indicator_input.sleep_range)
            self.indicator_input.find("komoditas", 3).click()
            time.sleep(self.indicator_input.sleep_range)

            subsector = subsector.replace(" ", "_").lower()
            file_handler = FileHandler("web-scraping/data/page_source/commodities")
            file_handler.save(self.page_loader.driver.page_source, f"{idx:02}_{subsector}.html")
            print(idx, subsector, "done")
        
        # Get Regency
        for idx, province in enumerate(province_list):
            self.indicator_input.find("level", 4).click()
            time.sleep(self.indicator_input.sleep_range)
            self.indicator_input.find("prov", idx + 2).click()
            time.sleep(self.indicator_input.sleep_range)
            self.indicator_input.find("kab", 3).click()
            time.sleep(self.indicator_input.sleep_range)

            province = province.replace(" ", "_").lower()
            file_handler = FileHandler("web-scraping/data/page_source/regency")
            file_handler.save(self.page_loader.driver.page_source, f"{idx:02}_{province}.html")
            print(idx, province, "done")
        
    def transform(self) -> None:
        pass
    
    def load(self) -> None:
        pass

class LocalHTMLToMongoDBPipeline:
    
    def __init__(self):
        self.indicator_id_list = INDICATOR_ID_LIST
        self.indicator_dict = {}
        self.reference_dict = {
            "all": ["subsektor", "level", "prov", "tahunAwal", "tahunAkhir"],
            "commodities": ["komoditas"],
            "regency": ["kab"]
        }
    
    def initialize(self, url: str):
        self.url = url
        self.page_loader = WebPageLoader()
        self.page_loader.load_page(self.url)
        
        self.indicator_input = IndicatorExtractor(
            self.page_loader.driver, 
            self.indicator_id_list
        )
        
    def quit(self):
        self.page_loader.driver.quit()
        
    def extract(self, indicator: str) -> None:
        if indicator not in list(self.reference_dict.keys()):
            print("Folder does not exist")
            return None
        
        abs_path = os.path.abspath(f"data/page_source/{indicator}/*.html")
        
        tmp_dict = {}
        for idx, page_source_path in enumerate(glob.glob(abs_path)):
            
            print(page_source_path)
            
            self.initialize(url=f"file:///{page_source_path}")
            for name in self.reference_dict[indicator]:
                result_list = self.indicator_input.get_values(name)
                
                if indicator == "all":
                    self.indicator_dict.update({name: result_list})
                
                else:
                    dict_key = self.__clean(page_source_path)
                    tmp_dict.update({dict_key: result_list})
                    
        if tmp_dict:
            self.indicator_dict.update({indicator: tmp_dict})
        
    def transform(self):
        pass
    
    def load(self):
        pass
    
    def __clean(self, path: str) -> str:
        """
        i.e.
        path = "/home/irfanfadh43/web-scraping/data/page_source/regency/10_daerah_khusus_ibukota_jakarta"
        output: Daerah Khusus Ibukota Jakarta
        """
        path_list = re.split(r"\d{1,}\_", path)
        path_list = re.sub(r".html", "", path_list[-1])
        path_list = re.split(r"_", path_list)
        
        path_list = [loc.capitalize() for loc in path_list]
        return " ".join(path_list)
        

def main():
    # 1. Get a HTML elements snapshot and save it locally
    if not glob.glob("data/page_source/**/*.html"):
        print("Yes")
        # pipeline = WebPageToLocalHTMLFilesPipeline()
        # pipeline.initialize(url="https://bdsp2.pertanian.go.id/bdsp/id/indikator")
        # pipeline.extract()
        # pipeline.quit()
    
    # 2. Extract all values of indicators from local HTML files
    file_handler = BinaryFileHandler("web-scraping/data/binary")
    if not os.path.exists(f"{file_handler.abs_path}/indicator_input_values.bin"):
        print("Yes")
        # pipeline = LocalHTMLToMongoDBPipeline() 
        
        # for html_folder in ["all", "commodities", "regency"]:
        #     pipeline.extract(html_folder)
    
        # print(pipeline.indicator_dict)
    
        # # 3. Save the results as binary
        # file_handler.save(pipeline.indicator_dict, "indicator_input_values.bin")
        
        # try:
        #     pipeline.quit()
        # except AttributeError:
        #     print("There is no active driver")
    
    # 4. Read the scrapped result
    indicator_dict = file_handler.load("indicator_input_values.bin")
    # print(indicator_dict)
        
    # TEMP: 5. Load indicator input data to MongoDB
    mongo_db = MongoDBDatabase(
        "mongodb://localhost:27017",
        username="root",
        password="rootpassword"
    )
    mongo_db.connect()
    mongo_db.create_database("bdsp")
    
    for indicator in ["subsektor", "level", "tahunAwal", "tahunAkhir"]:
        mongo_db.create_collection(indicator)
        
        for idx, name in enumerate(indicator_dict[indicator]):            
            if indicator in ["tahunAwal", "tahunAkhir"]:
                doc = {
                    f"{indicator}_idx": idx,
                    f"{indicator}_name": int(name)
                }
            else:
                doc = {
                    f"{indicator}_idx": idx,
                    f"{indicator}_name": name
                }
            mongo_db.insert_document(doc)
    
    ## Komoditas
    indicator = "komoditas"
    mongo_db.create_collection(indicator)
    
    for subsector, commodity_list in indicator_dict["commodities"].items():
        for idx, commodity in enumerate(commodity_list):
            doc = {
                "subsektor_name": subsector,
                "komoditas_idx": idx,
                "komoditas_name": commodity
            }
            mongo_db.insert_document(doc)
    
    ## Provinsi
    indicator = "prov"
    mongo_db.create_collection(indicator)
    
    for idx, prov in enumerate(indicator_dict["prov"]):
        doc = {
            "level_name": "Provinsi",
            "prov_idx": idx,
            "prov_name": prov
        }
        mongo_db.insert_document(doc)
        
    ## Kabupaten
    indicator = "kab"
    mongo_db.create_collection(indicator)
    
    for province, regency_list in indicator_dict["regency"].items():
        for idx, regency in enumerate(regency_list):
            doc = {
                "level_name": "Kabupaten",
                "prov_name": province,
                "kab_idx": idx,
                "kab_name": regency    
            }
            mongo_db.insert_document(doc)

    for name in mongo_db.db.list_collection_names():
        print(name)
        pprint.pprint(mongo_db.db[name].count_documents({}))
        
    # Input validation
    def validate(input_dict: Dict, indicator: str) -> Dict:
        searched = mongo_db.db[indicator].find_one(
            {f"{indicator}_name": input_dict[indicator]}
        )
        if not searched:
            print(f"{indicator} Not found")
            return None
        
        idx = searched[f"{indicator}_idx"]
        return {indicator: idx}

    def validate_all(input_dict: Dict) -> Dict:
        input_idx = {}
        for indicator in input_dict.keys():
            idx_dict = validate(input_dict, indicator)
            if isinstance(idx_dict, dict):
                input_idx.update(idx_dict)  
                
        return input_idx

    # Input for a table scrapping
    input_dict = {
        "subsektor": "Tanaman Pangan",
        "komoditas": "JAGUNG",
        "level": "Kabupaten",
        "prov": "Aceh",
        "kab": "Kab. Simeulue",
        "tahunAwal": 1970,
        "tahunAkhir": 2023,
    }
    print(input_dict)
    print(validate_all(input_dict))
    
    # TEMP: drop all database
    try:
        for name in mongo_db.db.list_collection_names():
            mongo_db.db[name].drop()
    except:
        pass
    
if __name__ == "__main__":
    main()