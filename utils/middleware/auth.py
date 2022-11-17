from functools import wraps
import jwt
from flask import request, abort
from flask import current_app
from utils.models.models import User
from utils.database.database import Database

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
            database = Database(
                database_file=current_app.config["DATABASE_FILE"], logging_level=current_app.config["LOGGING_LEVEL"])
            user_data_from_request = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
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
