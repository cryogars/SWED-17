#!/usr/bin/env python
# coding: utf-8

import pandas as pd

from nb_paths import HOST_IP
from data_load import available_zones, swe_for_zone, snow_17_swe_for_zone
from timeline_plot import add_scatter_line

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

START_DATE = "2020-10-01"
DATASETS = ["Snow-17", "iSnobal", "SNODAS", "UArizona", "CU Boulder", "ASO"]

# Dash App
# --------
zones = available_zones()
basin_values = [name for name in zones["Segment"].unique()]
basin_options = [
    {
        "label": f"{name[0:4]} - {zones[zones['Segment'] == name].iloc[0]['Description']}",
        "value": name,
    }
    for name in basin_values
]

app = Dash(__name__, external_stylesheets=[dbc.themes.ZEPHYR])
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
            yaxis=dict(title="SWE (in)"),
            height=700,
        ),
    )

    zone_ids = zones[zones["Segment"] == value].index.values
    segment = value[0:6]

    df = pd.merge(
        snow_17_swe_for_zone(segment, START_DATE),
        swe_for_zone(zone_ids, START_DATE),
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
