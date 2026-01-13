import xarray as xr
import numpy as np
import pandas as pd

from psycopg import sql
from nb_paths import SWE_DB, SNOW17_DB, MODEL_DOMAINS, BASIN_DIR

ZONE_QUERY = """
SELECT cz.gid, cc.ch5_id, cz.segment, cz.zone, cc.description
 FROM cbrfc_zones cz LEFT JOIN cbrfc_ch5id cc ON cz.ch5_id = cc.id
 WHERE cz.gid in ({});
"""
SWE_QUERY = """
SELECT *
 FROM public.zonal_swe
 WHERE
    cbrfc_zone_id in ({}) AND
    date >= to_date({}, 'YYYY-MM-DD')
"""
ZONE_NAME = "Zone Name"
DATA_COLUMNS = [
    "Date",
    ZONE_NAME,
    "iSnobal",
    "SNODAS",
    "UArizona",
    "CU Boulder",
    "ASO",
    "ID",
]

def available_zones():
    zone_ids = []

    for domain in MODEL_DOMAINS:
        domain = xr.open_dataset(BASIN_DIR + f"/{domain}_topo.nc")
        zone_ids = np.append(zone_ids, np.unique(domain.cbrfc_zone.values))

    zone_query = sql.SQL(ZONE_QUERY).format(
        sql.SQL(",").join(map(sql.Literal, zone_ids))
    )

    with SWE_DB.query(zone_query) as results:
        zones = pd.DataFrame(
            results.fetchall(),
            columns=["ID", "CH5ID", "Segment", ZONE_NAME, "Description"],
        ).set_index("ID")

    return zones


def swe_for_zone(zone_ids: list, date: str):
    zone_query = sql.SQL(SWE_QUERY).format(
        sql.SQL(",").join(map(sql.Literal, zone_ids)), date
    )

    with SWE_DB.query(zone_query) as results:
        swe = pd.DataFrame(
            results.fetchall(),
            columns=DATA_COLUMNS,
        )
    swe[ZONE_NAME] = swe[ZONE_NAME].astype("string")

    return swe


def snow_17_swe_for_zone(zone_id: str, date: str):
    df = SNOW17_DB.for_zone_forecasted(zone_id, from_year=date[0:4])
    df.rename(columns={"SWE (mm)": "Snow-17"}, inplace=True)
    df[ZONE_NAME] = df[ZONE_NAME].astype("string")
    # Need to reset index to be able to merge on Date and Zone Name
    df = df.reset_index()
    df["Date"] = df["Date"].dt.tz_localize("UTC")
    return df
