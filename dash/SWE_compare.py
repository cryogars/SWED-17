#!/usr/bin/env python
# coding: utf-8

import sys

from nb_paths import HOST_IP
from config import DATASETS
from data_load import available_zones, load_and_group
from timeline_plot import add_scatter_line
from data_statistics import generate_statistics, plot_year

import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

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
                        html.H3("Timeline", className="mt-4"),
                        html.Div(
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
                        ),
                    ]
                ),
            ]
        ),
        dbc.Row(
            dbc.Col(
                [
                    html.H3("Yearly Statistics", className="mt-4"),
                    dbc.Spinner(
                        html.Div(id="swe-stats"),
                        color="success",
                    ),
                ]
            )
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("swe-figure", "figure"), Input("segment-dropdown", "value")
)
def update_timeline(value):
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

    for name, df_group in load_and_group(value, zones):
        for dataset in DATASETS:
            figure.add_trace(add_scatter_line(df_group, dataset, name[6:8]))

    figure.update_traces(visible=True)
    figure.update_layout(template="plotly_white")

    return figure

@app.callback(
    Output("swe-stats", "children"), [Input("segment-dropdown", "value")]
)
def update_stats(value):
    children = []
    year_stats = {}

    if value is None:
        return children

    for name, df_group in load_and_group(value, zones):
        year_stats[name] = generate_statistics(df_group)

    for zone_name, all_years in year_stats.items():
        accordion_years = []
        for year, data in all_years.items():
            accordion_years.append(
                dbc.AccordionItem(
                    dcc.Graph(figure=plot_year(data)),
                    title=year,
                )
            )

        children.append(
            dbc.Row(
                dbc.Col(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            dbc.Accordion(
                                accordion_years,
                                start_collapsed=True,
                            ),
                            title=zone_name,
                        ),
                        start_collapsed=True,
                    )
                ),
                className="mt-4",
            )
        )

    return children


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        app.run(
            host="0.0.0.0", debug=True, use_reloader=True, dev_tools_ui=True
        )
    else:
        app.run(host=HOST_IP)
