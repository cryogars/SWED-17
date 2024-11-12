import numpy as np
import numpy.typing as npt

from rasterio import transform
from rasterio.io import MemoryFile


class ZoneRaster:
    """
    Helper class to handle rasterio MemoryFile.
    """

    @classmethod
    def bounding_box(cls, file: MemoryFile) -> dict:
        """
        Return bounding box for selection with Xarray.

        Parameters
        ----------
        file : MemoryFile
            Raster to extract the bounding box from

        Returns
        -------
        dict
            Dictionary with keys:
            * lat(minLat, maxLat)
            * lon(minLon, maxLon)
        """
        with file.open() as data:
            transform_info = data.profile['transform']
            width = data.profile['width']
            height = data.profile['height']

        ul = transform.xy(transform_info, 0, 0, offset='ul')
        lr = transform.xy(transform_info, height - 1, width - 1, offset='lr')

        lon_box = slice(ul[0], lr[0])
        lat_box = slice(lr[1], ul[1])

        return dict(lat=lat_box, lon=lon_box)

    @classmethod
    def data_as_xr(cls, file: MemoryFile) -> npt.NDArray:
        """
        Get raster data from file and return as array.

        Parameters
        ----------
        file : MemoryFile
            Raster to read data from

        Returns
        -------
        npt.NDArray
            Numpy array with mirror 0 axis to add as Xarray mask
        """
        with file.open() as data:
            data_array = data.read()

        return np.flip(data_array[0], axis=0)
