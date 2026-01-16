import os
import wildlife_datasets

class WildlifeDataset:
    def __init__(self, root):
        self.root = root
    
    def download(self):
        self.dataset_class.get_data(self.root)


class TurtlesOfSMSRC(WildlifeDataset):
    dataset_class = wildlife_datasets.datasets.TurtlesOfSMSRC

    def load_dataset(self):
        self.dataset_class(self.root)
        segmentation_csv = os.path.join(self.root, 'segmentation.csv')
        if not os.path.exists(segmentation_csv):
            # TODO: add download
            raise ValueError('segmentation.csv not found')
        # TODO: the segmentation.csv file must be identical
        return self.dataset_class(self.root, load_segmentation=True, img_load='bbox')
