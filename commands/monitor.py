from rich.live import Live
from rich.console import Console
from .operations import get_table


console = Console()



def init():
    print("Initializing monitor commands...")


def monitor(refresh: int = 1):
     with Live(get_table(), refresh_per_second=3, console=console) as live:
        while True:
            live.update(get_table())



def status():
    print("Checking status...")

def health_check():
    print("Performing health check...")

def logs():
    print("Fetching logs...")