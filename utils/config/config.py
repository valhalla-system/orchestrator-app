import os
import yaml

class ServerConfig:    
    def __init__(self):
        config_file = {}

        with open("~/.config/orchestrator/config.yml", "r") as stream:
            try:
                config_file = yaml.safe_load(stream)
            except Exception as e:
                print(e)

        config = config_file

        server_name_override = os.environ.get("VALHALLA_SERVER_NAME")
        server_port_override = os.environ.get("VALHALLA_SERVER_PORT")
        database_file_override = os.environ.get("VALHALLA_DATABASE_FILE")

        if server_name_override:
            config["server_name"] = server_name_override
    
        if server_port_override:
            config["server_port"] = server_port_override
        
        if database_file_override:
            config["database_file"] = database_file_override

        self.server_name = config["server_name"]
        self.server_port = config["server_port"]
        self.database_file = config["database_file"]
        