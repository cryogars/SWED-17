import math
import pandas as pd
import xarray as xr

from swed_17.zone_db import CBRFCZone
from .zone_raster import ZoneRaster

from .rasterize_zone import cbrfc_zone_mask_as_xr

SWANN_SUFFIX = '_SWANN'

def swann_data_for_zone(
        swann_files: xr.Dataset, zone_name: str, zone_db: CBRFCZone
) -> xr.DataArray:
    """
    Retrieve the data for requested zone from given SWANN files and calculate
    daily means.

    This uses the database to get the CBRFC zone mask and then applies
    it to the files as a mask.

    Parameters
    ----------
    swann_files : xr.Dataset
        Xarray Dataset with all SWE files to extract data from
    zone_name : str
        CBRFC zone to get data for
    zone_db : CBRFCZone
        Instance that holds the database connection

    Returns
    -------
    xr.DataArray
        Results as xarray DataArray.
    """
    zone_mask = zone_db.as_rio(zone_name)
    swann_xr = swann_files.sel(
        ZoneRaster.bounding_box(zone_mask)
    )

    # Apply mask as new coordinate
    swann_xr.coords['mask'] = (
        ('lat', 'lon'), ZoneRaster.data_as_xr(zone_mask)
    )

    return swann_xr.where(swann_xr.mask == 1).mean(['lat', 'lon']).compute()


def swann_swe_for_zone(
        swann_xr: xr.Dataset, zone_name: str, zone_db: CBRFCZone
) -> pd.DataFrame:
    """Get SWE data from SWANN xarray dataset and return as dataframe.

    Uses the :meth:`swann_data_for_zone` to retrieve SWANN data.

    Parameters
    ----------
    swann_xr : xr.Dataset
        Dataset with all SWANN files
    zone_name : str
        Zone name to extract data for.
    zone_db : ZoneDB
        Connection object to the database

    Returns
    -------
    pd.DataFrame
        Dataframe with dates of peak SWE by year.
    """
    zone_df = swann_data_for_zone(
        swann_xr, zone_name, zone_db
    ).SWE.to_dataframe()

    zone_df = zone_df.rename(columns={'SWE': zone_name + SWANN_SUFFIX})
    # Pandas uses a time index that accounts for nano-leapseconds
    # Rounding to the nearest day.
    zone_df.index = zone_df.index.round('D')

    return zone_df

def target_bounding_box_padded(target_zones: xr.Dataset) -> dict:
    """
    Get bounding box for Xarray dataset.

    Assumes that the coordinates are labeled as lon/lat. The coordinates
    are also rounded to add padding.

    Parameters
    ----------
    target_zones : xr.Dataset
        Dataset to extract bounding box from.

    Returns
    -------
    dict
        Dictionary containing the lat and lon as keys.
    """
    lon_box = slice(
        math.floor(target_zones.lon.values.min()),
        math.ceil(target_zones.lon.values.max())
    )
    lat_box = slice(
        math.floor(target_zones.lat.values.min()),
        math.ceil(target_zones.lat.values.max())
    )
    return dict(lat=lat_box, lon=lon_box)


def combine_cbrfc_swann(swann, cbrfc_zones):
    """
    Combines CBRFC mask with SWANN SWE and
    computes the CBRFC zonal mean.
    """
    return xr.combine_by_coords(
        [
            cbrfc_zones,
            swann,
        ],
        coords=['lat', 'lon'],
        join='inner'
    ).groupby('zone').mean()


def swann_swe_for_zones(
    swann_files,
    cbrfc_zone_tif,
    cbrfc_zone_shape,
    target_zones_dict,
):
    """
    Mask SWANN SWE with given CBRFC zone Tif and list of
    targeted zones.
    """

    target_cbrfc_zones = cbrfc_zone_mask_as_xr(
        cbrfc_zone_tif, cbrfc_zone_shape
    )

    # Reduce to zones of interest
    target_cbrfc_zones = target_cbrfc_zones.where(
        target_cbrfc_zones.isin(list(target_zones_dict.values())),
        drop=True
    )

    # Get SWE values for bounding box of target zones
    swann = xr.open_mfdataset(swann_files, parallel=True).sel(
        target_bounding_box_padded(target_cbrfc_zones)
    )

    swann = swann.interp(
        lat=target_cbrfc_zones.lat.values,
        lon=target_cbrfc_zones.lon.values,
        method='nearest'
    )

    swann_cbrfc_zones = combine_cbrfc_swann(swann, target_cbrfc_zones)

    return swann_cbrfc_zones.where(
        swann_cbrfc_zones.zone.isin(
            list(target_zones_dict.values())
        ), drop=True
    ).SWE.compute()
