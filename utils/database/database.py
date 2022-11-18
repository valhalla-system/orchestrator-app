from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils.models.models import Client, VMImage, User, Base
from utils.exceptions.DatabaseException import DatabaseException
import logging


class Database:
    def __init__(self, database_file: str, logging_level: str):
        try:
            # Connect to the database using SQLAlchemy
            engine = create_engine(f"sqlite:///{database_file}")
            self.Session = sessionmaker()
            self.Session.configure(bind=engine, expire_on_commit=False)
            self.base = Base
            self.base.metadata.create_all(bind=engine)
            # session = self.Session()
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
            session = self.Session()
            with session.begin():
                result = session.query(Client).all()
        except Exception as ex:
            self.logger.error(
                f"Error getting list of clients from database: {ex}")
            result = []
        return result

    def get_client_by_mac_address(self, mac_address: str) -> Client:
        result = None
        session = self.Session()
        try:
            with session.begin():
                result = session.query(
                    Client, mac_address=mac_address).first()
        except Exception as ex:
            self.logger.warn(f"Error getting client by mac address: {ex}")
        return result

    def get_clients_by_client_version(self, client_version: str) -> list[Client]:
        result = []
        try:
            session = self.Session()
            with session.begin():
                result = session.query(
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
            session = self.Session()
            with session.begin():
                session.add(client)
                session.flush()
                session.commit()
        except Exception as ex:
            self.logger.error(f"Error adding entity to database: {ex}")
            raise DatabaseException("Error adding entity to database")

    def modify_client(self, client: Client) -> Client:
        try:
            old_object = self.get_client_by_mac_address(client.mac_address)
            session = self.Session()
            with session.begin():
                old_object = client
                session.merge(old_object)
                session.flush()
                session.commit()
                return old_object
        except Exception as ex:
            self.logger.error(f"Error modifying object in the database: {ex}")
            raise DatabaseException("Error modifying entity in database")

    def delete_client(self, client: Client):
        try:
            session = self.Session()
            with session.begin():
                session.delete(client)
        except Exception as ex:
            self.logger.error(f"Error deleting client from database: {ex}")

    def get_image_by_id(self, image_id: int) -> VMImage:
        try:
            session = self.Session()
            with session.begin():
                response = session.query(
                    VMImage, image_id=image_id).first()
                return response
        except Exception as ex:
            self.logger.error(f"Error getting image data from database: {ex}")

    def get_images(self) -> list[VMImage]:
        try:
            session = self.Session()
            with session.begin():
                response = session.query(VMImage).all()
                return response
        except Exception as ex:
            self.logger.error(
                f"Error getting list of images from database: {ex}")

    def get_image_by_name(self, image_name: str) -> list[VMImage]:
        try:
            session = self.Session()
            with session.begin():
                response = session.query(
                    VMImage, image_name=image_name).all()
                return response
        except Exception as ex:
            self.logger.error(
                f"Error getting list of images from database: {ex}")

    def get_image_by_hash(self, image_hash: str) -> list[VMImage]:
        try:
            session = self.Session()
            with session.begin():
                response = session.query(VMImage, image_hash=image_hash)
                return response
        except Exception as ex:
            self.logger.error(
                f"Error getting list of images with specified hash: {ex}")

    def add_image(self, image: VMImage):
        try:
            session = self.Session()
            with session.begin():
                session.add(image)
                session.flush()
                session.commit()
        except Exception as ex:
            self.logger.error(f"Couldn't save client data do database: {ex}")
            raise DatabaseException(f"Couldn't add image to database: {ex}")

    def modify_image(self, new_image_object: VMImage) -> VMImage:
        try:
            old_object = self.get_image_by_id(new_image_object.image_id)
            session = self.Session()
            with session.begin():
                old_object = new_image_object
                session.merge(old_object)
                session.flush()
                session.commit()
                return old_object
        except Exception as ex:
            self.logger.error(f"Couldn't modify object in database: {ex}")
            raise DatabaseException(
                f"Couldn't modify object in database: {ex}")

    def add_user(self, new_user: User):
        try:
            session = self.Session()
            with session.begin():
                session.add(new_user)
                session.flush()
                session.commit()
        except Exception as ex:
            self.logger.error(f"Couldn't add user to the database: {ex}")
            raise DatabaseException(f"Couldn't add user to the database: {ex}")

    def get_user_by_id(self, user_id: int) -> User:
        try:
            session = self.Session()
            with session.begin():
                user = session.query(User).filter(
                    User.user_id == user_id).first()
                return user
        except Exception as ex:
            self.logger.error(f"Error getting data from database: {ex}")
            raise DatabaseException(f"Error getting data from database: {ex}")

    def get_user_by_name(self, username: str) -> User:
        try:
            session = self.Session()
            with session.begin():
                user = session.query(User).filter(
                    User.username == username).first()
                return user
        except Exception as ex:
            self.logger.error(f"Error getting data from database: {ex}")
            raise DatabaseException(f"Error getting data from database: {ex}")
