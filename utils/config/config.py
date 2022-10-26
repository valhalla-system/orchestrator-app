import os
import yaml

class ServerConfig:
    config_file = {}

    with open("~/.config/orchestrator/config.yml", "r") as stream:
        try:
            config_file = yaml.safe_load(stream)
        except Exception as e:
            print(e)

    config = config_file

    server_name_override = os.environ.get("VALHALLA_SERVER_NAME")
    server_port_override = os.environ.get("VALHALLA_SERVER_PORT")
