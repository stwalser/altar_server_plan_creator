from pathlib import Path

import yaml


def load_yaml_file(path: str) -> list | dict:
    """Load a yaml file at the given path.

    :param path: The path to the yaml file.
    :return: The dictionary containing the content of the yaml file.
    """
    with Path(path).open("r") as file:
        return yaml.safe_load(file)
