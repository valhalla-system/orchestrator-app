from functools import wraps
import jwt
from flask import request, abort
from flask import current_app
from utils.models.models import User
from utils.database.database import Database
from utils.config.config import ServerConfig

# Inspired by: https://blog.loginradius.com/engineering/guest-post/securing-flask-api-with-jwt/ [access: 16.11.2022, 18:33 CET]


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return {
                "message": "Missing auth token",
                "data": None,
                "error": "Unauthorized"
            }, 401
        try:
            config = ServerConfig()
            database = Database(
                database_file=config.database_file, logging_level=config.server_loglevel)
            user_data_from_request = jwt.decode(
                token, config.jwt_secret, algorithms=["HS256"])
            request_user = database.get_user_by_name(
                username=user_data_from_request["username"])
            if request_user is None:
                return {
                    "message": "Invalid auth token",
                    "data": None,
                    "error": "Unauthorized"
                }, 403
        except Exception as ex:
            return {
                "message": "Internal server error",
                "data": None,
                "error": str(ex)
            }, 500

        return f(request_user, *args, **kwargs)

    return decorated
