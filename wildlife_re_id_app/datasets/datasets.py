import ast
import os

import pandas as pd
import wildlife_datasets
from wildlife_datasets.datasets import WildlifeDataset as WD

from . import utils
from .datasets_animal_re_id import TurtlewatchEgypt_Citizen, TurtlewatchEgypt_Master


class WildlifeDataset:
    segmentation_urls: list[str] = []
    verification_url: str | None = None

    def __init__(self) -> None:
        self.query: WD | None = None
        self.database: WD | None = None

    def get_index_database(self, i) -> int | None:
        assert self.database is not None
        return utils.get_index(self.database, i)

    def get_index_query(self, i) -> int | None:
        assert self.query is not None
        return utils.get_index(self.query, i)

    def download_dataset(self) -> None:
        raise NotImplementedError("Must be implemented by subclasses.")

    def is_downloaded(self) -> bool:
        raise NotImplementedError("Must be implemented by subclasses.")

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        raise NotImplementedError("Must be implemented by subclasses.")

    def load(self) -> None:
        raise NotImplementedError("Must be implemented by subclasses.")


class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = [
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv"
    ]
    verification_url = (
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv"
    )

    def __init__(self, root: str, matching_encounters_path: str | None = None) -> None:
        self.root = root
        self.matching_encounters_path = matching_encounters_path

    def download_dataset(self) -> None:
        self.dataset_wd.get_data(self.root)

    def is_downloaded(self) -> bool:
        file_name = os.path.join(self.root, "metadata.csv")
        return os.path.exists(file_name)

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        file_name = os.path.join(self.root, "segmentation.csv")
        return (self.segmentation_urls, [file_name])

    def load(self) -> None:
        replace_identity = []
        if self.matching_encounters_path is not None:
            if not os.path.exists(self.matching_encounters_path):
                raise FileNotFoundError(f"Matching encounters file not found: {self.matching_encounters_path}")
            with open(self.matching_encounters_path) as f:
                replace_identity = ast.literal_eval(f.read())
        self.query = self.dataset_wd(
            self.root, load_segmentation=True, img_load="bbox", replace_identity=replace_identity
        )
        self.database = self.query


class TurtlewatchEgypt(WildlifeDataset):
    dataset_wd_query = wildlife_datasets.datasets.TurtlewatchEgypt_Citizen
    segmentation_urls = [
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/Turtlewatch_Egypt/segmentation.csv"
    ]
    verification_url = (
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/Turtlewatch_Egypt/verification_data.csv"
    )

    def __init__(
            self,
            file_name_individuals: str,
            file_name_downloads: str,
            root_citizen: str,
            root_heads: str,
            root_flippers_f: str,
            root_flippers_r: str,
            ) -> None:
        
        self.file_name_individuals = file_name_individuals
        self.file_name_downloads = file_name_downloads
        self.root_citizen = root_citizen
        self.root_heads = root_heads
        self.root_flippers_f = root_flippers_f
        self.root_flippers_r = root_flippers_r

    def download_dataset(self) -> None:
        data = pd.read_csv(self.file_name_downloads)
        self.dataset_wd_query.get_data(self.root_citizen, data=data, force=True)

    def is_downloaded(self) -> bool:
        # TODO: return hard error for other datasets
        file_name = os.path.join(self.root_citizen, "metadata.csv")
        return os.path.exists(file_name)

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        # TODO: add segmentation for master database
        # TODO: check if master database contains additional files, it also loads
        file_name = os.path.join(self.root_citizen, "segmentation.csv")
        return (self.segmentation_urls, [file_name])

    def load(self) -> None:
        dataset_kwargs_citizen = {"load_label": False}
        dataset_kwargs_master = {"load_label": False, "check_files": False, "img_load": "bbox"}

        database_query_matching = True
        self.query = TurtlewatchEgypt_Citizen(self.root_citizen, database_query_matching, dataset_kwargs=dataset_kwargs_citizen).dataset
        self.database = TurtlewatchEgypt_Master(
            self.root_heads,
            self.root_flippers_f,
            self.root_flippers_r,
            database_query_matching,
            self.file_name_individuals,
            dataset_kwargs=dataset_kwargs_master
        ).dataset
