import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .utils import read_file


@dataclass(frozen=True)
class Site:

    title: str
    url: str
    author: str
    email: str
    data_file: str
    image_sizes: List

    @classmethod
    def from_filepath(cls, filepath: Path):

        if not filepath.exists():
            raise FileNotFoundError("Config file not found.")

        content = read_file(filepath=filepath)
        configs = yaml.safe_load(content)

        return cls(
            title=configs.get("title"),
            url=configs.get("url"),
            author=configs.get("author"),
            email=configs.get("email"),
            data_file=configs.get("data_file"),
            image_sizes=configs.get("image_sizes").split(),
        )
