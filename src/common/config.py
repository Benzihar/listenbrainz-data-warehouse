import configparser
from pathlib import Path

class Config:

    def __init__(self):

        self.config = configparser.ConfigParser()

        config_file = Path(__file__).parents[2] / "config"/ "Extraction.properties"

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
    def audit_schema(self):
        return self.config["SCHEMA"]["AUDIT"]

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
    def log_path(self):
        return self.config["LOGGING"]["PATH"]

    @property
    def source_raw_table(self):
        return self.config["BRZ_TABLE"]["SOURCE_RAW"]

    @property
    def archive_raw_table(self):
        return self.config["BRZ_TABLE"]["ARCHIVE_RAW"]

    @property
    def dim_user_table(self):
        return self.config["SIL_TABLE"]["DIM_USER"]

    @property
    def dim_artist_table(self):
        return self.config["SIL_TABLE"]["DIM_ARTIST"]

    @property
    def dim_release_table(self):
        return self.config["SIL_TABLE"]["DIM_RELEASE"]

    @property
    def dim_recording_table(self):
        return self.config["SIL_TABLE"]["DIM_RECORDING"]

    @property
    def fact_listen_table(self):
        return self.config["GLD_TABLE"]["FACT_LISTEN"]

    @property
    def etl_file_audit_table(self):
        return self.config["AUD_TABLE"]["ETL_FILE_AUDIT"]

    @property
    def etl_object_audit_table(self):
        return self.config["AUD_TABLE"]["ETL_OBJECT_AUDIT"]
    
config = Config()