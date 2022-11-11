from http.client import NON_AUTHORITATIVE_INFORMATION
from flask import Flask
from utils.database.database import Database
from utils.exceptions import DatabaseException


class FlaskAppWrapper(object):

    def __init__(self, app, **configs):
        self.app = app
        self.configs(**configs)

    def configs(self, **configs):
        for config, value in configs:
            self.app.config[config.upper()] = value

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name,
                              handler, methods=methods, *args, **kwargs)

    def run(self, **kwargs):
        self.app.run(**kwargs)


class Server():

    def __init__(self, host: str, port: int, name: str, access_password: str, access_username: str, version: str, database_file_path: str, logging_level: str, ):
        self.host = host
        self.port = port
        self.name = name
        self.access_password = access_password
        self.access_username = access_username
        self.version = version
        self.database = Database(
            database_file=database_file_path, logging_level=logging_level)
        self.flask_app = Flask(name)
        self.app = FlaskAppWrapper(self.flask_app)

    def basic_server_data(self):
        return {"server_name": self.name, "server_version": self.version, "host": self.host}

    def register_new_client_to_database(self):
        # TODO: implement
        self.database

    def run(self):
        self.app.add_endpoint(endpoint="/", endpoint_name="server_data",
                              handler=self.basic_server_data, methods=["GET"])
        # TODO: add rest of endpoints
        self.app.run()
