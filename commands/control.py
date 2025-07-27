import typer

def start(container_name_or_id: str = typer.Argument(None, help="Container name or ID to start.")):
    print("Starting the service...")
    if container_name_or_id:
        print(f"Container {container_name_or_id} started.")

def stop(container_name_or_id: str = typer.Argument(None, help="Container name or ID to stop.")):
    print("Stopping the service...")
    if container_name_or_id:
        print(f"Container {container_name_or_id} stopped.")

def restart(cotainer_name_or_id: str = typer.Argument(None, help="Container name or ID to restart.")):
    print("Restarting the service...")
    if cotainer_name_or_id:
        print(f"Container {cotainer_name_or_id} restarted.")



def update_image():
    print("Updating the service image...")

