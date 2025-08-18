import typer, docker
from docker.errors import DockerException
from rich.console import Console
from rich.table import Table
from rich.live import Live
import time

console = Console()
try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)


def start(container_names_or_ids: list[str] = typer.Argument(None, help="Container name or ID to start."),
          all_containers: bool = typer.Option(False, "--all", "-a", help="start all containers.")):
    try:
        if all_containers:
            console.print('[blue]Starting all containers...[/blue]')
            containers = client.containers.list(all=True, filters={"status": "exited"})

            with Live(console=console, refresh_per_second=2) as live:
                table = Table(title="Starting Containers", expand=False)
                table.add_column("Container", style="bold cyan", justify="left")
                table.add_column("Status", justify="center")

                if len(containers) == 0:
                    console.print("[bold red]No stopped containers found.[/bold red]")
                    console.print("[bold green]All containers are running already.[/bold green]")
                    return 

                for container in containers:
                    container.start()
                    container = client.containers.get(container.id)
                    time.sleep(1)
                    color = "green" if container.status == "running" else "red"
                    icon = "🟢" if container.status == "running" else "🔴"
                    table.add_row(f"{icon} {container.name}", f"[{color}] {container.status} [/{color}]")
                    live.update(table)
            console.print("[bold green]All containers have been started.[/bold green]")
            return 

        elif container_names_or_ids:
            with Live(console=console, refresh_per_second=2) as live:
                console.print("[blue]Starting containers ... [/blue]")

                table = Table(title="Container Status", expand=False)
                table.add_column("Container", style="bold cyan", justify="left")
                table.add_column("Status", justify="center")

                for container_name in container_names_or_ids:
                    container = client.containers.get(container_name)
                    if not container:
                        console.print(f"[bold red]Container '{container_name}' not found.[/bold red]")
                
                    else:
                        if container.status == "exited":
                            container.start()
                            console.print(f"[/green]Container [cyan]'{container_name}'[/cyan] started.[/green]")
                        else:
                            console.print(f"[green]Container [cyan]'{container_name}'[/cyan] is already running.[/green]")
                        
                        container = client.containers.get(container_name)
                        
                        current_status = container.status
                        icon = "🟢" if current_status == "running" else "🔴"
                        color = "green" if current_status == "running" else "red"
                        table.add_row(f"{icon} " + container.name, f"[{color}]{current_status}[/{color}]")
                live.update(table)
        else:
            console.print("[bold red]Please provide a container name or ID to start.[/bold red]")
                
    except docker.errors.NotFound:
        console.print(f"[bold red]Container '{container_names_or_ids}' not found. [/bold red]")



# multiple container input remaining
def stop(container_name_or_id: list[str] = typer.Argument(None, help="Container name or ID to stop."),
         all_containers: bool = typer.Option(False, "--all", "-a", help="stop all the containers.")):
    try: 
        if all_containers:
            print('Stopping all running containers...')
            containers = client.containers.list(filters={"status": "running"})

            table = Table(title="Stopping containers", expand=False)
            table.add_column("Container", style="bold cyan", justify="left")
            table.add_column("Status", justify="center")
            with Live(console=console, refresh_per_second=2) as live:
                for container in containers:
                    container.stop()
                    container = client.containers.get(container.id)
                    time.sleep(1)
                    color = "red" if container.status == "exited" else "green"
                    icon = "🔴" if container.status == "exited" else "🟢"
                    table.add_row(f"{icon} {container.name}", f"[{color}] {container.status} [/{color}]")
                    live.update(table)
            console.print("[bold green]All running containers have been stopped.[/bold green]")
            return

        elif container_name_or_id:
            container = client.containers.get(container_name_or_id)
            if not container:
                console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]")
                return

            print("Stopping the container...")
            if container.status == "running":
                container.stop()
                with Live(console=console, refresh_per_second=3) as live:
                    while container.status != "exited":
                        container = client.containers.get(container_name_or_id)

                        table = Table(title="Container Status", expand=False)
                        table.add_column("Container", style="bold cyan", justify="left")
                        table.add_column("Status", style="red", justify="center")
                        color = 'red' if container.status == "exited" else 'green'
                        icon = "🔴" if container.status == "exited" else "🟢"
                        table.add_row(f"{icon} {container.name}", f"[{color}]{container.status}[/{color}]")
                        live.update(table)
                typer.echo(f"Container {container_name_or_id} stopped.")
            else:
                typer.echo(f"Container {container_name_or_id} is not running.")
        else:
            console.print("[bold red]Please provide a container name or ID to stop.[/bold red]")

    except docker.errors.NotFound:
        console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]" )


# multiple input remaining
def restart(container_name_or_id: str = typer.Argument(None, help="Container name or ID to restart."),
            all_containers: bool = typer.Option(False, "--all", "-a", help="Restart all the containers.")):
    try:
        with Live(console=console, refresh_per_second=2) as live:
            if all_containers:
                console.print('[blue]Restarting all containers...[/blue]')
                containers = client.containers.list(all=True)

                table = Table(title="Restarting Containers", expand=False)
                table.add_column("Container", style="bold cyan", justify="left")
                table.add_column("Status", justify="center")

                for container in containers:
                    container.restart()
                    time.sleep(1)
                    color = "green" if container.status == "running" else "red"
                    icon = "🟢" if container.status == "running" else "🔴"
                    table.add_row(f"{icon} {container.name}", f"[{color}] {container.status} [/{color}]")
                    live.update(table)
                console.print("[bold green]All containers have been restarted.[/bold green]")
                return
                
            elif container_name_or_id:
                container = client.containers.get(container_name_or_id)
                if not container:
                    console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]")
                    return

                first_run = True
                console.print(f"[bold white]Restarting container '{container.name}'...[/bold white]")
                while True:
                    container = client.containers.get(container_name_or_id)

                    table = Table(title="Restarting Container", expand=False)
                    table.add_column("Container", style="bold cyan", justify="left")
                    table.add_column("Status", justify="center")

                    status = container.status
                    color = "green" if status == "running" else "red"
                    icon = "🟢" if status == "running" else "🔴"
                    table.add_row(f"{icon} {container.name}", f"[{color}] {status} [/{color}]")
                    live.update(table)
                    
                    if first_run:
                        container.restart()
                        time.sleep(2)
                        first_run = False
                    else:
                        break
            else:
                console.print("[bold red]Please provide a container name or ID to restart.[/bold red]")
        console.print(f"[bold green]Container [magenta]'{container.name}'[/magenta] restarted successfully.[/bold green]")

    except docker.errors.NotFound:
        console.print(f"[bold red]Container '{container_name_or_id}' not found.[/bold red]")
        return
            




def update_image():
    print("Updating the service image...")

