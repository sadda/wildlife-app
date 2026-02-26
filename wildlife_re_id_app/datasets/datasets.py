import os
import wildlife_datasets
from . import utils
from .datasets_animal_re_id import TurtlewatchEgypt_Citizen, TurtlewatchEgypt_Master

class WildlifeDataset:
    segmentation_urls = None
    verification_url = None

    def __init__(self, root_query, root_database):
        self.root_query = root_query
        self.root_database = root_database
        self.query = None
        self.database = None
    
    def is_downloaded(self):
        try:
            self.try_basic_loading()            
            return True
        except Exception:
            return False

    def get_index_database(self, i):
        return utils.get_index(self.database, i)

    def get_index_query(self, i):
        return utils.get_index(self.query, i)

    def try_basic_loading(self):
        raise NotImplementedError("Must be implemented by subclasses.")

class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = ['https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv']
    verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def __init__(self, root):
        super().__init__(root, root)
    
    def download_dataset(self):
        self.dataset_wd.get_data(self.root_query)

    def get_segmentation_files(self):
        file_name = os.path.join(self.query.root, "segmentation.csv")
        return (self.segmentation_urls, [file_name])
    
    def load(self):
        self.query = self.dataset_wd(self.root_query, load_segmentation=True, img_load='bbox')
        self.database = self.query

    def try_basic_loading(self):
        self.dataset_wd(self.root_query)


class TurtlewatchEgypt(WildlifeDataset):
    # dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_urls = []
    # verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def __init__(self):
        # TODO: hacky
        # TODO: in general, I do not like that dataset.root_query appears in the app
        super().__init__(None, None)
    
    def download_dataset(self):
        raise NotImplementedError()

    def get_segmentation_files(self):
        # TODO: finish
        return (self.segmentation_urls, [])

    def load(self):
        # TODO: add to config

        file_name = "wildlife_re_id_app/datasets/twe_individuals.csv"
        root_citizen = 'data/TurtlewatchEgypt/citizen'
        root_heads = 'data/TurtlewatchEgypt/PROFILES'
        root_flippers_f = 'data/TurtlewatchEgypt/TWE_flipperprofiles_registered ind_LR_front'
        root_flippers_r = 'data/TurtlewatchEgypt/TWE_flipperprofiles_registered ind_LR_rear'        
        root_new = 'data/TurtlewatchEgypt'
        roots_new = [
            # '2017 PICS + DATASHEET',
            # '2018 PICS + DATASHEET',
            # '2019 PICS + DATASHEET',
            # '2020 PICS + DATASHEET',
            # '2021 PICS + DATASHEET',
            # '2022 PICS + online database',
            # '2023 PICS + online database',
            # '2024 PICS + online database',
            '2025 PICS + online database',
        ]

        database_query_matching = False
        dataset_q = TurtlewatchEgypt_Citizen(root_citizen, database_query_matching, load_label=False)
        dataset_d = TurtlewatchEgypt_Master(root_heads, root_flippers_f, root_flippers_r, database_query_matching, file_name, check_files=False, img_load="bbox", load_label=False)

        self.query = dataset_q.dataset
        self.database = dataset_d.dataset

    def try_basic_loading(self):
        # TODO: finish
        pass
