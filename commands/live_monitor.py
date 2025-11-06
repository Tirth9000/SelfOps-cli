import typer, docker, time
import socketio, ast
from decouple import config
from rich.console import Console
from docker.errors import DockerException
from utils.file_utility import get_value
from .operations import get_container_stats_json
from utils.middleware import login_required

console = Console()

try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)

sio = socketio.Client()


@sio.event
def connect():
    print("CLI Connected to the server")


@sio.event()
def disconnect():
    print("CLI Client Disconnected!")


    
@login_required
def live(app_name: str = typer.Argument(help="Name of the application to monitor required!")):
    if not app_name:
        console.print("[bold red]Application name is required to start live monitoring.[/bold red]")
        return

    try:
        url = config('BACKEND_URL', default="https://selfops.onrender.com")
        sio.connect(url, socketio_path="ws")
        app_id = get_value("app_id")
        response = sio.call('join', {"room": "cli-" + app_id})

        if response["status_code"] == 409:
            console.print("[bold yellow]⚠️ Live monitoring is already running.[/bold yellow]")
            return

        registered_apps = ast.literal_eval(get_value("registered_apps"))
        container_list = registered_apps.get(app_name, None)

        if container_list is None:
            console.print(f"[bold red]❌ No registered containers found for application '{app_name}'. Please initialize first.[/bold red]")
            return

        while True:
            containers_data = get_container_stats_json(container_list)
            sio.emit("live_message", containers_data)
            time.sleep(3)

    except Exception as e:
        print(f"An error occurred: {e}")