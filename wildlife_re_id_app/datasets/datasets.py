import os
import wildlife_datasets
from . import utils
from .datasets_animal_re_id import TurtlewatchEgypt_Citizen, TurtlewatchEgypt_Master
from wildlife_datasets.datasets import WildlifeDataset as WD

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
    segmentation_urls = ['https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv']
    verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

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
        self.query = self.dataset_wd(self.root, load_segmentation=True, img_load='bbox')
        self.database = self.query

    def try_basic_loading(self) -> None:
        self.dataset_wd(self.root)


class TurtlewatchEgypt(WildlifeDataset):
    # dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = []
    # verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def __init__(self) -> None:
        pass
    
    def download_dataset(self):# -> Any:
        raise NotImplementedError()

    def get_segmentation_files(self) -> tuple[list[str], list[str]]:
        # TODO: finish
        return (self.segmentation_urls, [])

    def load(self) -> None:
        # TODO: add to config

        file_name = "wildlife_re_id_app/datasets/twe_individuals.csv"
        root_citizen = 'data/TurtlewatchEgypt/citizen'
        root_heads = 'data/TurtlewatchEgypt/PROFILES'
        root_flippers_f = 'data/TurtlewatchEgypt/TWE_flipperprofiles_registered ind_LR_front'
        root_flippers_r = 'data/TurtlewatchEgypt/TWE_flipperprofiles_registered ind_LR_rear'        
        # root_new = 'data/TurtlewatchEgypt'
        # roots_new = [
        #     # '2017 PICS + DATASHEET',
        #     # '2018 PICS + DATASHEET',
        #     # '2019 PICS + DATASHEET',
        #     # '2020 PICS + DATASHEET',
        #     # '2021 PICS + DATASHEET',
        #     # '2022 PICS + online database',
        #     # '2023 PICS + online database',
        #     # '2024 PICS + online database',
        #     '2025 PICS + online database',
        # ]

        database_query_matching = False
        dataset_q = TurtlewatchEgypt_Citizen(root_citizen, database_query_matching, load_label=False)
        dataset_d = TurtlewatchEgypt_Master(root_heads, root_flippers_f, root_flippers_r, database_query_matching, file_name, check_files=False, img_load="bbox", load_label=False)

        self.query = dataset_q.dataset
        self.database = dataset_d.dataset

    def try_basic_loading(self) -> None:
        # TODO: finish
        pass
