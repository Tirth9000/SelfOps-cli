import typer, jwt
from functools import wraps
from decouple import config
from utils.file_utility import *


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_value("token")
        if not token:
            typer.echo("❌ You must login first: selfops login")
            return typer.Exit()
        try:
            token = jwt.decode(token, config("SECRET_KEY", default="supersecret"), algorithms=["HS256"])
        except jwt.InvalidTokenError:
            typer.echo("❌ Invalid token. Please login again.")
            raise typer.Exit()
        return func(*args, **kwargs)
    return wrapper
