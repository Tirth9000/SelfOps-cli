import typer, jwt
from functools import wraps
from decouple import config
from utils.file_utility import read_value


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = read_value("token")
        if not token:
            typer.echo("❌ You must login first: selfops login")
            return typer.Exit()
        try:
            token = jwt.decode(token, config("SECRET_KEY"), algorithms=["HS256"])
            print(token)
        except jwt.InvalidTokenError:
            typer.echo("❌ Invalid token. Please login again.")
            raise typer.Exit()
        return func(*args, **kwargs)
    return wrapper
