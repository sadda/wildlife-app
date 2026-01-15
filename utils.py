def get_index(dataset, image_id):
    idx = dataset.metadata['image_id'] == image_id
    if idx.sum() != 1:
        raise ValueError('image_id not found or found multiple times.')
    return dataset.metadata[idx].index[0]
