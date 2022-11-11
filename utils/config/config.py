import os
import yaml


class ServerConfig:
    def __init__(self):
        config_file = {}

        with open("config.yml", "r") as stream:
            try:
                config_file = yaml.safe_load(stream)
            except Exception as e:
                print(e)

        config = config_file

        server_name_override = os.environ.get("VALHALLA_SERVER_NAME")
        server_port_override = os.environ.get("VALHALLA_SERVER_PORT")
        server_host_override = os.environ.get("VALHALLA_SERVER_HOST")
        server_password_override = os.environ.get("VALHALLA_SERVER_PASSWORD")
        server_access_username_override = os.environ.get(
            "VALHALLA_SERVER_ACCESS_USERNAME")
        database_file_override = os.environ.get("VALHALLA_DATABASE_FILE")
        server_logging_override = os.environ.get("VALHALLA_LOGLEVEL")

        if server_name_override:
            config["server_name"] = server_name_override

        if server_port_override:
            config["server_port"] = server_port_override

        if server_host_override:
            config["server_host"] = server_host_override

        if database_file_override:
            config["database_file"] = database_file_override

        if server_password_override:
            config["server_password"] = server_password_override

        if server_access_username_override:
            config["server_access_username"] = server_access_username_override

        if server_logging_override:
            config["server_loglevel"] = server_logging_override

        self.server_name = config["server_name"]
        self.server_port = config["server_port"]
        self.database_file = config["database_file"]
        self.server_host = config["server_host"]
        self.server_password = config["server_password"]
        self.server_access_username = config["server_access_username"]
        self.server_loglevel = config["server_loglevel"]
