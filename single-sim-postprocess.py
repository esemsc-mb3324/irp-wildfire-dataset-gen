import numpy as np
import os
import glob
import rasterio

# This script takes in the time of arrival file, specified like so:
# toa = './outputs/time_of_arrival_0000001_0001805.tif'
# and converts it to a numpy array, which is then saved as a .npy file.
# and uses the array to create files that show the time of arrival, fireline

# Desired shape: (timesteps, channel/band, h, w)

# function to convert geotiff to numpy array
def tif_to_npy(file_path, handle_nodata=True):
    """
    Load a GeoTIFF file as a numpy array, optionally handling NoData values
    """
    with rasterio.open(file_path) as src:
        data = src.read(1)
        # replace nodata values with nan if there are some
        if handle_nodata and src.nodata is not None:
            data = np.where(data==src.nodata, np.nan, data)

        return data, src.meta


