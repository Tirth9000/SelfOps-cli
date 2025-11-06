import typer, requests
from fastapi import status
from decouple import config
from utils.file_utility import *

auth_app = typer.Typer()

url = config("BACKEND_URL")


def login():
    try:
        email = typer.prompt("Enter your email ")
        password = typer.prompt("Enter your password ", hide_input=True)
        data = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{url}/cli/login", json=data)
        
        if response.status_code == status.HTTP_200_OK:
            token = response.json()["access_token"]
            username = response.json().get('username')
            set_value("username", username)
            set_value("token", token)
            typer.echo(f"User: {username} Login successful!")
            
        else:
            typer.echo(f"[red]Login failed![/red]", err=True)
            return

    except requests.ConnectionError:
        typer.echo("[red]Error: Unable to connect to the authentication server.[/red]", err=True)
        return


def logout():
    if typer.confirm("Are you sure you want to logout?"):
        response = delete_value("token")
        username = get_value("username")
        if response is not None:
            typer.echo(f"User: {username} Logged out successfully.")
        else:
            typer.echo("You are not logged in.", err=True)
    else:
        typer.echo("Logout cancelled.")