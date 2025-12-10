#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import xarray as xr

from psycopg import sql

from nb_paths import HOST_IP, MODEL_DOMAINS, BASIN_DIR, SWE_DB, SNOW17_DB

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

START_DATE = "2020-10-01"
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
DATASETS = ["Snow-17", "iSnobal", "SNODAS", "UArizona", "CU Boulder", "ASO"]
COLORS = {
    'UF': 'steelblue',
    'MF': 'goldenrod',
    'LF': 'darkorchid',
    'OF': 'seagreen',
}


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
        columns=['ID', 'CH5ID', 'Segment', 'Zone Name', 'Description']
    ).set_index('ID')


def swe_for_zone(zone_ids: list = []):
    zone_query = sql.SQL(SWE_QUERY).format(
        sql.SQL(",").join(map(sql.Literal, zone_ids)), START_DATE
    )

    with SWE_DB.query(zone_query) as results:
        swe = pd.DataFrame(
            results.fetchall(),
            columns=[
                "Date",
                "Zone Name",
                "iSnobal",
                "SNODAS",
                "UArizona",
                "CU Boulder",
                "ASO",
                "ID",
            ],
        )
    swe["Zone Name"] = swe["Zone Name"].astype("string")

    return swe


def snow_17_swe_for_zone(zone_id):
    df = SNOW17_DB.for_zone_forecasted(zone_id, from_year=START_DATE[0:4])
    df.rename(columns={"SWE (mm)": "Snow-17"}, inplace=True)
    df["Zone Name"] = df["Zone Name"].astype("string")
    # Need to reset index to be able to merge on Date and Zone Name
    df = df.reset_index()
    df["Date"] = df["Date"].dt.tz_localize("UTC")
    return df


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

app.layout = dbc.Container(
    [
        dbc.Row([html.H3("SWE by zones")]),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.P("Select zone"),
                        dcc.Dropdown(
                            id="segment-dropdown",
                            options=basin_options,
                            clearable=False,
                        ),
                    ],
                    width=5,
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Loading(
                            id="loading-animation",
                            type="circle",
                            children=[
                                dcc.Graph(
                                    id="swe-figure",
                                    config={"responsive": True},
                                )
                            ],
                        ),
                    ]
                ),
            ]
        ),
    ],
    fluid=True,
)

def add_scatter_line(df_group: pd.DataFrame, product: str, zone_index: str):
    style_opts = {}
    if product == "iSnobal":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "8px 3px",
            },
        }
    elif product == "SNODAS":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "16px 3px",
            },
        }
    elif product == "UArizona":
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "dash": "24px 3px",
            },
        }
    elif product == "CU Boulder":
        style_opts = {
            "mode": "markers",
            "marker": {
                "color": COLORS[zone_index],
                "symbol": "triangle-up",
                "size": 10,
            },
        }
    elif product == "ASO":
        style_opts = {
            "mode": "markers",
            "marker": {
                "color": COLORS[zone_index],
                "symbol": "circle",
                "size": 10,
            },
        }
    else:  # Snow-17
        style_opts = {
            "mode": "lines",
            "line": {
                "color": COLORS[zone_index],
                "width": 3,
            },
        }

    return go.Scatter(
        x=df_group.index.tolist(),
        y=df_group[product],
        name=f"{product} {zone_index}",
        **style_opts,
    )


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
            height=700,
        ),
    )

    zone_ids = zones[zones["Segment"] == value].index.values
    segment = value[0:6]

    df = pd.merge(
        snow_17_swe_for_zone(segment),
        swe_for_zone(zone_ids),
        on=["Date", "Zone Name"],
        how="inner",
    ).set_index("Date")

    for name, df_group in df.groupby("Zone Name"):
        zone_index = name[6:8]
        for dataset in DATASETS:
            figure.add_trace(add_scatter_line(df_group, dataset, zone_index))
    figure.update_traces(visible=True)
    figure.update_layout(template="plotly_white")

    return figure


if __name__ == '__main__':
    app.run(host=HOST_IP)
