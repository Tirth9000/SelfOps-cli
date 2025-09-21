import socketio, time
from typer import Typer
from decouple import config
import docker
from rich.console import Console
from docker.errors import DockerException

from operations import get_cpu_percent

console = Console()

try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)

sio = socketio.Client()
app = Typer()


@sio.event
def connect():
    print("CLI Connected to the server")


@sio.event()
def disconnect():
    print("CLI Client Disconnected!")


def get_container_stats_json():
    containers = client.containers.list(all=True)
    
    data = []

    for container in containers:
        try:
            stats = container.stats(stream=False)
            cpu = get_cpu_percent(stats["cpu_stats"], stats["precpu_stats"])
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            mem_display = f"{mem_usage // (1024*1024)}MB / {mem_limit // (1024*1024)}MB"

            status = container.status
            health = container.attrs["State"].get("Health", {}).get("Status", "N/A")
            icon = "🟢" if status == "running" else "🔴"
            color = "green" if status == "running" else "red"

            container_data = {
                "name": container.name,
                "cpu": cpu,
                "memory": mem_display,
                "status": status,
                "health": health
            }
            data.append(container_data)
        except Exception as e:
            return {"error": str(e)}
    return data


@app.command()
def live_monitor():
    try:
        sio.connect(config("BACKEND_URL"))
        app_name = "selfops"
        sio.emit('join', {"username": "tirth", "room": app_name})

        while True:
            containers_data = get_container_stats_json()
            print(containers_data)
            time.sleep(3)

    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    app()