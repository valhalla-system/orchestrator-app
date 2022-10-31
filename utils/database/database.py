from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.models import Client, VMImage
import logging


class Database:
    def __init__(self, database_file: str, logging_level: str):
        try:
            # Connect to the database using SQLAlchemy
            engine = create_engine(f"sqlite:///{database_file}")
            Session = sessionmaker()
            Session.configure(bind=engine)
            self.session = Session()
            # create logger using data from config file
            self.logger = logging.getLogger(__name__)
            log_level_mapping_dict = {
                "NOTSET": 0,
                "DEBUG": 10,
                "INFO": 20,
                "WARNING": 30,
                "ERROR": 40,
                "CRITICAL": 50
            }
            self.logger.setLevel(log_level_mapping_dict[logging_level])
        except Exception as ex:
            print(ex)
            exit(-1)

    def get_clients(self) -> list(Client):
        result = None
        try:
            with self.session.begin():
                result = self.session.query(Client).all()
        except Exception as ex:
            self.logger.error(
                f"Error getting list of clients from database: {ex}")
            result = None
        return result

    def get_client_by_mac_address(self, mac_address: str) -> Client:
        result = None
        try:
            with self.session.begin():
                result = self.session.query(
                    Client, mac_address=mac_address).first()
        except Exception as ex:
            self.logger.error(f"Error getting client by mac address: {ex}")
        return result

    def get_clients_by_client_version(self, client_version: str) -> list(Client):
        result = None
