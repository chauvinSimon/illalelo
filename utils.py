import yaml
from pathlib import Path


def yaml_load(file_path: Path) -> dict:
    if not file_path.is_file():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with file_path.open('r') as file:
        return yaml.safe_load(file)


def read_file(file_path: Path) -> str:
    with file_path.open('r') as file:
        return file.read()

def save_file(file_path: Path, content: str) -> None:
    with file_path.open('w') as file:
        file.write(content)
