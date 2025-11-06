import typer, time
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.align import Align

console = Console()

def show_intro():
    greet = "Welcome to SelfOps CLI"
    for char in greet:
        console.print(char, end="", style="bold white")
        time.sleep(0.08)
    time.sleep(1)
    for i in range(3):
        console.print(" .", end="", style="bold white")
        time.sleep(1)
    console.print("\n")


    logo_text = Text("""
                     
                     
   ███████╗███████╗██╗     ███████╗ ██████╗ ██████╗ ███████╗
   ██╔════╝██╔════╝██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝
   ███████╗█████╗  ██║     █████╗  ██║   ██║██████╔╝███████╗
   ╚════██║██╔══╝  ██║     ██╔══╝  ██║   ██║██╔═══╝ ╚════██║
   ███████║███████╗███████╗██║     ╚██████╔╝██║     ███████║
   ╚══════╝╚══════╝╚══════╝╚═╝      ╚═════╝ ╚═╝     ╚══════╝
    """)

    centered_logo = Align.center(logo_text)
    for line in centered_logo.renderable.split("\n"):
        console.print(Align.center(line, style="bold dodger_blue3"))
        time.sleep(0.1)  # Slight delay for effect

    table = Table(title="✨ Quick Start Commands", title_style="bold cyan", show_lines=True)
    table.add_column("Command", style="bold green", justify="center")
    table.add_column("Description", style="yellow")

    table.add_row("selfops init", "Initialize your project")
    table.add_row("selfops login", "Login to SelfOps")
    table.add_row("selfops status", "Check current status")
    table.add_row("selfops help", "Show help menu")

    console.print(table)


def intro(ctx: typer.Context):
    """SelfOps CLI entrypoint."""
    if ctx.invoked_subcommand is None:
        show_intro()