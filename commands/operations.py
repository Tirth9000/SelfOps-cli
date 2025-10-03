from rich.table import Table
import docker
from rich.console import Console
from docker.errors import DockerException

console = Console()

try:
    client = docker.from_env()
except DockerException as e:
    console.print("[bold red]❌ Docker daemon is not running. Please start Docker and try again.[/bold red]")
    console.print(f"Error details: {e}")
    exit(1)

def get_cpu_percent(cpu_stats, precpu_stats):
    try:
        cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
        system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get("system_cpu_usage", 0)
        cpu_count = cpu_stats.get("online_cpus", 1)
        if system_delta > 0.0 and cpu_delta > 0.0:
            return round((cpu_delta / system_delta) * 100, 2)
    except Exception:
        return 0.0
    return 0.0


def calculate_cpu_percent(stats):
    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
    if system_delta > 0.0 and cpu_delta > 0.0:
        return (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100.0
    return 0.0


def get_network_io(stats):
    if "networks" in stats:
        rx = sum(net["rx_bytes"] for net in stats["networks"].values())
        tx = sum(net["tx_bytes"] for net in stats["networks"].values())
        return {"rx_bytes": rx, "tx_bytes": tx}
    return {"rx_bytes": 0, "tx_bytes": 0}

def get_table():
    table = Table(title="🚀 Docker Containers Live Monitor", expand=True)
    table.add_column("Container", style="bold cyan", justify="left")
    table.add_column("CPU %", style="bold yellow", justify="right")
    table.add_column("Memory", style="magenta", justify="center")
    table.add_column("Status", style="green", justify="center")
    table.add_column("Health", style="bold red", justify="center")

    containers = client.containers.list(all=True)
    for container in containers:
        try:
            stats = container.stats(stream=False)
            cpu = get_cpu_percent(stats["cpu_stats"], stats["precpu_stats"])
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            mem_display = f"{mem_usage // (1024 * 1024)}MB / {mem_limit // (1024 * 1024)}MB"

            status = container.status
            health = container.attrs["State"].get("Health", {}).get("Status", "N/A")
            icon = "🟢" if status == "running" else "🔴"
            color = "green" if status == "running" else "red"
            table.add_row(f"{icon} {container.name}", f"{cpu}%", mem_display, f"[{color}] {status} [/{color}]", health)
        except Exception as e:
            table.add_row(container.name, "-", "-", "ERROR", str(e))
    return table
    