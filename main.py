import typer
from commands import auth, control, monitor

app = typer.Typer()


# auth routes
app.command(name="login")(auth.login)
app.command(name="logout")(auth.logout)


# control routes
app.command(name="start")(control.start)
app.command(name="stop")(control.stop)
app.command(name="restart")(control.restart)
app.command(name="update-image")(control.update_image)


# monitor routes
app.command(name="init")(monitor.init)
app.command(name="monitor")(monitor.monitor)
app.command(name="status")(monitor.status)
app.command(name="health-check")(monitor.health_check)
app.command(name="logs")(monitor.logs)




if __name__ == "__main__":
    app()