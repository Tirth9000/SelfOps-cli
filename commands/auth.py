import typer, requests
from fastapi import status

auth_app = typer.Typer()


# logic remaining 
def login():
    username = typer.prompt("Enter your username ")
    password = typer.prompt("Enter your password ", hide_input=True)
    response = requests.post(url="http://localhost:8000/cli/login", json={"username": username, "password": password})
    print(response.status_code)
    if response.status_code == status.HTTP_200_OK:
        typer.echo("Login successful!")
    else:
        typer.echo(f"Login failed: {response.json().get('message', 'Unknown Error')}", err=True)
        raise typer.Exit(code=1)


def logout():
    if typer.confirm("Are you sure you want to logout? [y/N]"):
        typer.echo("You have been logged out successfully.")
    else:
        typer.echo("Logout cancelled.")