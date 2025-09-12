import typer, time
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv('/Users/tirthsharma/Downloads/Web-Dev/Projects/SelfOps/example.env'))


def selfops_info():
    logo = r"""
   _____ ________    __________  ____  _____      
  / ___// ____/ /   / ____/ __ \/ __ \/ ___/      
  \__ \/ __/ / /   / /_  / / / / /_/ /\__ \       
 ___/ / /___/ /___/ __/ / /_/ / ____/___/ /       
/____/_____/_____/_/    \____/_/    /____/   
         🚀 SelfOps CLI
"""
    for line in logo.splitlines():
        print(line)
        time.sleep(0.05) 

