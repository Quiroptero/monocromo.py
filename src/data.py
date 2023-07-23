import yaml
from datetime import datetime as dt
from typing import Union, Dict, Optional, List
from pathlib import Path

from .utils import read_file


class DataManager:

    def __init__(self, filepath: Path):
        self.filepath = filepath

    @classmethod
    def from_filepath(cls, filepath: Path):
        if not filepath.exists():
            raise FileNotFoundError("Database does not exist. Add a photo first.")
        return cls(filepath=filepath)

    @classmethod
    def create_database(cls, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.touch(exist_ok=True)

    @property
    def database(self) -> str:
        content = read_file(filepath=self.filepath)
        return content

    @property
    def ids(self):
        return [int(parts[0]) for parts in [line.split("\t") for line in self.database.splitlines()]]

    def get_max_id(self) -> int:
        return max(self.ids) if len(self.ids) else 0

    def get_min_id(self) -> int:
        return min(self.ids) if len(self.ids) else 0

    def write(self, id: str, filename: str):
        alt = dt.utcnow().strftime("%a, %d %b %Y")
        with open(self.filepath, "a") as file:
            file.writelines(f"{id}\t{alt}\t{filename}\n")
            file.close()

    def get_records(self, image_sizes: List[str]) -> Dict[str, Dict]:
        records = {}
        lines = [line.strip().split("\t") for line in self.database.splitlines()]
        for line in lines:
            records[line[0]] = {"id": line[0], "alt": line[1], "filename": line[2]}
        for key, value in records.items():
            prev_id = str(int(key) - 1) if int(key) > self.get_min_id() else None
            post_id = str(int(key) + 1) if int(key) < self.get_max_id() else None
            value.update({"prev_id": prev_id, "post_id": post_id, "sizes": image_sizes})
        return records
