import rasterio as rio


def sample_gen(dataset, x,y, indexes=None):
    #rewrite de la source du meme nom de rio (rio.sample.sample_gen) 
    index = dataset.index
    read = dataset.read
    if isinstance(indexes, int):
        indexes = [indexes]
    r, c = index(x, y)
    window = ((r, r+1), (c, c+1))
    data = read(indexes, window=window, masked=False, boundless=True)
    return(data[0][0][0])