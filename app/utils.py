def get_index(dataset, image_id):
    idx = dataset.metadata['image_id'] == image_id
    if idx.sum() > 1:
        raise ValueError('image_id found multiple times.')
    elif idx.sum() == 1:
        return dataset.metadata[idx].index[0]
    elif idx.sum() == 0:
        print(f'image_id {image_id} not found')
        return None
