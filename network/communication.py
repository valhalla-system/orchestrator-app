from http.client import NON_AUTHORITATIVE_INFORMATION
from flask import Flask
from utils.config import ServerConfig
import sqlite3

class Server():

    def __init__(self, host, port, name, access_password, version, database_file):
        self.app = Flask(self.name)
        self.host = host
        self.port = port
        self.name = name
        self.access_password = access_password
        self.version = version
        self.client_database = sqlite3.connect(database_file)

    @app.route("/")
    def basic_server_data(self):
        return {"server_name": self.name, "server_version": self.version, "host": self.host}

    @app.route("/client/register")
    def register_new_client_to_database(self):
        # TODO: implement
        pass
