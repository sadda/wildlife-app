import os

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

    def is_downloaded(self) -> bool:
        try:
            self.try_basic_loading()
            return True
        except Exception:
            return False

    def get_index_database(self, i) -> int | None:
        assert self.database is not None
        return utils.get_index(self.database, i)

    def get_index_query(self, i) -> int | None:
        assert self.query is not None
        return utils.get_index(self.query, i)

    def download_dataset(self) -> None:
        raise NotImplementedError("Must be implemented by subclasses.")

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        raise NotImplementedError("Must be implemented by subclasses.")

    def load(self) -> None:
        raise NotImplementedError("Must be implemented by subclasses.")

    def try_basic_loading(self):
        raise NotImplementedError("Must be implemented by subclasses.")


class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = [
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv"
    ]
    verification_url = (
        "https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv"
    )

    def __init__(self, root: str) -> None:
        self.root = root

    def download_dataset(self) -> None:
        self.dataset_wd.get_data(self.root)

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        assert self.query is not None
        assert self.query.root is not None
        file_name = os.path.join(self.query.root, "segmentation.csv")
        return (self.segmentation_urls, [file_name])

    def load(self) -> None:
        self.query = self.dataset_wd(self.root, load_segmentation=True, img_load="bbox")
        self.database = self.query

    def try_basic_loading(self) -> None:
        self.dataset_wd(self.root)


class TurtlewatchEgypt(WildlifeDataset):
    # dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = []
    # verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def __init__(
            self,
            file_name: str,
            root_citizen: str,
            root_heads: str,
            root_flippers_f: str,
            root_flippers_r: str,
            ) -> None:
        
        self.file_name = file_name
        self.root_citizen = root_citizen
        self.root_heads = root_heads
        self.root_flippers_f = root_flippers_f
        self.root_flippers_r = root_flippers_r

    def download_dataset(self):
        raise NotImplementedError()

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        # TODO: finish
        return (self.segmentation_urls, [])

    def load(self) -> None:
        database_query_matching = False
        self.query = TurtlewatchEgypt_Citizen(self.root_citizen, database_query_matching, load_label=False).dataset
        self.database = TurtlewatchEgypt_Master(
            self.root_heads,
            self.root_flippers_f,
            self.root_flippers_r,
            database_query_matching,
            self.file_name,
            check_files=False,
            img_load="bbox",
            load_label=False,
        ).dataset

    def try_basic_loading(self) -> None:
        # TODO: finish
        pass
