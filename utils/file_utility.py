import os, re, sys
from decouple import config

FILE_PATH = config("FILE_PATH")


def read_content():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            return f.read()
    return ""


def create_and_write_file(key: str, value: str):
    content = read_content()

    with open(FILE_PATH, "w") as file:
        pattern = rf'^{key}\s*=\s*["\'].*?["\']'
        replacement = f'{key} = "{value}"'
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        else:
            if content and not content.endswith("\n"):
                content += "\n"
            content += replacement + "\n"
        file.write(content)


def read_value(key: str):
    content = read_content()
    pattern = rf'^{key}\s*=\s*["\'](.*?)["\']'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.group(1) 
    return None


def delete_key(key: str):
    content = read_content()

    pattern = rf'^{key}\s*=\s*["\'].*?["\']\n?'
    new_content = re.sub(pattern, '', content, flags=re.MULTILINE)
    with open(FILE_PATH, 'w') as file:
        file.write(new_content)

def cleanup_on_exit(*args):
    delete_key("token")
    return 