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
    
    def download(self):
        self.dataset_wd.get_data(self.root)

    def get_index(self, i):
        return utils.get_index(self.dataset, i)


class TurtlesOfSMSRC(WildlifeDataset):
    dataset_wd = wildlife_datasets.datasets.TurtlesOfSMSRC

    def load(self):
        # Check whether the class loads without segmentations
        self.dataset_wd(self.root)
        # Check whether segmentations are present
        segmentation_csv = os.path.join(self.root, 'segmentation.csv')
        if not os.path.exists(segmentation_csv):
            # TODO: add download
            raise ValueError('segmentation.csv not found')
        # Load the class with segmentations
        # TODO: the segmentation.csv file must be identical
        self.dataset = self.dataset_wd(self.root, load_segmentation=True, img_load='bbox')
