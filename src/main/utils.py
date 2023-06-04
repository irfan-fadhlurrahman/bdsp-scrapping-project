import random
import time
import os
import dill

import pymongo
from pymongo import MongoClient

from typing import Dict

class MongoDBDatabase:
    
    def __init__(self, uri: str, username: str, password: str):
        self.uri = uri
        self.username = username
        self.password = password
    
    def connect(self) -> None:
        self.client = MongoClient(
            self.uri,
            username=self.username,
            password=self.password
        )
    
    def create_database(self, db_name: str):
        self.db = self.client[db_name]
    
    def create_collection(self, collection_name: str) -> None:
        self.collection = self.db[collection_name]
    
    def drop_collection(self) -> None:
        self.collection.drop()
        
    def insert_document(self, document: Dict) -> None:
        if not self.collection.find_one(document):
            self.collection.insert_one(document).inserted_id

class Config:
    def __init__(self):
        pass

    def get_time_range(self, start: float, end: float) -> random.uniform:
        return random.uniform(start, end)


class FileHandler:
    def __init__(self, folder_path: str):
        self.root_path = os.path.expanduser("~")
        self.folder_path = folder_path
        self.create_folder_if_not_exist()

    def create_folder_if_not_exist(self) -> None:
        abs_path = f"{self.root_path}/{self.folder_path}"
        if not os.path.exists(abs_path):
            os.system(f"mkdir -p {abs_path}")

        self.abs_path = abs_path

    def save(self, text_to_save: Dict, filename: str) -> None:
        with open(f"{self.abs_path}/{filename}", "w") as f:
            f.write(text_to_save)

    def load(self, filename: str):
        with open(f"{self.abs_path}/{filename}", "r") as f:
            return f.read()


class BinaryFileHandler:
    def __init__(self, folder_path: str):
        self.root_path = os.path.expanduser("~")
        self.folder_path = folder_path
        self.create_folder_if_not_exist()

    def create_folder_if_not_exist(self) -> None:
        abs_path = f"{self.root_path}/{self.folder_path}"
        if not os.path.exists(abs_path):
            os.system(f"mkdir -p {abs_path}")

        self.abs_path = abs_path

    def save(self, dict_to_save: Dict, filename: str) -> None:
        with open(f"{self.abs_path}/{filename}", "wb") as f:
            dill.dump(dict_to_save, f)

    def load(self, filename: str):
        with open(f"{self.abs_path}/{filename}", "rb") as f:
            return dill.load(f)
