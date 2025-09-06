import typer, requests
from fastapi import status
from decouple import config
from utils.file_utility import create_and_write_file, read_value

auth_app = typer.Typer()

url = config("URL")

# logic remaining 
def login():
    try:
        username = typer.prompt("Enter your username ")
        password = typer.prompt("Enter your password ", hide_input=True)
        response = requests.post(url=f"{url}/cli/login", json={"username": username, "password": password})
        
        if response.status_code == status.HTTP_200_OK:
            typer.echo("Login successful!")
            create_and_write_file("token", response.json().get("token"))  
            
        else:
            typer.echo(f"Login failed: {response.json().get('message', 'Unknown Error')}", err=True)
            raise typer.Exit(code=1)

    except requests.ConnectionError:
        typer.echo("Error: Unable to connect to the authentication server.", err=True)
        raise typer.Exit(code=1)


def logout():
    if typer.confirm("Are you sure you want to logout?"):
        typer.echo("You have been logged out successfully.")
    else:
        typer.echo("Logout cancelled.")