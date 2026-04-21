import pandas as pd

from pandas.api.typing import DataFrameGroupBy
from psycopg import sql

from nb_paths import SWE_DB, SNOW17_DB
from config import START_DATE

ZONE_QUERY = """
SELECT gid, fgid, segment, zone, description from cbrfc_zones_in_isnobal;
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
    with SWE_DB.query(ZONE_QUERY) as results:
        zones = pd.DataFrame(
            results.fetchall(),
            columns=["ID", "CH5ID", "Segment", ZONE_NAME, "Description"],
        ).set_index("ID")

    return zones


def swe_for_zone(zone_ids: list, date: str):
    query = sql.SQL(SWE_QUERY).format(
        sql.SQL(",").join(map(sql.Literal, zone_ids)), date
    )

    with SWE_DB.query(query) as results:
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
    return df.dropna(subset=["Snow-17"])


def load_and_group(value: str, zones: pd.DataFrame) -> DataFrameGroupBy:
    zone_ids = zones[zones["Segment"] == value].index.values
    segment = value[0:6]

    df = pd.merge(
        snow_17_swe_for_zone(segment, START_DATE),
        swe_for_zone(zone_ids, START_DATE),
        on=["Date", "Zone Name"],
        how="inner",
    ).set_index("Date")

    return df.groupby("Zone Name")
