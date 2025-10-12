import typer, docker, requests
from docker.errors import DockerException
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .operations import get_table, get_cpu_percent, get_network_io, calculate_cpu_percent
from utils.middleware import login_required
from decouple import config
import yaml, json, time


console = Console()
try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)


@login_required
def init(app_name: str = typer.Argument(None, help="provide the application name. ")):
    if not app_name:
        console.print("[bold red]Application name is required to initialize monitoring.[/bold red]")
        return
    console.print(f"[bold]Initializing {app_name} registration...[/bold]")

    essentials = []
    for container in client.containers.list(all=True):
        stats = container.stats(stream=False)  # snapshot (not continuous stream)

        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            transient=True,  # hides spinner after done
            console=console,
        ) as progress:
            progress.add_task(description=f"Registering {container.name}...", total=None)

            time.sleep(3)
        
            port_binding = container.attrs["HostConfig"]["PortBindings"]
            for port, binding in port_binding.items():
                c_port = port
                if binding:
                    host_port = binding[0].get("HostPort", "N/A")
                else:
                    host_port = "N/A"

            container_details = {
                "container_id": container.short_id,
                "container_name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "status": container.status,   # running, exited, etc.
                "uptime": container.attrs["State"]["StartedAt"],  # ISO timestamp
                "restart_count": container.attrs["RestartCount"],
                "cpu_percent": get_cpu_percent(stats['cpu_stats'], stats['precpu_stats']),
                "memory_usage": stats["memory_stats"].get("usage", 0),
                "memory_limit": stats["memory_stats"].get("limit", 0),
                "network_io": get_network_io(stats),
                "ports": {"c_port": c_port, "host_port": host_port},
                "health": container.attrs["State"].get("Health", {}).get("Status", "N/A")
            }

        console.print(f"\nFound container: [bold]{container_details['container_name']}[/bold]")
        color = "green" if container_details['status'] == "running" else "red"
        console.print(f"  Status: [{color}]{container_details['status']}[/{color}]")

        if Confirm.ask(f"Do you want to register [bold]{container_details['container_name']}[/bold]?"):
            console.print(f"[green]{container_details['container_name']} registered successfully![/green]\n")
            essentials.append(container_details)
        else:
            console.print(f"[red]Skipped {container_details['container_name']}[/red]\n")

        # api call
    data = {"app_name": app_name, "containers": essentials}
    response = requests.post(f"{config('BACKEND_URL')}/cli/store_stats", json=data)
    print(response.status_code)
    print(response.json())
    return 



@login_required
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


@login_required
def status():
    console.print("[blue]Checking status of all containers...[/blue]")
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



@login_required
def health_check():
    print("Performing health check...")


@login_required
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

        
        
        
