import os
from decouple import config
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC



kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=config("SALT", default="selfops-salt").encode("utf-8"),
    iterations=390000,
)
key = base64.urlsafe_b64encode(kdf.derive(config("PASSWORD", default="super-secret-password").encode("utf-8")))
fernet = Fernet(key)


APP_DIR = os.path.join(os.path.expanduser("~"), ".selfops")
os.makedirs(APP_DIR, exist_ok=True)


CONFIG_FILE = os.path.join(APP_DIR, "selfops_config.enc")



def read_config_dict():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "rb") as f:
        encrypted = f.read()
    decrypted = fernet.decrypt(encrypted).decode()
    return dict(line.split("=", 1) for line in decrypted.splitlines() if "=" in line)


def save_config_dict(config: dict):
    text = "\n".join(f"{k}={v}" for k, v in config.items())
    encrypted = fernet.encrypt(text.encode())
    with open(CONFIG_FILE, "wb") as f:
        f.write(encrypted)



def set_value(key: str, value: str):
    config = read_config_dict()
    config[key.capitalize()] = value  
    save_config_dict(config)

def get_value(key: str):
    config = read_config_dict()
    return config.get(key.capitalize(), None)

def delete_value(key: str):
    config = read_config_dict()
    if key.capitalize() in config:
        del config[key.capitalize()]
        save_config_dict(config)
    else:
        return None