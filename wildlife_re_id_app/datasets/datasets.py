import os
import wildlife_datasets
from . import utils

class WildlifeDataset:
    segmentation_url = None
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

    def download_segmentation(self, path):
        utils.download_file(self.segmentation_url, path)

    def download_verification(self, name):
        utils.download_file(self.verification_url, name)

    def get_index_database(self, i):
        return utils.get_index(self.database, i)

    def get_index_query(self, i):
        return utils.get_index(self.query, i)

    def try_basic_loading(self):
        raise NotImplementedError("Must be implemented by subclasses.")

class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv'
    verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def __init__(self, root):
        super().__init__(root, root)
    
    def download_dataset(self):
        self.dataset_wd.get_data(self.root_query)

    def load(self):
        # Check whether segmentations are present
        segmentation_csv = os.path.join(self.root_query, 'segmentation.csv')
        if not os.path.exists(segmentation_csv):
            self.download_segmentation(segmentation_csv)
        # Load the class with segmentations
        self.query = self.dataset_wd(self.root_query, load_segmentation=True, img_load='bbox')
        self.database = self.query

    def try_basic_loading(self):
        self.dataset_wd(self.root_query)
