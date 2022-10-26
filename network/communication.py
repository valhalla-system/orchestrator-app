from flask import Flask


class Server(host, port, name, access_password, version):
    app = Flask(self.name)

    @app.route("/")
    def basic_server_data(self):
        return {"server_name": self.name, "server_version": self.version, "host": self.host}

    @app.route("/client/register")
    def register_new_client_to_database(self):

        # TODO: implement
