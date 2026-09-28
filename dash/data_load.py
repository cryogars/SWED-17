import functools

import pandas as pd
from config import DATASETS, START_DATE
from nb_paths import SNOW17_DB, SWE_DB
from pandas.api.typing import DataFrameGroupBy
from psycopg import sql

ZONE_QUERY = """
SELECT gid, fgid, segment, zone, description from cbrfc_zones_in_isnobal order by zone ASC;
"""
# Query to load SWE data for the configured products.
# NOTE: Update the query columns when new products are added
SWE_QUERY = """
SELECT date, isnobal_swe, snodas_swe, ua_swe, cu_boulder_swe, aso_swe, zone_name
 FROM public.zonal_swe
 WHERE
    cbrfc_zone_id in ({}) AND
    date >= to_date({}, 'YYYY-MM-DD')
"""
# Human readable names for query columns of SWE_QUERY
ZONE_NAME = "Zone Name"
SWE_COLUMNS = ["Date"] + DATASETS[1:] + [ZONE_NAME]


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
            columns=SWE_COLUMNS,
        )

    return swe


def snow_17_swe_for_zone(zone_id: str, date: str):
    df = SNOW17_DB.for_zone_forecasted(zone_id, from_year=date[0:4])
    df.rename(columns={"SWE (mm)": "Snow-17"}, inplace=True)
    df[ZONE_NAME] = df[ZONE_NAME].astype("string")
    # Can't filter in the Snow-17 DB by full date.
    df = df[df.index >= START_DATE]
    # Need to reset index to be able to merge on Date and Zone Name
    df = df.reset_index()
    df["Date"] = df["Date"].dt.tz_localize("UTC")
    return df.dropna(subset=["Snow-17"])


def load_and_group(value: str) -> DataFrameGroupBy:
    zones = available_zones()
    zone_ids = zones[zones["Segment"] == value].index.values
    segment = value[0:6]

    df = pd.merge(
        snow_17_swe_for_zone(segment, START_DATE),
        swe_for_zone(zone_ids, START_DATE),
        on=["Date", "Zone Name"],
        how="left",
    ).set_index("Date")

    return df.groupby("Zone Name")
