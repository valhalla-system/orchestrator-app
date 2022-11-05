from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.models.models import Client, VMImage
from utils.exceptions.DatabaseException import DatabaseException
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

    def get_clients(self) -> list[Client]:
        result = []
        try:
            with self.session.begin():
                result = self.session.query(Client).all()
        except Exception as ex:
            self.logger.error(
                f"Error getting list of clients from database: {ex}")
            result = []
        return result

    def get_client_by_mac_address(self, mac_address: str) -> Client:
        result = None
        try:
            with self.session.begin():
                result = self.session.query(
                    Client, mac_address=mac_address).first()
        except Exception as ex:
            self.logger.warn(f"Error getting client by mac address: {ex}")
        return result

    def get_clients_by_client_version(self, client_version: str) -> list[Client]:
        result = []
        try:
            with self.session.begin():
                result = self.session.query(
                    Client, client_version=client_version).all()
        except Exception as ex:
            self.logger.warn(
                f"Error getting client list by software version: {ex}")
        return result

    def get_clients_by_vm_image(self, vm_image: VMImage) -> list[Client]:
        result = []
        try:
            clients_list = self.get_clients()
            for client in clients_list:
                if client.has_vm_installed(vm_image.image_hash):
                    result.append()
        except Exception as ex:
            self.logger.warn(
                f"Error getting list of clients with VM installed: {ex}")
            result = []
        return result

    def add_client(self, client: Client):
        try:
            with self.session.begin():
                self.session.add(client)
                self.session.flush()
                self.session.commit()
        except Exception as ex:
            self.logger.error(f"Error adding entity to database: {ex}")
            raise DatabaseException("Error adding entity to database")

    def modify_client(self, client: Client) -> Client:
        try:
            old_object = self.get_client_by_mac_address(client.mac_address)
            with self.session.begin():
                old_object = client
                self.session.merge(old_object)
                self.session.flush()
                self.session.commit()
                return old_object
        except Exception as ex:
            self.logger.error(f"Error modifying object in the database: {ex}")
            raise DatabaseException("Error modifying entity in database")

    def delete_client(self, client: Client):
        try:
            with self.session.begin():
                self.session.delete(client)
        except Exception as ex:
            self.logger.error(f"Error deleting client from database: {ex}")
