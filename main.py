import typer, time, signal, atexit
from commands import auth, control, monitor, operations
from core import utils
from utils.file_utility import cleanup_on_exit

app = typer.Typer()


#core info routes
# app.add_command()(utils.selfops_info)


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


# atexit.register(cleanup_on_exit)  
# signal.signal(signal.SIGINT, cleanup_on_exit) 
# signal.signal(signal.SIGTERM, cleanup_on_exit)

logo = r"""
   _____ ________    __________  ____  _____      
  / ___// ____/ /   / ____/ __ \/ __ \/ ___/      
  \__ \/ __/ / /   / /_  / / / / /_/ /\__ \       
 ___/ / /___/ /___/ __/ / /_/ / ____/___/ /       
/____/_____/_____/_/    \____/_/    /____/   
         🚀 SelfOps CLI
"""
def print_logo():
    for line in logo.splitlines():
        print(line)
        time.sleep(0.05) 

