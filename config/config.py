import configparser
from pathlib import Path


class Config:

    def __init__(self):

        self.config = configparser.ConfigParser()

        config_file = Path(__file__).parent / "Extraction.properties"

        print(config_file)
        print(config_file.exists())

        self.config.read(config_file)

    @property
    def database(self):
        return self.config["DATABASE"]["NAME"]

    @property
    def bronze_schema(self):
        return self.config["SCHEMA"]["BRONZE"]

    @property
    def silver_schema(self):
        return self.config["SCHEMA"]["SILVER"]

    @property
    def gold_schema(self):
        return self.config["SCHEMA"]["GOLD"]

    @property
    def incoming_folder(self):
        return self.config["PATH"]["INCOMING"]

    @property
    def archive_folder(self):
        return self.config["PATH"]["ARCHIVE"]

    @property
    def error_folder(self):
        return self.config["PATH"]["ERROR"]

    @property
    def log_level(self):
        return self.config["LOGGING"]["LEVEL"]

    @property
    def log_level(self):
        return self.config["LOGGING"]["LEVEL"]

    @property
    def log_path(self):
        return self.config["LOGGING"]["PATH"]

    @property
    def source_raw_table(self):
        return self.config["TABLE"]["SOURCE_RAW"]
    
config = Config()