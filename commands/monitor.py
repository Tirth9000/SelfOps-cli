import typer, docker
from docker.errors import DockerException
from rich.live import Live
from rich.table import Table
from rich.console import Console
from .operations import get_table, get_cpu_percent
import yaml, json, time


console = Console()
try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)


def init(yml_path: str = typer.Argument(None, help="Path to the YAML file to initialize the monitor commands.")):
    console.print("[blue]Initializing monitor commands...[/blue]")
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
    if len(containers) == 0:
        console.print("[bold red]No containers found to monitor.[/bold red]")
        return

    console.print("[blue]Starting live monitoring of Docker containers... [/blue]")
    with Live(console=console, refresh_per_second=2) as live:
        table = Table(title="🚀 Docker Containers Live Monitor", expand=True)
        table.add_column("Container", style="bold cyan", justify="left")
        table.add_column("CPU %", style="bold yellow", justify="right")
        table.add_column("Memory", style="magenta", justify="center")
        table.add_column("Status", justify="center")
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
                color = "green" if status == "running" else "red"
                table.add_row(f"{icon} {container.name}", f"{cpu}%", mem_display, f"[{color}] {status} [/{color}]", health)

            except Exception as e:
                table.add_row(container.name, "-", "-", "ERROR", str(e))
            live.update(table)

        while True:
            live.update(get_table())
            time.sleep(1)


def status():
    try:
        containers = client.containers.list(all=True)

        table = Table(title="Containers Status", expand=False)
        table.add_column("Container", style="bold cyan", justify="left")
        table.add_column("Status", justify="center")
        for container in containers:
            try:
                container = client.containers.get(container.id)
                status = container.status
                icon = "🟢" if status == "running" else "🔴"
                status_color = "green" if status == "running" else "red"
                table.add_row(f"{icon} {container.name}", f"[{status_color}] {status} [/{status_color}]")
            except Exception as e:
                console.print(f"[red]Error fetching status for {container.name}: {e}[/red]")
        console.print(table)
        console.print("[green]Status check completed.[/green]")
    except docker.errors.APIError as e:
        console.print(f"[bold red]Docker API error: {e}[/bold red]")



def health_check():
    print("Performing health check...")


def logs(container_name_or_id: str = typer.Argument(None, help="Container name or ID to fetch logs."),
         live_log: bool = typer.Option(False, "--live", "-l", help="Fetch live logs.")):
    try:
        if not container_name_or_id:
            console.print("[bold red]Container name or ID is required to fetch logs.[/bold red]")
            return
        
        elif container_name_or_id:
            container = client.containers.get(container_name_or_id)
            if not container:
                console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]")
                return

            if live_log:
                for log in container.logs(stream=True, follow=True):
                    log_line = log.decode('utf-8').strip()
                    console.print(log_line)
                console.print("[bold green]Live logs streaming stopped.[/bold green]")

            else:
                logs = container.logs(stream=False)
                console.print(f"[bold cyan]Logs for {container_name_or_id}:[/bold cyan]")
                console.print(logs.decode('utf-8'))
        else:
            console.print("[bold red]Please provide a container name or ID to fetch logs.[/bold red]")

    except docker.errors.NotFound:
        console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]")
    except docker.errors.APIError as e:
        console.print(f"[bold red]Docker API error: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred while fetching logs: {e}[/bold red]")