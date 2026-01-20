import os
import wildlife_datasets
from . import utils

class WildlifeDataset:
    def __init__(self, root):
        self.root = root
        self.dataset = None
    
    def __getitem__(self, i):
        return self.dataset[i]
    
    @property
    def metadata(self):
        return self.dataset.metadata
    
    def is_downloaded(self):
        try:
            self.dataset_wd(self.root)
            return True
        except Exception:
            return False

    def download_dataset(self):
        self.dataset_wd.get_data(self.root)

    def download_segmentation(self, path):
        utils.download_file(self.segmentation_url, path)

    def download_verification(self, name):
        utils.download_file(self.verification_url, name)

    def get_index(self, i):
        return utils.get_index(self.dataset, i)


class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC
    segmentation_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/segmentation.csv'
    verification_url = 'https://raw.githubusercontent.com/sadda/wildlife-labels/refs/heads/main/TurtlesOfSMSRC/verification_data.csv'

    def load(self):
        # Check whether the class loads without segmentations
        self.dataset_wd(self.root)
        # Check whether segmentations are present
        segmentation_csv = os.path.join(self.root, 'segmentation.csv')
        if not os.path.exists(segmentation_csv):
            self.download_segmentation()
        # Load the class with segmentations
        self.dataset = self.dataset_wd(self.root, load_segmentation=True, img_load='bbox')
