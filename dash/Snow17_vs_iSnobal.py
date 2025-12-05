#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import xarray as xr

from psycopg import sql

from nb_paths import HOST_IP, BASE_DIR, ZONE_DB, SNOW17_DB

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

BASIN_DIR = BASE_DIR + "basinSetup"
SNOBAL_DIR = BASE_DIR + "isnobal"

ZONE_QUERY = (
    "SELECT cz.gid, cc.ch5_id, cz.segment, cz.zone, cc.description "
    "FROM cbrfc_zones cz LEFT JOIN cbrfc_ch5id cc ON cz.ch5_id = cc.id "
    "WHERE cz.gid in ({})"
)
ISNOBAL_SWE_QUERY = (
    "SELECT izs.value, izs.datetime::date, cz.zone "
    "FROM isnobal_zonal_swe izs LEFT JOIN cbrfc_zones cz "
    "ON izs.cbrfc_zone_id = cz.gid "
    "WHERE cbrfc_zone_id in ({}) AND datetime >= {} AND "
    "EXTRACT(HOUR FROM izs.datetime) = 00"
)

COLORS = {
    'UF': 'steelblue',
    'MF': 'goldenrod',
    'LF': 'darkorchid',
    'OF': 'seagreen',
}


zone_ids = []

for domain in ['erw_ext', 'wg_blue']:
    erw_topo = xr.open_dataset(BASIN_DIR + f'/{domain}_topo.nc')
    zone_ids = np.append(zone_ids, np.unique(erw_topo.cbrfc_zone.values))


zone_query = sql.SQL(ZONE_QUERY).format(
    sql.SQL(",").join(map(sql.Literal, zone_ids))
)

with ZONE_DB.query(ZONE_QUERY) as results:
    zones = pd.DataFrame(
        results.fetchall(),
        columns=['ID', 'CH5ID', 'Segment', 'Zone Name', 'Description']
    ).set_index('ID')


def isnobal_swe_for_zone(zone_ids: []):
    zone_query = sql.SQL(ISNOBAL_SWE_QUERY).format(
        sql.SQL(",").join(map(sql.Literal, zone_ids)), "2021-10-01"
    )

    with ZONE_DB.query(ZONE_QUERY) as results:
        isnobal_swe = pd.DataFrame(
            results.fetchall(),
            columns=["iSnobal SWE", "Date", "Zone Name"],
        )
    isnobal_swe["Date"] = pd.to_datetime(isnobal_swe["Date"])
    isnobal_swe["Zone Name"] = isnobal_swe["Zone Name"].astype("string")

    return isnobal_swe


def snow_17_swe_for_zone(zone_id):
    df = SNOW17_DB.for_zone_forecasted(zone_id, from_year=2021)
    df.rename(columns={"SWE (mm)": "Snow-17 SWE"}, inplace=True)
    df["Zone Name"] = df["Zone Name"].astype("string")
    # Need to reset index to be able to merge on Date and Zone Name
    return df.reset_index()


# Dash App
# --------

basin_values = [name for name in zones["Segment"].unique()]
basin_options = [
    {
        "label": f"{name[0:4]} - {zones[zones['Segment'] == name].iloc[0]['Description']}",
        "value": name,
    }
    for name in basin_values
]

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.ZEPHYR]
)
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        html.H3('SWE by zones')
    ]),
    dbc.Row([
        dbc.Col([
            html.P('Select zone'),
            dcc.Dropdown(
                id='segment-dropdown',
                options=basin_options,
                clearable=False,
                ),
            ], width=5
        ),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='swe-figure')
        ])
    ])
])

@app.callback(
    Output("swe-figure", "figure"), Input("segment-dropdown", "value")
)
def update_output(value):
    if value is None:
        return

    figure = go.Figure(
        layout=go.Layout(
            title=dict(text="Zonal SWE"),
            xaxis=dict(title="Date"),
            yaxis=dict(title="SWE (mm)"),
            height=600,
            width=1400,
        )
    )

    zone_ids = zones[zones["Segment"] == value].index.values
    segment = value[0:6]

    df = pd.merge(
        snow_17_swe_for_zone(segment),
        isnobal_swe_for_zone(zone_ids),
        on=["Date", "Zone Name"],
        how="inner",
    ).set_index("Date")

    for name, df_group in df.groupby("Zone Name"):
        zone_index = name[6:8]
        figure.add_trace(
            go.Scatter(
                x=df_group.index.tolist(),
                y=df_group["iSnobal SWE"],
                name=f"iSnobal {zone_index}",
                mode="lines",
                line=dict(
                    color=colors[zone_index],
                    dash="8px 3px",
                ),
                visible=False,
            )
        )
        figure.add_trace(
            go.Scatter(
                x=df_group.index.tolist(),
                y=df_group["Snow-17 SWE"],
                name=f"Snow-17 {zone_index}",
                mode="lines",
                line=dict(color=colors[zone_index]),
                visible=False,
            )
        )
    figure.update_traces(visible=True)
    figure.update_layout(template="plotly_white")

    return figure


if __name__ == '__main__':
    app.run(host=HOST_IP)
