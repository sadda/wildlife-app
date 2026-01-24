import json
from app import TurtlesOfSMSRC

_DATASETS = {
    "TurtlesOfSMSRC": TurtlesOfSMSRC,
}

def get_dataset(config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)

    dataset_cls = _DATASETS[cfg["dataset"]]
    return dataset_cls(cfg["root"]), cfg["dataset"]