import typer, docker
from rich.live import Live
from rich.table import Table
from rich.console import Console
from .operations import get_table, get_cpu_percent
import yaml, json, time


console = Console()
client = docker.from_env()


def init(yml_path: str = typer.Argument(None, help="Path to the YAML file to initialize the monitor commands.")):
    print("Initializing monitor commands...")
    if yml_path:
        yaml_file_path = yml_path
    yaml_file_path = "docker-compose.yml"

    try: 
        with open(yaml_file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        json_data = json.dumps(yaml_data, indent=4)
        print(json_data)
    
    except FileNotFoundError:
        typer.echo(f"Error: The file '{yaml_file_path}' does not exist.", err=True)



def monitor():
    containers = client.containers.list(all=True)

    with Live(console=console, refresh_per_second=3) as live:
        table = Table(title="🚀 Docker Containers Live Monitor", expand=True)
        table.add_column("Container", style="bold cyan", justify="left")
        table.add_column("CPU %", style="bold yellow", justify="right")
        table.add_column("Memory", style="magenta", justify="center")
        table.add_column("Status", style="green", justify="center")
        table.add_column("Health", style="bold red", justify="center")
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
                table.add_row(f"{icon} {container.name}", f"{cpu}%", mem_display, status, health)

            except Exception as e:
                table.add_row(container.name, "-", "-", "ERROR", str(e))
            live.update(table)

        while True:
            live.update(get_table())
            time.sleep(3)



def status():
    containers = client.containers.list(all=True)

    table = Table(title="Containers Status", expand=False)
    table.add_column("Container", style="bold cyan", justify="left")
    table.add_column("Status", justify="center")
    for container in containers:
        try:
            status = container.status
            icon = "🟢" if status == "running" else "🔴"
            status_color = "green" if status == "running" else "red"
            table.add_row(f"{icon} {container.name}", f"[{status_color}] {status} [/{status_color}]")
        except Exception as e:
            print(f"Error fetching status for {container.name}: {e}")
    console.print(table)
    typer.echo("Status check complete.")


def health_check():
    print("Performing health check...")

def logs():
    print("Fetching logs...")