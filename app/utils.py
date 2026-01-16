import requests

def get_index(dataset, image_id):
    idx = dataset.metadata['image_id'] == image_id
    if idx.sum() > 1:
        raise ValueError('image_id found multiple times.')
    elif idx.sum() == 1:
        return dataset.metadata[idx].index[0]
    elif idx.sum() == 0:
        print(f'image_id {image_id} not found')
        return None

def download_file(url, output_path):
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(r.content)