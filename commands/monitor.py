import typer, docker, requests
from docker.errors import DockerException
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from .operations import get_table, get_cpu_percent, get_container_stats
from utils.middleware import login_required
from decouple import config
from utils.file_utility import get_value, set_value
import time


console = Console()
try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)

backend_url = config("BACKEND_URL", default="https://selfops.onrender.com")

# @login_required
def init(app_name: str = typer.Argument(..., help="provide the application name. "), 
         all: bool = typer.Option(False, "--all", "-a", help="Register all containers or select specific ones."),
         select: bool = typer.Option(False, "--select", "-s", help="Select specific containers to register.")):

    essentials = []
    selected_containers = []
    if not app_name:
        console.print("[bold red]Application name is required to initialize monitoring.[/bold red]")
        return

    elif all:
        console.print(f"[bold]Initializing {app_name} registration...[/bold]")
        containers = client.containers.list(all=True)
        if len(containers) == 0:
            console.print("[bold red]No containers found to register.[/bold red]")
            return
        
        completed = []
        with Progress(SpinnerColumn(spinner_name="dots"), 
                      TextColumn("[bold yellow]registering {task.description}"), 
                      transient=True, 
                      console=console
            ) as progress:
            for container in containers:
                task = progress.add_task(f"{container.name}...", start=True)
                container_stats = get_container_stats(container)
                time.sleep(2)
                # print(container_stats)
                essentials.append(container_stats)
                progress.remove_task(task)

                completed.append(f"[green]✓ {container.name} registered[/green]")

                console.clear()
                for c in completed:
                    console.print(c)
                time.sleep(0.4)


    elif select:
        console.print(f"[bold]Initializing {app_name} registration...[/bold]")
        for container in client.containers.list(all=True):

            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                transient=True,  # hides spinner after done
                console=console,
            ) as progress:
                progress.add_task(description=f"Registering {container.name}...", total=None)

                time.sleep(3)

                container_details = get_container_stats(container)
            

            console.print(f"\nFound container: [bold]{container_details['container_name']}[/bold]")
            color = "green" if container_details['status'] == "running" else "red"
            console.print(f"  Status: [{color}]{container_details['status']}[/{color}]")

            if Confirm.ask(f"Do you want to register [bold]{container_details['container_name']}[/bold]?"):
                console.print(f"[green]{container_details['container_name']} registered successfully![/green]\n")
                essentials.append(container_details)
                selected_containers.append(container_details['container_name'])
            else:
                console.print(f"[red]Skipped {container_details['container_name']}[/red]\n")

    registered_apps = {str(app_name): selected_containers}
    set_value("registered_apps", registered_apps)

    access_token = get_value("token")

    data = {"app_name": str(app_name), "containers": essentials}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{backend_url}/cli/store_stats", json=data, headers=headers)

    if response.status_code == 201:
        set_value("app_id", response.json().get("app_id"))
        console.print("\n[bold green]All containers registered successfully! 🎉[/bold green]\n")
    else:
        console.print(f"\n[bold red]Failed to register containers. Status code: {response.status_code}[/bold red]\n")
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
