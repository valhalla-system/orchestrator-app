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
            print(
                f"Password: {request_data['password']}, password hash from database: {current_user.password_hash}")
            # if current_user.password_hash != hashed_request_password:
            if not bcrypt.checkpw(request_data["password"].encode("utf-8"), current_user.password_hash):
                return {
                    "message": "Invalid login data",
                    "data": None,
                    "error": "Auth error"
                }, 401
            try:
                new_token = jwt.encode({
                    "username": current_user.username
                },
                    self.flask_app.config["SECRET_KEY"],
                    algorithm="HS256"
                )
                user_dictionary = current_user.as_dict()
                user_dictionary.pop("password_hash")
                user_dictionary["token"] = new_token
                return user_dictionary, 202
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
    def register_new_client_to_database(request_user, self):
        request_content_type = request.headers.get('Content-Type')
        if request_content_type == 'application/json':
            json_object = request.json
            try:
                new_client_object = Client(mac_address=json_object["mac_address"], ip_address=json_object["ip_address"], hostname=json_object[
                                           "hostname"], client_version=json_object["client_version"], vm_list_on_machine=json_object["vm_list_on_machine"])
                self.database.add_client(new_client_object)
                response = jsonify(success=True)
                response.status_code = 201
                return response
            except Exception as ex:
                response = jsonify({
                    "message": "Internal server error",
                    "data": None,
                    "error": str(ex)
                })
                response.status_code = 400
                return response

    @require_auth
    def add_image_to_database(request_user, self):
        request_content_type = request.headers.get('Content-Type')
        if request_content_type == 'application/json':
            json_object = request.json
            try:
                new_image_object = VMImage(
                    image_name=json_object["image_name"],
                    image_file=json_object["image_file"],
                    image_version=json_object["image_version"],
                    image_hash=json_object["image_hash"],
                    image_name_version_combo=f"{json_object['image_name']}@{json_object['image_version']}",
                    clients=[]
                )
                self.database.add_client(new_image_object)
                response = jsonify(success=True)
                response.status_code = 201
                return response
            except Exception as ex:
                response = jsonify({
                    "message": "Bad input",
                    "data": None,
                    "error": str(ex)
                })
                response.status_code = 400
                return response

    @require_auth
    def update_client_data(request_user, self):
        request_content_type = request.headers.get('Content-Type')
        if request_content_type == 'application/json':
            json_object = request.json
            try:
                old_client: Client = self.database.get_client_by_mac_address(json_object["mac_address"])
                if old_client == None:
                    response = jsonify({
                        "message": "client not found",
                        "data": None,
                        "error": None
                    })
                    response.status_code = 404
                    return response
                new_client: Client = Client(
                    mac_address=json_object["mac_address"],
                    ip_address=json_object["ip_address"],
                    hostname=json_object["hostname"],
                    client_version=json_object["client_version"],
                    vm_list_on_machine=[]
                )
                self.database.modify_client(new_client)
                response = jsonify({
                    "message": "Data updated",
                    "data": None,
                    "error": None
                })
                response.status_code = 201
                return response
            except Exception as ex:
                response = jsonify({
                    "message": "Internal server error",
                    "data": None,
                    "error": str(ex)
                })
                response.status_code = 400
                return response
    
    @require_auth
    def get_client_data(request_user, self, client_mac_address):
        try:
            client_data = self.database.get_client_by_mac_address(client_mac_address)
            return jsonify(client_data.as_dict())
        except Exception as ex:
            response = jsonify({
                "message": "Internal server error",
                "data": None,
                "error": str(ex)
            })
            response.status_code = 500
            return response
    
    @require_auth
    def get_client_list_of_vms(request_user, self, client_mac_address):
        try:
            vm_ids_list = self.database.get_client_vm_list_by_mac_address(client_mac_address)
            return jsonify(vm_ids_list)
        except Exception as ex:
            response = jsonify({
                "message": "Internal server error",
                "data": None,
                "error": str(ex)
            })
            response.status_code = 500
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
        self.app.add_endpoint(
            endpoint="/login", endpoint_name="login", handler=self.login, methods=["POST"])
        self.app.add_endpoint(endpoint="/clients", endpoint_name="register_client",
                              handler=self.register_new_client_to_database, methods=["POST"])
        self.app.add_endpoint(endpoint="/images", endpoint_name="add_image",
                              handler=self.add_image_to_database, methods=["POST"])
        self.app.add_endpoint(endpoint="/clients", endpoint_name="update_client", handler=self.update_client_data, methods=["PUT"])
        self.app.add_endpoint(endpoint="/clients/<client_mac_address>", endpoint_name="get_client_data", handler=self.get_client_data, methods=["GET"])
        self.app.add_endpoint(endpoint="/clients/<client_mac_address>/vms", endpoint_name="get_client_vms_list", handler=self.get_client_list_of_vms, methods=["GET"])
        # TODO: add rest of endpoints
        self.app.run()
