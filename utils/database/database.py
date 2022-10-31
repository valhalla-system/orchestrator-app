from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.models import Client, VMImage
class Database:
    def __init__(self, database_file: str):
        try:
            # Connect to the database using SQLAlchemy
            engine = create_engine(f"sqlite:///{database_file}")
            Session = sessionmaker()
            Session.configure(bind=engine)
            self.session = Session()
        except Exception as ex:
            print(ex)
            exit(-1)
    
    def get_clients(self) -> list(Client):
        result = None
        try:
            result = self.session.query(Client).all()
        except Exception as ex:
            print(f"Error getting list of clients from database: {ex}")
            result = None
        return result
    
    def get_client_by_mac_address(mac_address: str) -> Client:
        result = None
        