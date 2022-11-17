from http.client import NON_AUTHORITATIVE_INFORMATION
from flask import Flask, request, jsonify
from utils.database.database import Database
from utils.exceptions import DatabaseException
from utils.models.models import Client, VMImage, User
from utils.middleware.auth import require_auth
import json
import bcrypt
import jwt


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

    def __init__(self, host: str, port: int, name: str, access_password: str, access_username: str, jwt_secret: str, version: str, database_file_path: str, logging_level: str, ):
        self.host = host
        self.port = port
        self.name = name
        self.access_password = access_password
        self.access_username = access_username
        self.version = version
        self.database = Database(
            database_file=database_file_path, logging_level=logging_level)
        self.flask_app = Flask(name)
        self.flask_app.config['SECRET_KEY'] = jwt_secret
        self.flask_app.config['DATABASE_FILE_PATH'] = database_file_path
        self.flask_app.config['LOGGING_LEVEL'] = logging_level
        self.app = FlaskAppWrapper(self.flask_app)

    def basic_server_data(self):
        return {"server_name": self.name, "server_version": self.version, "host": self.host}

    def login(self):
        try:
            request_data = request.json
            if not request_data:
                return {
                    "message": "Please provide login info",
                    "data": None,
                    "error": "Bad request"
                }, 400

            current_user = self.database.get_user_by_name(
                request_data["username"])
            if current_user is None:
                return {
                    "message": "Please provide correct login info",
                    "data": None,
                    "error": "Bad request"
                }, 400
            correct_password = False
            temporary_salt = bcrypt.gensalt()
            hashed_request_password = bcrypt.hashpw(
                password=request_data["password"].encode("utf-8"), salt=temporary_salt)
            if current_user.password_hash != hashed_request_password:
                return {
                    "message": "Invalid login data",
                    "data": None,
                    "error": "Auth error"
                }, 401
            try:
                current_user["token"] = jwt.encode({
                    "username": current_user["username"]
                },
                    self.flask_app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                current_user.pop("password")
                return current_user, 202
            except Exception as ex:
                return {
                    "message": "Error loging in",
                    "data": None,
                    "error": f"Internal server error: {str(ex)}",
                }, 500
        except Exception as ex:
            return {
                "message": "Error loging in",
                "data": None,
                "error": f"Internal server error: {str(ex)}",
            }, 500

    @require_auth
    def register_new_client_to_database(self, request_user):
        request_content_type = request.headers.get('Content-Type')
        json_string = ""
        if request_content_type == 'application/json':
            json_string = request.json
            try:
                json_object = json.loads(json_string)
                new_client_object = Client(mac_address=json_object["mac_address"], ip_address=json_object["ip_address"], hostname=json_object[
                                           "hostname"], client_version=json_object["client_version"], vm_list_on_machine=json_object["vm_list_on_machine"])
                self.database.add_client(new_client_object)
                response = jsonify(success=True)
                response.status_code = 201
                return response
            except Exception as ex:
                response = jsonify(success=False)
                response.status_code = 400
                return response

    def run(self):
        # add admin user to dataabse (or update existing one)
        salt = bcrypt.gensalt()
        temp_password_hash = bcrypt.hashpw(
            self.access_password.encode("utf-8"), salt)
        admin_user = self.database.get_user_by_name(self.access_username)
        if admin_user == None:
            admin_user = User(username=self.access_username,
                              password_hash=temp_password_hash)
        self.database.add_user(admin_user)
        self.app.add_endpoint(endpoint="/", endpoint_name="server_data",
                              handler=self.basic_server_data, methods=["GET"])
        self.app.add_endpoint(endpoint="/clients", endpoint_name="register_client",
                              handler=self.register_new_client_to_database, methods=["POST"])
        # TODO: add rest of endpoints
        self.app.run()
