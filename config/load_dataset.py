import json
from wildlife_re_id_app.datasets import TurtlesOfSMSRC, TurtlewatchEgypt

_DATASETS = {
    "TurtlesOfSMSRC": TurtlesOfSMSRC,
    "TurtlewatchEgypt": TurtlewatchEgypt,
}

def get_dataset(config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)

    dataset_cls = _DATASETS[cfg["dataset"]]
    kwargs = cfg.get("kwargs", {})
    return dataset_cls(**kwargs), cfg["dataset"]