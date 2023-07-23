import json
from pathlib import Path
from typing import Optional, Union, List

from .utils import read_file
from .data import DataManager
from .site import Site
from .builder import Builder
from .photo import Photo


class CLI:

    @staticmethod
    def add(src: str, ref: str, build: bool = False):
        # This method registers a photo in the database and copy the image in the non-public directory
        src = Path(src).resolve()
        ref = Path(ref).resolve()

        if not ref.is_file():
            raise ValueError("The reference provided is not a file.")

        site_configs = Site.from_filepath(filepath=Path(src, "config.yaml"))
        if not (data_filepath := Path(src, site_configs.data_file)).exists():
            DataManager.create_database(filepath=data_filepath)
        data_manager = DataManager.from_filepath(filepath=data_filepath)
        id = str(data_manager.get_max_id() + 1)
        data_manager.write(id=id, filename=ref.name)
        # if build:  # Figure out if this can be done. Is it convenient?
        #     self.build()

    @staticmethod
    def build(src: str, dst: str):
        # This method takes the info from data file and builds the documents needed
        dst = Path(dst).resolve()
        src = Path(src).resolve()

        site = Site.from_filepath(filepath=Path(src, "config.yaml"))

        data_manager = DataManager.from_filepath(filepath=Path(src, site.data_file))
        records_dict = data_manager.get_records(image_sizes=site.image_sizes)

        photos = [Photo.from_record(record=r) for r in records_dict.values()]

        builder = Builder(site=site, photos=photos)
        builder.build(src=src, dst=dst)
