import typer, requests
from fastapi import status
from rich.console import Console
from decouple import config
from utils.file_utility import *

auth_app = typer.Typer()
console = Console()

url = config("BACKEND_URL", default="https://selfops.onrender.com")


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
            console.print(f"User: {username} Login successful!")
            
        else:
            console.print(f"[red]Login failed![/red]", err=True)
            return

    except requests.ConnectionError:
        console.print("[red]Error: Unable to connect to the authentication server.[/red]", err=True)
        return


def logout():
    if typer.confirm("Are you sure you want to logout?"):
        response = delete_value("token")
        username = get_value("username")
        if response is not None:
            console.print(f"User: {username} Logged out successfully.")
        else:
            console.print("You are not logged in.", err=True)
    else:
        console.print("Logout cancelled.")