import typer

auth_app = typer.Typer()


def login():
    username = typer.prompt("Enter your username ")
    password = typer.prompt("Enter your password ", hide_input=True)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("Logging you in...")


def logout():
    typer.echo("Are you sure you want to logout? [y/N]")
    if typer.confirm("Confirm logout"):
        # Logic to handle logout
        typer.echo("You have been logged out successfully.")
    else:
        typer.echo("Logout cancelled.")